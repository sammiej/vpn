import socket
import logging
import _thread
from connection import ConnectionWrapper

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
        s = socket.socket()
        logging.info("Server socket created")
        try:
            s.bind((self.host, self.port))
        except socket.error as msg:
            logging.error("Server socket bind failed")
            s.close()
            return
        logging.info("Server socket bind complete")

        s.listen(NUM_CLIENTS)

        try:            
            conn, addr = s.accept()
            logging.info("Connected with {} : {}".format(addr[0], addr[1]))
            self.handleClientThread(conn)
        except:
            s.close()

    def handleClientThread(self, conn):
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
                conn.send("received")
        finally:
            conn.close()
        

class ClientConnectCommand(Command):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.kex = KeyExchanger()
        self.auth = Authenticator()
        
    def execute(self):
        c = socket.socket()
        logging.info("Client socket created")
        try:
            c.connect((self.host, self.port))
            logging.info("Client connected")
            conn = ConnectionWrapper(c)
            self.kex.exchangeKey(conn)
            self.auth.authenticate()
            while True:
                # TODO: talk to server here
                pass
        finally:
            c.close()
        
        
        
