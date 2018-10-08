import socket
from logger import logger
from threading import Thread
from connection import ConnectionWrapper
from util import Q, MQ, Message, UMessage
from key import KeyExchanger
from auth import Authenticator, AuthError
from queue import Empty, Full

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
    def __init__(self, port, sharedSecret):
        self.host = "0.0.0.0"
        self.port = port
        self.kex = KeyExchanger()
        # TODO: get shared secret from input
        self.auth = Authenticator(sharedSecret)

    def execute(self):    
        self.sock = socket.socket()
        logger.info("Server socket created")
        try:
            self.sock.bind((self.host, self.port))
            logger.info("Server listening on port: {}".format(self.port))
        except socket.error as msg:
            logger.error("Server socket bind failed")
            self.sock.close()
            return
        logger.info("Server socket bind complete")
        t = Thread(target=self.listenThread)
        t.start()

    def listenThread(self):
        logger.info("Listening for connection on separate thread")
        self.sock.listen(NUM_CLIENTS)

        try:
            while True:            
                conn, addr = self.sock.accept()
                logger.info("Connected with {} : {}".format(addr[0], addr[1]))
                self.handleClient(conn)
        except:
            logger.info("Connection to client closed unexpectedly")
            self.sock.close()

    def handleClient(self, conn):
        try:
            conn = ConnectionWrapper(conn)
            self.kex.exchangeKey(conn)
            self.auth.authenticate(conn)
            while True:
                # TODO: Change this
                data = conn.recv(1024)
                if not data:
                    break
                logger.info("obtained {}".format(data))
                conn.send("received".encode())
        except AuthError as err:
            logger.info(str(err))
        finally:
            logger.info("Connection to client closed")
            conn.close()

class ClientConnectCommand(Command):
    def __init__(self, host, port, sharedSecret):
        self.host = host
        self.port = port
        self.kex = KeyExchanger()
        self.auth = Authenticator(sharedSecret)
        
    def execute(self):
        self.sock = socket.socket()
        logger.info("Client socket created")
        t = Thread(target=self.connectThread)
        t.start()

    def connectThread(self):
        conn = None
        try:
            self.sock.connect((self.host, self.port))
            logger.info("Client connected")
            conn = ConnectionWrapper(self.sock)
            # use connection from now on to talk
            self.kex.exchangeKey(conn)
            self.auth.authenticate(conn)
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
                    logger.info("data: {}".format(data))
                except socket.timeout:
                    pass
        except AuthError as err:
            logger.info(str(err))
        finally:
            logger.info("Connection to server closed")
            if conn:
                conn.close()        
        
        
