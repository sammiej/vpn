import logging
import hashlib
import hmac
import secrets
import string
import socket
try:
    import cPickle as pickle
except ImportError:
    import pickle

"""
    Executes the mutual authentication protocol.
    """
class Authenticator(object):
    # TODO replace these with actual models or function where they're returned
    N = 7 # length of random hashToken
    sharedSecret = "12345".encode("utf-8") #dummy
    secretKey = "ABCDE".encode("utf-8") #dummy
    hashSize = 256 / 8 #(sha-256)
    authMagic = "sendreceive".encode("utf-8") # to identify auth messages sent over self.conn

    def __init__(self, sharedSecret):
        self.sharedSecret = sharedSecret
    
    def generateHashToken(self):
        return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(Authenticator.N))
    
    def authenticateSend(self):
        # Compute HMACs
        self.sendToken = self.generateHashToken().encode("utf-8")
        intermediateHash = hmac.new(key=self.sendToken, msg=self.sharedSecret, digestmod=hashlib.sha256).digest()
        computedHash = hmac.new(key=self.conn.getKey(), msg=intermediateHash, digestmod=hashlib.sha256).digest() # h(h(S,N1),K)
        
        assert len(computedHash) == Authenticator.hashSize
        logging.debug("computedHash: {}".format(computedHash))
        
        message = Authenticator.authMagic + computedHash + self.sendToken
        logging.debug("message: {}".format(message))
        # Send computed HMACs over
        try:
            self.conn.send(message)
            logging.info("Authentication hash sent")
        except socket.error:
            logging.info("self.conn connection broken on send")
            
    """
    Params:
      conn: should be an encrypted connection object
    """
    def authenticate(self, conn):
        self.conn = conn
        self.authenticateSend()

        logging.info("Trying to receive auth data")
        data = self.conn.recv(1024)
        logging.info("Auth data received!")
        logging.debug("Auth data: {}".format(data))
        if len(data) == len(Authenticator.authMagic) + Authenticator.hashSize + Authenticator.N:
            magicLen = len(Authenticator.authMagic)
            if data[:magicLen] == Authenticator.authMagic:
                
                hashStart = len(Authenticator.authMagic)
                hashEnd = int(hashStart) + int(Authenticator.hashSize)
                receiveHash = data[hashStart:hashEnd]
                receiveToken = data[hashEnd:]

                if self.sendToken == receiveToken:
                    raise AuthError("Same random token sent from other side, potentially a replay attack!")
                
                # Compute and authenticate received HMACs
                intermediateHash = hmac.new(key=receiveToken, msg=self.sharedSecret, digestmod=hashlib.sha256).digest()
                computedHash = hmac.new(key=self.conn.getKey(), msg=intermediateHash, digestmod=hashlib.sha256).digest()
                
                # Cryptographically secure compare
                if hmac.compare_digest(computedHash, receiveHash):
                    logging.info("Other side is authenticated!")
                    return
                else:
                    raise AuthError("Authentication failed")

class AuthError(Exception):
    pass
