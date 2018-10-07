from queue import Queue

MQ = Queue() # queue for talking to main thread
Q = Queue() # queue for talking to network thread
"""
Decorator a connection object
"""
class ConnectionWrapper(object):
    def __init__(self, conn):
        self.conn = conn
        self.sessionkey = "ABCDE".encode("utf-8") # dummy value

    """
    Params:
      data: string or bytes object
    """
    def send(self, data):
        if isinstance(data, str):
            data = data.encode()
        if not self.sessionkey:
            return self.conn.send(data)
        # TODO: change this when key established
        return self.conn.send(data)        
        #raise NotImplementedError("Not implemented!")

    """
    Post-Condition:
      returns bytes like object
    """
    def recv(self, size=1024):
        if not self.sessionkey:
            return self.conn.recv(size)
        # TODO: change this when key established
        return self.conn.recv(size)
        #raise NotImplementedError("Not implemented!")

    def close(self):
        self.conn.close()

    """
    Sets the session key for this connection
    """
    def setKey(self, key):
        self.sessionkey = key

    def getKey(self):
        return self.sessionkey

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
    
