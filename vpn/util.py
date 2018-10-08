from queue import Queue

MQ = Queue() # queue for talking to main thread
Q = Queue() # queue for talking to network thread

"""
Message that is placed on the queue to be consumed by network threads
"""
class Message(object):
    SEND = 0 # send message over network
    def __init__(self, mtype, text):
        self.mtype = mtype
        self.bytes = text.encode()

"""
Message that is placed on the main queue to be consumed by the main thread
"""
class UMessage(object):
    DISPLAY = 0 # display message in shared secret slot? testing
    def __init__(self, mtype, text):
        self.mtype = mtype
        self.text = text
    
