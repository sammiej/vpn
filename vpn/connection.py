
"""
Decorator a connection object
"""
class ConnectionWrapper(object):
    def __init__(self, conn):
        self.conn = conn
        self.key = None

    def send(self, data):
        if not self.key:
            return self.conn.send(data)
        raise NotImplementedError("Not implemented!")

    def recv(self, size=1024):
        if not self.key:
            return self.conn.recv(size)
        raise NotImplementedError("Not implemented!")
    
    def setKey(self, key):
        self.key = key
