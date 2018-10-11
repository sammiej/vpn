import logging
from tkinter import END
from util import UMessage, MQ
from queue import Full
import datetime

screen = None
logger = logging

def log_decorator(log):
    def wrapper(*args, **kwargs):
        try:
            # Can't touch the ui directly because this
            # might be called on other thread
            text = "{}---{}\n".format(datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S"), args[0])
            umsg = UMessage(UMessage.DISPLAY, text)
            MQ.put_nowait(umsg)
            log(*args, **kwargs)
        except Full:
            logger.error("Main queue is full!")
        except:
            pass
    return wrapper

logger.info = log_decorator(logger.info)
