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
    sharedSecret = '12345'.encode('utf-8') #dummy
    secretKey = 'ABCDE'.encode('utf-8') #dummy
    hashSize = 256 / 8 #(sha-256)
    authMagic = 'sendreceive'.encode('utf-8') # to identify auth messages sent over self.socket
    
    """
        Params:
        socket - currently initializes with the socket to
        send and receive auth messages over
        """
    def __init__(self, socket):
        self.socket = socket
    
    def generateHashToken(self):
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(Authenticator.N))
    
    def authenticateSend(self):
        # Compute HMACs
        sendToken = self.generateHashToken().encode('utf-8')
        intermediateHash = hmac.new(key=sendToken, msg=Authenticator.sharedSecret, digestmod=hashlib.sha256).digest()
        computedHash = hmac.new(key=Authenticator.secretKey, msg=intermediateHash, digestmod=hashlib.sha256).digest() # h(h(S,N1),K)
        
        assert len(computedHash) == Authenticator.hashSize
        logging.info(computedHash)
        
        message = Authenticator.authMagic + computedHash + sendToken
        
        # Send computed HMACs over
        try:
            self.socket.send(message)
            print("Auth sent")
        except self.socket.error:
            logging.info("self.socket connection broken on send")

def authenticate(self):
    self.authenticateSend()
    
    data = self.socket.recv(1024)
        if len(data) == len(Authenticator.authMagic) + Authenticator.hashSize + Authenticator.N:
            magicLen = len(Authenticator.authMagic)
            if data[:magicLen] == Authenticator.authMagic:
                
                hashStart = len(Authenticator.authMagic)
                hashEnd = int(hashStart) + int(Authenticator.hashSize)
                receiveHash = data[hashStart:hashEnd]
                receiveToken = data[hashEnd:]
                
                # Compute and authenticate received HMACs
                intermediateHash = hmac.new(key=receiveToken, msg=self.sharedSecret, digestmod=hashlib.sha256).digest()
                computedHash = hmac.new(key=self.secretKey, msg=intermediateHash, digestmod=hashlib.sha256).digest()
                
                # Cryptographically secure compare
                if hmac.compare_digest(computedHash, receiveHash) == True:
                    return True
                else:
                    raise Exception('Authentication failed')

