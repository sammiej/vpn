import random
import sys
import os
from random import randint

#------------------------------------------------------------------------------
# Server Diffie-Hellman key exchange class:
#
#   Server class generates shared prime number and primitive root,
#   and then send them to server. (to be efficient, they will be sent
#   with the client public key together)
#
#   Client class receives the server public key, and then calculate
#   the shared secret.
#------------------------------------------------------------------------------
class ServerKeyExchange:

    def __init__(self):
        self.serverRandNum = 13 # For testing
        #self.serverRandNum = random.randrange(10, 50)  # Server generates a random number from a range 10-50 
        
    # Receive the shared prime number and primitive root from client and calculate server's public key
    def server_public_key(self, sharedRoot, sharedPrime):
        self.serverPublicKey = (sharedRoot)**(self.serverRandNum) % (sharedPrime)

    # Receive the public key from client and calculate the shared secret
    def shared_secret(self, clientPublicKey, sharedPrime):
        self.serverSharedSecret = (clientPublicKey)**(self.serverRandNum) % (sharedPrime)

    # Method to get the server public key (sent to client)
    def get_server_public_key(self):
        return self.serverPublicKey

    # Method to get the server shared secret
    def get_server_shared_secret(self):
        return self.serverSharedSecret


# Todo: random number generator
#       DH library


# Test code
serverTest = ServerKeyExchange()
serverTest.server_public_key(3,17)
serverTest.shared_secret(6, 17)
print('Server: Public key is:', serverTest.get_server_public_key())
print('Server: Shared secret is:', serverTest.get_server_shared_secret())
