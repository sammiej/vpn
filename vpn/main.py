import key
from logging import DEBUG, INFO
from logger import logger
import socket
import command as cmd
import ui

if __name__ == "__main__":
    logger.basicConfig(level=DEBUG)
    
    ui.run()
    while True:
        pass
