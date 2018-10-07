import random
import sys
import os
from random import randint

#------------------------------------------------------------------------------
# Client Diffie-Hellman key exchange class:
#
#   Client class generates shared prime number and primitive root,
#   and then send them to server. (to be efficient, they will be sent
#   with the client public key together)
#
#   Client class receives the server public key, and then calculate
#   the shared secret.
#------------------------------------------------------------------------------
class ClientKeyExchange:
    
    def __init__(self):
        self.sharedPrime        = generate_prime(8)                 # Generate a 8-bit prime number
        self.sharedRoot         = primitive_root(self.sharedPrime)  # Generate the corresponding primitive root
        self.clientRandNum      = random.randrange(10, 50)          # Client generates a random number from a range 10-50 
        self.clientPublicKey    = (self.sharedRoot)**(self.clientRandNum) % (self.sharedPrime) # Generate client public key

    # Get the public key from server and calculate the shared secret
    def shared_secret(self, serverPublicKey):
        self.clientSharedSecret = (serverPublicKey)**(self.clientRandNum) % (self.sharedPrime)

    # Method to get the shared prime number (sent to server)
    def get_shared_prime(self):
        return self.sharedPrime

    # Method to get the shared primitive root (sent to server)
    def get_shared_root(self):
        return self.sharedRoot

    # Method to get the client public key (sent to server)
    def get_client_public_key(self):
        return self.clientPublicKey

    # Method to get the client shared secret
    def get_client_shared_secret(self):
        return self.clientSharedSecret

#------------------------------------------------------
# Two functions used to generate random prime number
#------------------------------------------------------
def is_prime(num, test_count):
    if num == 1:
        return False
    if test_count >= num:
        test_count = num - 1
    for x in range(test_count):
        val = randint(1, num - 1)
        if pow(val, num-1, num) != 1:
            return False
    return True

def generate_prime(n): # Generate a n-bit prime number (n <= 1000)
    found_prime = False
    while not found_prime:
        p = randint(2**(n-1), 2**n)
        if is_prime(p, 1000):
            return p

#------------------------------------------------------
# Two functions used to find the primitive root
#------------------------------------------------------
def gcd(a,b):
    while a != b:
        if a > b:
            a = a - b
        else:
            b = b - a
    return a

def primitive_root(modulo):
    required_set = set(num for num in range (1, modulo) if gcd(num, modulo) == 1)
    for g in range(1, modulo):
        actual_set = set(pow(g, powers) % modulo for powers in range (1, modulo))
        if required_set == actual_set:
            return g


# Test code
clientTest = ClientKeyExchange()
clientTest.shared_secret(12) # Assume that the public key received from server is 12. 
print('Client: Shared prime number is:', clientTest.get_shared_prime())
print('Client: Shared primitive root is:', clientTest.get_shared_root())
print('Client: Public key is:', clientTest.get_client_public_key())
print('Client: Shared secret is:', clientTest.get_client_shared_secret())
