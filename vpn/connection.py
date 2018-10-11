from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from logger import logger
"""
Decorator a connection object
"""
class ConnectionWrapper(object):
    def __init__(self, conn):
        self.conn = conn
        self.hashSize = 256 / 8
        self.sessionKey = None
        #self.sessionkey = b'j\xefp\x8a=z/\x11"\x11+\x9dwj\x08*\xf3\xb6\x1b \x9f\xab\x11Y\x1c\xe3&\x9b\x0f\x8dG\t' # test value
        self.blockSize = 128 / 8
        
    def send(self, data):
        header = Header()
        if isinstance(data, str):
            data = data.encode()
        
        header.setSize(len(data))
        msg = header.getBytes() + data

        logger.debug("msg: " + str(msg))
        if not self.sessionKey:
            self.conn.send(msg)
            return

        (data, paddingSize) = self.applyPadding(data)
        header.setPaddingSize(paddingSize)
        msg = header.getBytes() + data
        iv = os.urandom(self.blockSize)
        cipher = Cipher(algorithms.AES(self.sessionKey), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(msg) + encryptor.finalize()
        
        h = hmac.HMAC(self.sessionKey, hashes.SHA256(), backend=default_backend())
        h.update(ct)
        mac = h.finalize()

        self.conn.send(iv + ct + mac)

    """
    Apply insecure padding of all zeros
    Params:
      msg: bytes
    Post-Condition:
      returns the padded msg and the padding size as a tuple
    """
    def applyPadding(msg):
        leftover = len(msg) % self.blockSize
        if leftover != 0:
            paddingSize = self.blockSize - leftover
            msg += paddingSize * "0".encode();
        else:
            paddingSize = 0
        return (msg, paddingSize)
        
    """
    Receives the next protocol packet.
    Params:
      asBytes: if true return result as bytes, string otherwise.
    """
    def recv(self, asBytes=False):
        if self.sessionKey:
            iv = "".encode()
            while len(iv) < self.blockSize:
                iv += self.conn.recv(self.blockSize - len(iv))
                
        headerBytes = b''
        Normal = 0
        FirstNL = 1
        FirstCR = 2
        SecondNL = 3
        SecondCR = 4
        state = Normal
        while True:
            char = self.conn.recv(1)
            headerBytes += char
            if char == b'\n':
                if state == Normal:
                    state = FirstNL
                elif state == FirstCR:
                    state = SecondNL
            elif char == b'\r':
                if state == FirstNL:
                    state = FirstCR
                elif state == SecondNL:
                    state = SecondCR
            else:
                if state == FirstCR:
                    state = Normal
            if state == SecondCR:
                break

        header = Header()
        body = header.update(headerBytes)
            
        if not body:
            body = b''
            
        totalSize = header.getSize()
        if self.sessionKey:
            totalSize = header.getPaddingSize() + self.hashSize
        while len(body) < totalSize:
            body += self.conn.recv(int(totalSize - len(body)))
            
        if not self.sessionKey:
            if not asBytes:
                return body.decode()
            return body
            
        checkHmac = body[-self.hashSize:]
        ct = body[:len(body)-self.hashSize]
        h = hmac.HMAC(self.sessionKey, hashes.SHA256(), backend=default_backend())
        h.update(ct)
        h.verify(checkHmac)

        cipher = Cipher(algorithms.AES(self.sessionKey), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        msg = decryptor.update(ct) + decryptor.finalize()
        msg = msg[:len(msg) - header.getPaddingSize()]
        
        if not asBytes:
            msg = body.decode()
        return msg

    def close(self):
        self.conn.close()

    """
    Sets the session key for this connection
    """
    def setKey(self, key):
        self.sessionKey = key

    def getKey(self):
        return b'j\xefp\x8a=z/\x11"\x11+\x9dwj\x08*\xf3\xb6\x1b \x9f\xab\x11Y\x1c\xe3&\x9b\x0f\x8dG\t'        
        #return self.sessionKey

"""
Handles receiving packets
"""
class Receiver(object):
    pass
    
class Header(object):
    cr = "\n\r"
    hSize = "size";
    hPaddingSize = "paddingSize"

    def __init__(self):
        self.size = 0
        self.paddingSize = 0
        self.completed = False
    
    def setSize(self, size):
        self.size = size

    def getSize(self):
        return self.size

    def setPaddingSize(self, pSize):
        self.paddingSize = pSize

    def getPaddingSize(self):
        return self.paddingSize
    
    """
    Returns the encoded header
    """
    def getBytes(self):
        header = "{}:{}{}".format(Header.hSize, self.size, Header.cr)
        header += "{}:{}{}".format(Header.hPaddingSize, self.paddingSize, Header.cr)
        header += Header.cr
        return header.encode()

    """
    Update the values in the header based on bytes received
    Params:
      buf: the header bytes received
    """
    def update(self, buf):
        headerStr = buf[:-len(Header.cr)].decode()
        self._extractHeaderValues(headerStr)

    def _extractHeaderValues(self, headerStr):
        headerStrMapArr = headerStr.split(Header.cr)
        self.size = int(headerStrMapArr[0].split(":")[1])
        self.paddingSize = int(headerStrMapArr[1].split(":")[1])
