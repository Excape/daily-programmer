import socket
import threading

SIZE = 1024

class CardServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port 
        self.clients = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        print "Server started at %s on port %s" % (self.host, self.port)
        
    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            print 'client %s connected on port %s' % address
            threading.Thread(target = self.listen_to_client, args = (client, address)).start()
            
        
    def listen_to_client(self, client, address):
        while True:
            try:
                data = client.recv(SIZE)
                if data:
                    self.handle_client_response(client, data)
                else:
                    raise Exception('Disconnected')
            except Exception as e:
                print '%s - %s' % (address[0], e)
                if (client in self.clients):
                    del self.clients[client]
                client.close()
                return False
                
    def handle_client_response(self, client, data):
        print 'received "%s" from %s' % (data, client)
        print self.clients
        if not client in self.clients:
            self.identify_client(client, data)
        else:
            client.send(data)
        
    def identify_client(self, client, data):
        if data.startswith('IDENTIFY'):
            name = data[9:]
            self.clients[client] = {'name': name, 'isReady': False}
            client.send('Identified as %s' % name)
            return True
        else:
            client.send('Please identify yourself with "IDENTIFY <name>"')
            return False
            
if __name__ == "__main__":
    CardServer('localhost', 12915).listen()
