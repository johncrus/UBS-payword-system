from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256,SHA
import pickle
def get_sign(message,private_key):
    if type(message)==bytes:
         h = SHA256.new(message)
    else:
         h = SHA256.new(pickle.dumps(message,-1))
    signature = pkcs1_15.new(private_key).sign(h)
    return signature
def auth_sign(message,public_key,signature):
    if type(message)==bytes:
         h = SHA256.new(message)
    else:
         h = SHA256.new(pickle.dumps(message,-1))
    key = RSA.import_key(public_key)
    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False
