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
