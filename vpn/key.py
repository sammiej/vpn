from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_der_public_key, Encoding, PublicFormat
from logger import logger

application_info = b'cpen442-simple-vpn'

class KeyExchanger(object):
    CLIENT = 0
    SERVER = 1
    """
    Uses a key exchange algorithm to exchange keys with the other
    host.
    """
    def exchangeKey(self, host_type, conn):
        self.conn = conn
        if host_type == KeyExchanger.CLIENT:
            self._client_exchange(ClientKeyExchange())
        elif host_type == KeyExchanger.SERVER:
            self._server_exchange(ServerKeyExchange())
        else:
            raise ValueError("Unknown host_type!")

    def _client_exchange(self, exchanger):
        exchanger.generate()
        key_stream = exchanger.serialize()
        logger.debug("Sending key stream: " + str(key_stream))
        self.conn.send(key_stream)
        server_pub_key_stream = self.conn.recv(asBytes=True)
        logger.debug("Received server key stream: " + str(server_pub_key_stream))
        key = exchanger.symmetric_key(server_pub_key_stream)
        self.conn.setKey(key)

    def _server_exchange(self, exchanger):
        client_pub_key_stream = self.conn.recv(asBytes=True)
        logger.debug("Received client key stream: " + str(client_pub_key_stream))
        exchanger.generate(client_pub_key_stream)
        key_stream = exchanger.serialize()
        logger.debug("Sending key stream: " + str(key_stream))
        self.conn.send(key_stream)
        key = exchanger.symmetric_key()
        self.conn.setKey(key)

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
    def __init__(self, key_len=16, key_size=512):
        self.key_len = key_len
        self.key_size = key_size
    
    def generate(self):
        parameters = dh.generate_parameters(generator=2, key_size=self.key_size, backend=default_backend())
        self._private_key = parameters.generate_private_key()
        self._public_key = self._private_key.public_key()
        logger.debug("Client public number y: {}".format(self._public_key.public_numbers().y))

    def serialize(self):
        return self._public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

    """
    Generate symmetric key
    Params:
      server_pub_key_stream: serialization byte stream received from the server, contains
        the public key info of the server
    Post-Condition:
      returns the derived symmetric key
    """
    def symmetric_key(self, server_pub_key_stream):
        peer_public_key = load_der_public_key(server_pub_key_stream, default_backend())
        shared_key     = self._private_key.exchange(peer_public_key) # Generate the agreed key
        derived_key    = HKDF(
            algorithm=hashes.SHA256(),
            length=self.key_len,
            salt=None,
            info=application_info,
            backend=default_backend()
        ).derive(shared_key)

        return derived_key

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
    def __init__(self, key_len=16):
        self.key_len = key_len

    """
    Generates the public key to send to the client

    Params:
      client_pub_key_stream: the public key serialization stream obtained from the client
    """
    def generate(self, client_pub_key_stream):
        self._peer_public_key = load_der_public_key(client_pub_key_stream, default_backend())
        self._private_key = self._peer_public_key.parameters().generate_private_key()
        self._public_key = self._private_key.public_key()
        logger.debug("Server public number y: {}".format(self._public_key.public_numbers().y)) 

    """
    Serializes the public key of the server to send to the client
    """
    def serialize(self):
        return self._public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

    """
    Generates the symmetric key used for encryption
    """
    def symmetric_key(self):
        shared_key = self._private_key.exchange(self._peer_public_key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=self.key_len,
            salt=None,
            info=application_info,
            backend=default_backend()
        ).derive(shared_key)

        return derived_key
