import socket
import pysocket
import pickle
from sympy import *
def comm(message,signature):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10002)
    sock.connect(server_address)
    try:
            type=b'com'
            pysocket.send_msg(sock,type)
            pysocket.send_msg(sock,message)
            pysocket.send_msg(sock,signature)
            succes=pysocket.recv_msg(sock)
            if succes==b'valid comm':
                return True,sock
            else:
                sock.close()
                return False
    finally:
            print("succes new comm")
def payment(sock,c1,c3,c5):
    i1 = c1[1]
    i3 = c3[1]
    i5 = c5[1]
    try:

        while True:
            if len(c1[0]) - i1 - 1==0 and len(c3[0]) - i3 - 1==0 and len(c5[0]) - i5 - 1==0:
                print("No more funds in the account. Closing operation")
                return False,i1,i3,i5
            value=int(input("Value centi = "))
            while value-1>(len(c1[0])-i1-1)+(len(c3[0])-i3-1)*3+(len(c5[0])-i5-1)*5:
                print("Value too big")
                value = int(input("Value centi = "))
            if value<=0:
                print("Closing operation")
                return True,i1,i3,i5
            type=b'pay'
            pysocket.send_msg(sock,type)
            payment_representation=get_payment_representation(value,len(c1[0])-i1-1,len(c3[0])-i3-1,len(c5[0])-i5-1)
            print([len(c1[0])-i1-1,len(c3[0])-i3-1,len(c5[0])-i5-1])
            print(payment_representation)
            if payment_representation[0]!=0 or payment_representation[1]!=0 or payment_representation[2]!=0:
                payment_representation_bytes=[[c1[0][payment_representation[0]+i1],payment_representation[0]],[c3[0][payment_representation[1]+i3],payment_representation[1]],[c5[0][payment_representation[2]+i5],payment_representation[2]]]
            else:
                print("No more funds in the account. Closing operation")
                return False,i1,i3,i5
            payment_representation_bytes=pickle.dumps(payment_representation_bytes,-1)

            pysocket.send_msg(sock,payment_representation_bytes)
            succes=pysocket.recv_msg(sock)
            if succes==b'valid payment':
                i1 += payment_representation[0]
                i3 += payment_representation[1]
                i5 += payment_representation[2]
                print([len(c1[0]) - i1 - 1, len(c3[0]) - i3 - 1, len(c5[0]) - i5 - 1])
                print("Valid payment")
            else:
                print("Invalid payment")
    except:
        print("error")
def get_payment_representation(n,c1,c3,c5):
   if c1==0 and c3==0 and c5==0:
       return [0,0,0]
   if c1==0 and c3==0:
       for i in range(0,c5+1):
           if i*5==n:
               return [0,0,i]
   if c1==0 and c5==0:
       for i in range(0,c3+1):
           if i*3==n:
               return [0,i,0]
   if c3 == 0 and c5 == 0:
       for i in range(0, c1+1):
           if i  == n:
               return [i, 0, 0]
   if c1==0:
       for i in range(0,c3+1):
           for j in range(0,c5+1):
               if i*3+j*5==n:
                   return [0,i,j]
   if c3 == 0:
       for i in range(0, c1+1):
           for j in range(0, c5+1):
               if i + j * 5 == n:
                   return [i, 0, j]
   if c5 == 0:
       for i in range(0, c1+1):
           for j in range(0, c3+1):
               if i + j * 3 == n:
                   return [i, j, 0]
   for i in range(0,c1+1):
        for j in range(0,c3+1):
            for k in range (0,c5+1):
                if i + j*3+k*5==n:
                    return [i,j,k]
   return [0,0,0]

