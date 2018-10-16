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
        self.conn = conn # immutable
        self.hashSize = int(256 / 8) # immutable
        self.sessionKey = None # should not change after initial setKey is called
        self.blockSize = int(128 / 8) # immutable
        
    def send(self, data):
        header = Header(self.blockSize)
        if isinstance(data, str):
            data = data.encode()
        
        header.setSize(len(data))
        msg = header.getBytes() + data

        logger.debug("msg before padding: {}, len: {}".format(msg, len(msg)))
        if not self.sessionKey:
            self.conn.send(msg)
            return

        (data, paddingSize) = self._applyPadding(header, data)
        logger.debug("data after padding: " + str(data))
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
      header: the header of the packet
      msg: bytes
    Post-Condition:
      returns the padded msg and the padding size as a tuple
    """
    def _applyPadding(self, header, msg):
        totalLen = len(msg) + header.getHeaderSize()
        leftover = totalLen % self.blockSize
        if leftover != 0:
            paddingSize = self.blockSize - leftover
            msg += (paddingSize * "0").encode()
        else:
            paddingSize = 0
        return (msg, paddingSize)

    """
    Post-Condition:
      returns tuple containing headerBytes and state, state is None
      if header is fully extracted
    """
    def _recvHeaderBytes(self, state=None, generator=None):        
        headerBytes = b''
        Normal = 0
        FirstNL = 1
        FirstCR = 2
        SecondNL = 3
        SecondCR = 4
        if not state:
            state = Normal
        while True:
            if not generator:
                char = self.conn.recv(1)
            else:
                try:
                    char = next(generator)
                except StopIteration:
                    break
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
                state = None
                break
        return (headerBytes, state)

    def _recvBytes(self, size):
        block = b''
        while len(block) < size:
            block += self.conn.recv(size - len(block))
        return block

    def _blkGenerator(self, blk):
        for b in blk:
            yield bytes([b & 0xff])
    
    """
    Receives the next protocol packet, this function blocks till a packet is received.
    Params:
      asBytes: if true return result as bytes, string otherwise.
    """
    def recv(self, asBytes=False):
        if self.sessionKey:
            iv = self._recvBytes(self.blockSize)
            logger.debug("iv: {}".format(iv))
            cipher = Cipher(algorithms.AES(self.sessionKey), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            ct = b''
            blk = self._recvBytes(self.blockSize)
            ct += blk
            dblk = decryptor.update(blk)
            gen = self._blkGenerator(dblk)            
            headerBytes, state = self._recvHeaderBytes(generator=gen)
            logger.debug("state: {}".format(state))
            while state != None:
                blk = self._recvBytes(self.blockSize)
                ct += blk
                dblk = decryptor.update(blk)
                gen = self._blkGenerator(dblk)
                temp, state = self._recvHeaderBytes(generator=gen)
                headerBytes += temp

            logger.debug("HeaderBytes: {}".format(headerBytes))
            header = Header(self.blockSize)
            header.update(headerBytes)
            body = b''
            try:
                while True:
                    body += next(gen)
            except StopIteration:
                pass

            leftoverBodySize = header.getSize() - len(body) + header.getPaddingSize()
            leftoverBodyEncrypted = self._recvBytes(leftoverBodySize)
            ct += leftoverBodyEncrypted
            body += decryptor.update(leftoverBodyEncrypted) + decryptor.finalize()
            
            checkHmac = self._recvBytes(self.hashSize)
            h = hmac.HMAC(self.sessionKey, hashes.SHA256(), backend=default_backend())
            h.update(ct)
            h.verify(checkHmac)

            body = body[:len(body) - header.getPaddingSize()]
            if not asBytes:
                body = body.decode()
            return body                  
        else:
            header = Header()
            (headerBytes, _) = self._recvHeaderBytes()
            header.update(headerBytes)
            body = b''
            
            totalSize = header.getSize()
            while len(body) < totalSize:
                body += self.conn.recv(int(totalSize - len(body)))
            
            if not asBytes:
                return body.decode()
            return body

    def close(self):
        self.conn.close()

    """
    Sets the session key for this connection
    """
    def setKey(self, key):
        self.sessionKey = key

    def getKey(self):
        return self.sessionKey
            
class Header(object):
    cr = "\n\r"
    hSize = "size";
    hPaddingSize = "paddingSize"

    def __init__(self, blockSize=None):
        self.size = 0
        self.paddingSize = 0
        self.completed = False
        if blockSize:
            self.numPaddingDigits = len(str(blockSize))
        else:
            self.numPaddingDigits = 1

    """
    Get the number of bytes that header takes up in packet
    """
    def getHeaderSize(self):
        return len(self.getBytes())
        
    def setSize(self, size):
        self.size = size

    """
    Get the payload size of this header
    """
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
        padding = str(self.paddingSize)
        paddingStr = str(self.paddingSize)
        diff = self.numPaddingDigits - len(paddingStr)
        if diff > 0:
            paddingStr += diff * " "
        header += "{}:{}{}".format(Header.hPaddingSize, paddingStr, Header.cr)
        header += Header.cr
        return header.encode()

    """
    Update the values in the header based on bytes received
    Params:
      buf: the header bytes received
    """
    def update(self, buf):
        headerStr = buf[:-len(Header.cr)].decode()
        headerStrMapArr = headerStr.split(Header.cr)
        self.size = int(headerStrMapArr[0].split(":")[1])
        self.paddingSize = int(headerStrMapArr[1].split(":")[1].strip())
