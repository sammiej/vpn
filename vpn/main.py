import key
import logging
import socket
import command as cmd
#import ui

def serverTest():
    s = cmd.ServerListenCommand()
    s.execute()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    serverTest()
    #ui.run()
    while True:
        pass
