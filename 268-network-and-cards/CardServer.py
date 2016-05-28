"""A simple multiplayer black jack server over TCP"""
import socket
import threading
import random
import Queue
import signal
import sys
from time import sleep

PACKET_SIZE = 1024

CARD_VALUES = {
    'two' : 2,
    'three' : 3,
    'four' : 4,
    'five' : 5,
    'six' : 6,
    'seven' : 7,
    'eight' : 8,
    'nine' : 9,
    'jack' : 10,
    'queen' : 10,
    'king' : 10,
    'ace' : 11 #or 1
}
    
CARD_SUITS = {
    'hearts' : 0,
    'clubs' : 1,
    'spades' : 2,
    'diamonds' : 3
}
class CardServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port 
        self.clients = {}
        self.card_deck = self.make_card_deck()
        self.has_started = False
        self.player_queue = Queue.Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        signal.signal(signal.SIGINT, self.shutdown)
        print "Server started at %s on port %s" % (self.host, self.port)
        
    def start_game(self):
        print 'Participating clients:'
        print self.clients
        self.has_started = True
        self.broadcast("Game begins now!")
        sleep(1)
        
        for client in self.clients:
            self.player_queue.put(client)
            
        while not self.player_queue.empty():
            cur_player = self.player_queue.get()
            self.broadcast('It\'s %s\'s turn!' % self.clients[cur_player]['name'])
            sleep(1)
            self.deal_card(cur_player)
        
        self.determine_winner()
        #TODO: Error on exit
        self.shutdown(signal.SIGINT, None)
        
    def deal_card(self, client):
        client_entry = self.clients[client]
        client.send('Its your turn - TAKE or PASS. Your current cards have a value of %s' % client_entry['cur_value'])
        
        # Wait for answer
        client_entry['waiting'] = True
        while client_entry['waiting']:
            sleep(1) 
            
        if not client_entry['has_passed']:
            suit = random.choice(list(CARD_SUITS))
            value = random.choice(list(CARD_VALUES))
            card = suit.upper() + ' ' + value.upper()
            card, value = random.choice(self.card_deck)
            self.card_deck.remove((card, value))
            print '%s draws %s' % (client_entry['name'], card)
            self.broadcast('%s draws %s' % (client_entry['name'], card))
            sleep(1)
            client.send("Your Card: %s" % card)
            sleep(1)
            client_entry['drawn_cards'].append(card)
            client_entry['cur_value'] += value
            client.send('Cards in your hand: %s' % ', '.join(client_entry['drawn_cards']))
            sleep(1)
            if not self.check_draw_result(client):
                self.broadcast('%s is over 21! Game Over!' % client_entry['name'])
            else:
                client.send('Your current value is %s' % client_entry['cur_value'])
                self.player_queue.put(client)
        else:
            self.broadcast('%s has passed!' % client_entry['name'])
        sleep(1)
        
    def determine_winner(self):
        candidates = []
        for client in self.clients.values():    
            if client['has_passed']:
                candidates.append((client, client['cur_value']))
        if not candidates:
            self.broadcast('Nobody has won!')
            return
        sorted_candidates = sorted(candidates, key=lambda c: c[1], reverse=True)
        if len(sorted_candidates) > 1 and sorted_candidates[0][1] == sorted_candidates[1][1]:
            self.broadcast('We have a tie!')
        else:
            winner = sorted_candidates[0]
            print '%s has won!' % winner[0]['name']
            self.broadcast('Player %s has won with %s!' % (winner[0]['name'], ', '.join(winner[0]['drawn_cards'])))
        
    def check_draw_result(self, client):
        client_entry = self.clients[client]
        if client_entry['cur_value'] <= 21: return True
        for card in client_entry['drawn_cards']:
            if 'ace' in card:
                client_entry['cur_value'] -= 10
                if client_entry['cur_value'] <= 21:
                    return True 
        return False
        
    def make_card_deck(self):
        card_deck = []
        for suit in CARD_SUITS:    
            for value in CARD_VALUES:
                card_deck.append(('%s of %s' % (value, suit), CARD_VALUES[value]))
        return card_deck           
        
    def listen(self):
        """Start listening on the socket and start a thread for every connection"""
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(300)
            print 'client %s connected on port %s' % address
            threading.Thread(target=self.listen_to_client, args=(client, address)).start()
            
        
    def listen_to_client(self, client, address):
        """Runs in a thread for a given client"""
        while True:
            try:
                data = client.recv(PACKET_SIZE)
                if data:
                    self.handle_client_response(client, data)
                else:
                    raise Exception('Disconnected')
            except Exception as ex:
                print '%s - %s' % (address[0], ex)
                if client in self.clients:
                    del self.clients[client]
                client.close()
                return False
                
    def handle_client_response(self, client, data):
        print 'received "%s" from %s' % (data, client)
            
        if self.has_started:
            if client not in self.clients:
                client.send('Game has already started - sorry!')
                return
            client_entry = self.clients[client]
            if not client_entry['waiting']:
                client.send('Please wait for your turn')
                return
            if data.startswith('TAKE'):
                client_entry['waiting'] = False
            elif data.startswith('PASS'):
                client_entry['has_passed'] = True
                client_entry['waiting'] = False
            else:
                client.send('Please type TAKE or PASS')
        else:
            if not client in self.clients:
                self.identify_client(client, data)
            else:
                if data.startswith('START'):
                    self.clients[client]['isReady'] = True
                    if self.all_clients_ready():
                        print self.clients
                        threading.Thread(target=self.start_game).start()
                    else:
                        client.send('Waiting for other clients to get ready...')
                else:
                    client.send('Send "START" to start the game')
                        
    def broadcast(self, message):
        for client in self.clients:
            client.send(message)
    
    def identify_client(self, client, data):
        if data.startswith('IDENTIFY'):
            name = data[9:]
            #TODO: check if name already exists
            self.clients[client] = {
                'name': name,
                'isReady': False,
                'cur_value': 0,
                'drawn_cards': [],
                'waiting': False,
                'has_passed': False}
            client.send('Identified as %s' % name)
            return True
        else:
            client.send('Please identify yourself with "IDENTIFY <name>"')
            return False
            
    def all_clients_ready(self):
        # TODO: Doesn't always work correctly
        for client in self.clients.values():
            if not client['isReady']:
                return False
            return True
        
    def shutdown(self, signal, frame):
        print 'Shutting down...'
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        sys.exit(0)
        
if __name__ == "__main__":
    my_server = CardServer('localhost', 12916)
    my_server.listen()
