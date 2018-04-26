import socket
import sign
import pysocket

def register(message,signature):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    sock.connect(server_address)
    try:
            type=b'reg'
            pysocket.send_msg(sock,type)
            pysocket.send_msg(sock,message)
            pysocket.send_msg(sock,signature)
            succes=pysocket.recv_msg(sock)
            if succes==b'#succesRG':
                certificate=pysocket.recv_msg(sock)
                if certificate!=b'#invalid':
                    signature=pysocket.recv_msg(sock)
                    sock.close()
                    return certificate,signature
                else:
                    sock.close()
                    return b'invalid',b'invalid'
            else:
                sock.close()
                return b'#error',b'#error'

    finally:
            sock.close()
def upload_hash(user,message,signature):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    sock.connect(server_address)
    try:
            type=b'upload_hash'
            pysocket.send_msg(sock, type)
            pysocket.send_msg(sock,user)
            pysocket.send_msg(sock,message)
            pysocket.send_msg(sock,signature)
            succes=pysocket.recv_msg(sock)
            if succes==b'#succesUH':
                print("succes UH")
            else:
                sock.close()
                print(succes)

    finally:
            sock.close()
def register_seller(message,signature):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    sock.connect(server_address)
    try:
            type=b'reg_seller'
            pysocket.send_msg(sock, type)
            pysocket.send_msg(sock,message)
            pysocket.send_msg(sock,signature)
            succes=pysocket.recv_msg(sock)
            if succes==b'#succesRGS':
                print("succes RGS")
            else:
                sock.close()
                print(succes)

    finally:
            sock.close()
def request_payment(user,message,signature):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    sock.connect(server_address)
    try:
            type=b'request_payment'
            pysocket.send_msg(sock, type)
            pysocket.send_msg(sock,user.encode())
            pysocket.send_msg(sock,message)
            pysocket.send_msg(sock,signature)
            succes=pysocket.recv_msg(sock)
            if succes==b'#succesTM':
                print("succes TM")
            else:
                sock.close()
                print(succes)

    finally:
            sock.close()

def request_currency(message,signature):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    sock.connect(server_address)
    try:
            type=b'req_currency'
            pysocket.send_msg(sock, type)
            pysocket.send_msg(sock,message)
            pysocket.send_msg(sock,signature)
            succes=pysocket.recv_msg(sock)
            if succes==b'#succesRC':
                print("succes RC")
                return pysocket.recv_msg(sock)
            else:
                sock.close()
                print(succes)

    finally:
            sock.close()