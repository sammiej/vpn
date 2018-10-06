from queue import Queue

MQ = Queue() # queue for talking to main thread
Q = Queue() # queue for talking to network thread
"""
Decorator a connection object
"""
class ConnectionWrapper(object):
    def __init__(self, conn):
        self.conn = conn
        self.key = None

    """
    Params:
      data: string or bytes object
    """
    def send(self, data):
        if isinstance(data, str):
            data = data.encode()
        if not self.key:
            return self.conn.send(data)
        raise NotImplementedError("Not implemented!")

    """
    Post-Condition:
      returns bytes like object
    """
    def recv(self, size=1024):
        if not self.key:
            return self.conn.recv(size)
        raise NotImplementedError("Not implemented!")

    def close(self):
        self.conn.close()
    
    def setKey(self, key):
        self.key = key

"""
Message that is placed on the queue to be consumed by threads
"""
class Message(object):
    SEND = 0 # send message over network
    def __init__(self, mtype, text):
        self.mtype = mtype
        self.bytes = text.encode()
