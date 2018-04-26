from Crypto.PublicKey import RSA

secret_code = "Unguessable"
private_key = RSA.generate(2048)
public_key=private_key.publickey()

print (private_key.exportKey(format='PEM'))