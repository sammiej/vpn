import socket
import logging
import _thread

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
            while True:
                conn, addr = s.accept()
                logging.info("Connected with {} : {}".format(addr[0], addr[1]))
                _thread.start_new_thread(self.startClientThread, (conn,))
        except:
            s.close()

    def startlientThread(self, conn):
        # TODO: change this
        conn.send("Hi")

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
    def execute(self):
        pass
        
