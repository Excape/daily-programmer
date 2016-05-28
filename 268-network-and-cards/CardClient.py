import socket
import threading
from time import sleep

class CardClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
    
    def send(self, message):
        print 'sending %s' % message
        self.sock.sendall(message)
        
    def listen(self):
        size = 1024
        while True:
            data = self.sock.recv(size)
            if not data: break
            if data.startswith('HEARTBEAT'):
                self.echoheartbeat(data[10:])
            else:
                print 'Received: %s' % data
    
    def echoheartbeat(self, response):
        self.send('HBRESPONSE %s' % response)

if __name__ == "__main__":
    myClient = CardClient('localhost', 12915)
    threading.Thread(target = myClient.listen).start()
    while True:
        message = input("Message: ")
        myClient.send(message)
        sleep(1)
# try:
#    message = 'This is a message'
#   print 'sending %s' % message
#   sock.sendall(message)
    
#   data = sock.recv(4096)
#   print 'received %s' % data
#finally:
#    sock.shutdown(socket.SHUT_RDWR)
#    sock.close()
#   exit
