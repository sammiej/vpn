from logger import logger
import hashlib
import hmac
import secrets
import string
import socket
from logger import logger
import util

prefix = "Authentication"

def halt():
    logger.info("Press Continue...")
    util.halt()

"""
    Executes the mutual authentication protocol.
    """
class Authenticator(object):
    N = 7 # length of random hashToken
    hashSize = 256 / 8 #(sha-256)
    authMagic = "sendreceive".encode("utf-8") # to identify auth messages sent over self.conn
    """
    Params:
      sharedSecret: a secret string
    """
    def __init__(self, sharedSecret):
        self.sharedSecret = sharedSecret.encode("utf-8")
    
    def generateHashToken(self):
        return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(Authenticator.N))
    
    def authenticateSend(self):
        # Compute HMACs
        logger.info("{}: generating random token to calculate first hmac to prevent replay attack".format(prefix))
        self.sendToken = self.generateHashToken().encode("utf-8")
        
        logger.info("{}: random token: {}".format(prefix, self.sendToken))
        halt()

        logger.info("{}: calculating intermediate hmac, HMAC(sharesecret, random token)".format(prefix))
        intermediateHash = hmac.new(key=self.sendToken, msg=self.sharedSecret, digestmod=hashlib.sha256).digest()
        logger.info("{}: intermediate hmac value: {}".format(prefix, intermediateHash))
        halt()

        logger.info("{}: calculating final hmac, HMAC(intermediate hmac, session key)".format(prefix))
        computedHash = hmac.new(key=self.conn.getKey(), msg=intermediateHash, digestmod=hashlib.sha256).digest() # h(h(S,N1),K)
        
        assert len(computedHash) == Authenticator.hashSize
        logger.info("{}: final hmac: {}".format(prefix, computedHash))
        halt()
        
        message = Authenticator.authMagic + computedHash + self.sendToken
        logger.debug("message: {}".format(message))
        # Send computed HMACs over
        try:
            logger.info("{}: sending final mac + random token: {}".format(prefix, message[len(Authenticator.authMagic):]))
            self.conn.send(message)
            logger.info("{}: authentication hash sent".format(prefix))
        except socket.error:
            logger.error("{}: connection broken on send".format(prefix))
            
    """
    Params:
      conn: should be an encrypted connection object
    """
    def authenticate(self, conn):
        logger.info("{}: beginning authentication procedure".format(prefix))
        self.conn = conn
        self.authenticateSend()

        logger.info("{}: waiting to receive authentication data from other host".format(prefix))
        data = self.conn.recv(asBytes=True)
        logger.info("{}: authentication data received!".format(prefix))
        logger.debug("Auth data: {}".format(data))
        if len(data) == len(Authenticator.authMagic) + Authenticator.hashSize + Authenticator.N:
            magicLen = len(Authenticator.authMagic)
            if data[:magicLen] == Authenticator.authMagic:
                logger.info("{}: authentication info received: {}".format(prefix, data[magicLen:]))
                
                hashStart = len(Authenticator.authMagic)
                hashEnd = int(hashStart) + int(Authenticator.hashSize)
                receiveHash = data[hashStart:hashEnd]
                receiveToken = data[hashEnd:]

                logger.info("{}: received hmac: {}".format(prefix, receiveHash))
                logger.info("{}: received random token: {}".format(prefix, receiveToken))
                halt()
                
                logger.info("{}: checking that (our random token) != (other host random token)".format(prefix))
                if self.sendToken == receiveToken:
                    raise AuthError("Same random token sent from other side, potentially a replay attack!")
                
                # Compute and authenticate received HMACs
                intermediateHash = hmac.new(key=receiveToken, msg=self.sharedSecret, digestmod=hashlib.sha256).digest()
                computedHash = hmac.new(key=self.conn.getKey(), msg=intermediateHash, digestmod=hashlib.sha256).digest()

                logger.info("{}: computed hmac from other host random token: {}".format(prefix, computedHash))
                
                # Cryptographically secure compare
                if hmac.compare_digest(computedHash, receiveHash):
                    logger.info("{}: Other host is authenticated!".format(prefix))
                    return
                else:
                    raise AuthError("Authentication failed")
        
        raise AuthError("Incorrect authentication protocol!")

class AuthError(Exception):
    pass
