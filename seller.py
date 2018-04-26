import socket
import sys
import pysocket
import sign
import pickle
import keyserver_methods
from Crypto.PublicKey import RSA
from dateutil import parser
import datetime
import hash_functions
import broker_methods

now = datetime.datetime.now()

#generare RSA cheie pub/priv
private_key = RSA.generate(2048)
public_key=private_key.publickey()
#trimitem la server cheia sa publica si identitatea
identitate={'V':'vanzator','currency':1000,'key':public_key.exportKey("PEM")}
print(keyserver_methods.reg(identitate['V'], public_key.exportKey("PEM")))
identitate_bytes=pickle.dumps(identitate,-1)
seller_signature=sign.get_sign(identitate_bytes,private_key)
broker_methods.register_seller(identitate_bytes,seller_signature)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10002)
print (sys.stderr, 'starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
while True:
    # Wait for a connection
    print (sys.stderr, 'waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print ( sys.stderr, 'connection from', client_address)
        c01 = 0
        c03 = 0
        c05 = 0
        i1 = 0
        i3 = 0
        i5 = 0
        cCU = 0
        sCU = 0
        cCOMM=0
        sCOMM=0
        # Receive the data in small chunks and retransmit it
        while True:
            type=pysocket.recv_msg(connection)

            if type==b'com':
                #angajamentul primit de la user
                message=pysocket.recv_msg(connection)
                semnatura=pysocket.recv_msg(connection)
                data1=message
                data=pickle.loads(data1)
                c01=data["c0"][0]
                c03=data["c0"][1]
                c05=data["c0"][2]
                cCU=data["cCU"]
                sCU=data["sCU"]
                cCOMM=message
                sCOMM=semnatura
                if not sign.auth_sign(message,keyserver_methods.req(data["U"]),semnatura):
                    pysocket.send_msg(connection,b'invalid user sign')
                    connection.close()
                    break
                if not sign.auth_sign(data["cCU"],keyserver_methods.req("banca"),data["sCU"]):
                    pysocket.send_msg(connection,b'invalid bank sign')
                    connection.close()
                    break
                currentdate=str(now.strftime("%Y-%m-%d"))
                currentdate=parser.parse(currentdate)
                if currentdate>parser.parse(data["d"]):
                    pysocket.send_msg(connection, b'date expired')
                    connection.close()
                    break
                pysocket.send_msg(connection,b'valid comm')
            if type == b'pay':
                payment_bytes=pysocket.recv_msg(connection)
                payment=pickle.loads(payment_bytes)
                if hash_functions.check(c01,payment[0][0],payment[0][1]) and hash_functions.check(c03,payment[1][0],payment[1][1]) and hash_functions.check(c05,payment[2][0],payment[2][1]):
                    pysocket.send_msg(connection,b'valid payment')
                    c01=payment[0][0]
                    c03=payment[1][0]
                    c05=payment[2][0]
                    i1+=payment[0][1]
                    i3+=payment[1][1]
                    i5+=payment[2][1]
                else:
                    pysocket.send_msg(connection,b'invalid payment')
            if type == b'close':
                package=[[cCU,sCU],[c01,i1],[c03,i3],[c05,i5],[cCOMM,sCOMM]]
                package_bytes=pickle.dumps(package,-1)
                package_sign=sign.get_sign(package_bytes,private_key)
                broker_methods.request_payment(identitate['V'],package_bytes,package_sign)
                broker_methods.request_payment(identitate['V'], package_bytes, package_sign)
                break

        connection.close()
    except:
        print("Unexpected error:", sys.exc_info()[0])
    finally:
        # Clean up the connection
        connection.close()