import socket

def reg(username,pubkey):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    sock.connect(server_address)
    try:
        message = b'reg'
        sock.send(message)
        message=sock.recv(20)
        sock.send(username.encode())
        message=sock.recv(20)
        sock.send(pubkey)
        status = sock.recv(20)
        sock.close()
        return status
    finally:
        sock.close()
def req(username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    sock.connect(server_address)
    try:
        message = b'req'
        sock.send(message)
        message=sock.recv(20)
        sock.send(username.encode())
        status = sock.recv(10000)
        sock.close()
        return status
    finally:
        sock.close()

