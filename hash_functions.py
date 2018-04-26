from Crypto.Util import number
from Crypto.Hash import SHA256
from random import randint
def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def int_from_bytes(xbytes):
    return int.from_bytes(xbytes, 'big')

def generate_hash(n):
      lant_hash=[]
      n_length = 100
      x = number.getPrime(n_length)
      h=SHA256.new(int_to_bytes(x))
      lant_hash.append(h.digest())
      for i in range(0,n):
             lant_hash.append(SHA256.new(lant_hash[i]).digest())
      return lant_hash[::-1]
def check(c0,ci,i):
    if i==0:
        if c0==ci:
            return True
        else:
            return False
    nextc=SHA256.new(ci).digest()
    for j in range(1,i):
        nextc=SHA256.new(nextc).digest()
    if c0!=nextc:
        return False
    else:
        return True

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)
