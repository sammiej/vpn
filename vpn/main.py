import key
import logging
import _thread
from threading import Condition
import socket
from command import ServerListenCommand, ClientConnectCommand

def serverThread():
    s = ServerListenCommand(cv)
    s.execute()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    serverThread()

    while True:
        pass
