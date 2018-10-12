import os
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.primitives.serialization import load_der_public_key

#------------------------------------------
# Diffie-Hellman key exchange parameters class:
#
#   Parameters class generates shared prime number and primitive root
#------------------------------------------
class KeyExchangeParameters:
    
    def __init__(self):
        # Create a 'DHParameters' instance
        self.parameters = dh.generate_parameters(generator=2, key_size=512,
                                    backend=default_backend()) # Generate a 512-bit prime number; primitive root (= generator) = 2 

        # Shared prime number and primitive root
        self.shared_prime  = self.parameters.parameter_numbers().p # Get the shared prime number
        self.shared_root   = self.parameters.parameter_numbers().g # Get the shared primitive root
'''
    # Get methods
    parameters      = self.parameters
    shared_prime    = self.shared_prime
    shared_root     = self.shared_root 
'''
#------------------------------------------------------------------------------
# Client Diffie-Hellman key exchange class:
#
#   - Generates its own private and public key.
#   
#   - Pass the public key value to server class
#
#   - Receive the server public key, and then calculate the symmetric key.
#------------------------------------------------------------------------------
class ClientKeyExchange:
    
    def __init__(self, parameters, shared_prime, shared_root):

        self.parameters     = parameters
        self.shared_prime   = shared_prime
        self.shared_root    = shared_root

    # Private key
    def generate_private_key(self):
    
        self.private_key        = self.parameters.generate_private_key()     # Generate private key
        self.private_key_value  = self.private_key.private_numbers().x  # Get the private key value 

    # Public key
    def generate_public_key(self):
        
        self.public_key         = self.private_key.public_key()         # Generate a public key associated with the private key
        self.public_key_value   = self.public_key.public_numbers().y    # Get the public key value 

    # Assemble 'DHPublicKey' instance so that exchange(peer_public_key) can use it as parameter
    def assamble_public_key(self, server_public_key_value):
        
        self.peer_public_key_value  = server_public_key_value                                       # Receive the public key value from server
        self.pn                     = dh.DHParameterNumbers(self.shared_prime, self.shared_root)    # Assemble 'DHParameterNumbers' instance
        self.peer_public_numbers    = dh.DHPublicNumbers(self.peer_public_key_value, self.pn)       # Assemble 'DHPublicNumbers' instance
        self.peer_public_key        = self.peer_public_numbers.public_key(default_backend())        # Get the 'DHPublicKey' instance

    # Generate symmetric key
    def symmetric_key(self):
        
        self.shared_key     = self.private_key.exchange(self.peer_public_key) # Generate the agreed key
        
        self.derived_key    = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
            backend=default_backend()
        ).derive(self.shared_key)
'''
    # Get values
    shared_prime        = self.shared_prime
    shared_root         = self.shared_root
    private_key_value   = self.private_key_value
    public_key_value    = self.public_key_value
    shared_key          = self.shared_key
    derived_key         = self.derived_key
'''
#------------------------------------------------------------------------------
# Server Diffie-Hellman key exchange class:
#
#   - Generates its own private and public key.
#   
#   - Pass the public key value to client class
#
#   - Receive the client public key, and then calculate the symmetric key.
#------------------------------------------------------------------------------
class ServerKeyExchange:
    
    def __init__(self, parameters, shared_prime, shared_root):

        self.parameters     = parameters
        self.shared_prime   = shared_prime
        self.shared_root    = shared_root

    # Private key
    def generate_private_key(self):
        
        self.private_key        = self.parameters.generate_private_key()     # Generate private key
        self.private_key_value  = self.private_key.private_numbers().x  # Get the private key value 

    # Public key
    def generate_public_key(self):
    
        self.public_key         = self.private_key.public_key()         # Generate a public key associated with the private key
        self.public_key_value   = self.public_key.public_numbers().y    # Get the public key value 

    # Assemble 'DHPublicKey' instance so that exchange(peer_public_key) can use it as parameter
    def assamble_public_key(self, client_public_key_value):
        
        self.peer_public_key_value  = client_public_key_value                                       # Receive the public key value from client
        self.pn                     = dh.DHParameterNumbers(self.shared_prime, self.shared_root)    # Assemble 'DHParameterNumbers' instance
        self.peer_public_numbers    = dh.DHPublicNumbers(self.peer_public_key_value, self.pn)       # Assemble 'DHPublicNumbers' instance
        self.peer_public_key        = self.peer_public_numbers.public_key(default_backend())        # Get the 'DHPublicKey' instance

    # Generate symmetric key
    def symmetric_key(self):
        
        self.shared_key     = self.private_key.exchange(self.peer_public_key) # Generate the agreed key
        
        self.derived_key    = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
            backend=default_backend()
        ).derive(self.shared_key)
'''
    # Get values
    shared_prime        = self.shared_prime
    shared_root         = self.shared_root
    private_key_value   = self.private_key_value
    public_key_value    = self.public_key_value
    shared_key          = self.shared_key
    derived_key         = self.derived_key
'''


        
# Before actual implementation:
#   Do: change the key_size to 2048 or higher

#----------------------------------------------
# Example codes on how to use the classes
#----------------------------------------------

p = KeyExchangeParameters() # Create a 'KeyExchangeParameters' instance

c = ClientKeyExchange(p.parameters, p.shared_prime, p.shared_root)     # Create a 'ClientKeyExchange' instance
s = ServerKeyExchange(p.parameters, p.shared_prime, p.shared_root)     # Create a 'ServerKeyExchange' instance

# Generate private key
c.generate_private_key()
s.generate_private_key()

# Generate public key
c.generate_public_key()
s.generate_public_key()

# Send public keys to each other
c.assamble_public_key(s.public_key_value) # server sends its public key to client
s.assamble_public_key(c.public_key_value) # client sends its public key to server

# Generate the symmetric key
c.symmetric_key()
s.symmetric_key()

print("Parameters: \nprime = {} \nroot = {}".format(p.shared_prime, p.shared_root))
print("")
print("Client: \nprime = {} \nroot = {} \nprivate_key_value = {} \npublic_key_value = {} \nshared_key = {} \nderived_key = {}"
      .format(c.shared_prime, c.shared_root, c.private_key_value, c.public_key_value, c.shared_key, c.derived_key))
print("")
print("Server: \nprime = {} \nroot = {} \nprivate_key_value = {} \npublic_key_value = {} \nshared_key = {} \nderived_key = {}"
      .format(s.shared_prime, s.shared_root, s.private_key_value, s.public_key_value, s.shared_key, s.derived_key))














    
          
