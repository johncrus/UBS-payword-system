from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP


def encrypt(message,key):
    file_out = open("encrypted_data.bin", "wb")

    recipient_key = RSA.import_key(key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    file_out.write(cipher_rsa.encrypt(session_key))

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message)
    [file_out.write(x) for x in (cipher_aes.nonce, tag, ciphertext)]
    file_out.close()
    file_in=open("encrypted_data.bin","rb")
    data_out=file_in.read()
    file_in.close()
    return data_out



def decrypt(ciphertext,key):
    file_out = open("encrypted_data.bin", "wb")
    file_out.write(ciphertext)
    file_out.close()
    file_in = open("encrypted_data.bin", "rb")

    private_key = RSA.import_key(key)

    enc_session_key, nonce, tag, ciphertext = \
        [file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]
    file_in.close()
    # Decrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data
