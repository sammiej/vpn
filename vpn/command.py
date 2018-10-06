import socket
import logging
from threading import Thread
from connection import ConnectionWrapper, Q, Message
from key import KeyExchanger
from auth import Authenticator
from queue import Empty

NUM_CLIENTS = 1

"""
Command interface
"""
class Command(object):
    """
    executes the command
    """
    def execute(self):
        raise NotImplementedError("Not Implemented!")

class ServerListenCommand(Command):
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 8888
        self.kex = KeyExchanger()
        self.auth = Authenticator()

    def execute(self):    
        self.sock = socket.socket()
        logging.info("Server socket created")
        try:
            self.sock.bind((self.host, self.port))
            logging.info("Server listening on port: {}".format(self.port))
        except socket.error as msg:
            logging.error("Server socket bind failed")
            self.sock.close()
            return
        logging.info("Server socket bind complete")
        t = Thread(target=self.listenThread)
        t.start()

    def listenThread(self):
        logging.info("Listening for connection on separate thread")
        self.sock.listen(NUM_CLIENTS)

        try:
            while True:            
                conn, addr = self.sock.accept()
                logging.info("Connected with {} : {}".format(addr[0], addr[1]))
                self.handleClient(conn)
        except:
            logging.info("Connection to client closed unexpectedly")
            self.sock.close()

    def handleClient(self, conn):
        # TODO: change this
        conn = ConnectionWrapper(conn)
        self.kex.exchangeKey(conn)
        self.auth.authenticate()
        # TODO: start talking here
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("obtained {}".format(data))
                conn.send("received".encode())
        finally:
            logging.info("Connection to client closed")
            conn.close()
        

class ClientConnectCommand(Command):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.kex = KeyExchanger()
        self.auth = Authenticator()
        
    def execute(self):
        self.sock = socket.socket()
        logging.info("Client socket created")
        t = Thread(target=self.connectThread)
        t.start()

    def connectThread(self):
        conn = None
        try:
            self.sock.connect((self.host, self.port))
            logging.info("Client connected")
            conn = ConnectionWrapper(self.sock)
            # use connection from now on to talk
            self.kex.exchangeKey(conn)
            self.auth.authenticate()
            # From here on only use conn to send and recv messages
            self.sock.settimeout(0.2)                                
            while True:
                try:
                    msg = Q.get(timeout=0.2)
                    if msg is None:
                        break
                    if msg.mtype == Message.SEND:
                        conn.send(msg.bytes)
                    Q.task_done()
                except Empty:
                    pass
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print("data: {}".format(data))
                except socket.timeout:
                    pass
                # TODO: talk to server here
        finally:
            logging.info("Connection to server closed")
            if conn:
                conn.close()        
        
        
