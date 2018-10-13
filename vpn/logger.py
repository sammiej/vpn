import logging
from tkinter import END
from util import UMessage, MQ
import datetime

screen = None
logger = logging

def log_decorator(log, prefix=""):
    def wrapper(*args, **kwargs):
        try:
            # Can't touch the ui directly because this
            # might be called on other thread
            text = "{}-[{}]-{}\n".format(datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S"), prefix, args[0])
            umsg = UMessage(UMessage.DISPLAY, text)
            MQ.put_nowait(umsg)
            log(*args, **kwargs)
        except:
            pass
    return wrapper

logger.info = log_decorator(logger.info, "INFO")
logger.error = log_decorator(logger.error, "ERROR")
