import socket
import sys
import pysocket
import sign
import pickle
import keyserver_methods
from Crypto.PublicKey import RSA
import hash_functions
import crypt
import datetime

now = datetime.datetime.now()
#generare RSA cheie pub/priv
private_key = RSA.generate(2048)
public_key=private_key.publickey()
#trimitem la server cheia sa publica si identitatea
print(keyserver_methods.reg("banca", public_key.exportKey("PEM")))
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
database={}
# Bind the socket to the port
server_address = ('localhost', 10000)
print (sys.stderr, 'starting up on %s port %s' % server_address)
sock.bind(server_address)
#structura cu dataele personale
mydata={"B":"banca"}
mydata["Kb"]=public_key.exportKey("PEM")
# Listen for incoming connections
sock.listen(1)
while True:
    # Wait for a connection
    print (sys.stderr, 'waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print ( sys.stderr, 'connection from', client_address)

        # Receive the data in small chunks and retransmit it
        type=pysocket.recv_msg(connection)

        if type==b'reg':
            #datele primite de la user
            message=pysocket.recv_msg(connection)
            message=crypt.decrypt(message,private_key.exportKey("PEM"))
            data1=message
            data=pickle.loads(data1)
            #completam structura cu datele necesare pentru user
            mydata["U"]=data["U"]
            database[data["U"]]={"currency":data["currency"],"pub_key":data["key"]}
            mydata["Uip"]=client_address
            difference2 = datetime.timedelta(weeks=5)
            mydata["exp"]=now+difference2
            mydata["info"]={'serial':hash_functions.random_with_N_digits(10),'cred_limit':30000}
            data_string = pickle.dumps(mydata, -1)


            signature=pysocket.recv_msg(connection) #receptionam semnatura
            signature=crypt.decrypt(signature,private_key.exportKey("PEM"))
            if sign.auth_sign(message, keyserver_methods.req(data["U"]), signature): #verificam semnatura userului conform cheii publice primite de la server
                pysocket.send_msg(connection,b'#succesRG') #confirmam userului ca semnatura e valida
                pysocket.send_msg(connection,crypt.encrypt(data_string,keyserver_methods.req(data["U"])))# trimitem certificatul
                signature=sign.get_sign(data_string,private_key) # semnam certificatul
                pysocket.send_msg(connection,crypt.encrypt(signature,keyserver_methods.req(data["U"])))#trimitem certificatul semnat
                connection.close()
            else:
                pysocket.send_msg(sock,b'#notsucces') #in caz ca semnatura nu e valida
                connection.close()
        if type==b'reg_seller':
            #datele primite de la seller
            message=pysocket.recv_msg(connection)
            data1=message
            data=pickle.loads(data1)
            database[data["V"]]={"currency":data["currency"],"pub_key":data["key"]}

            signature=pysocket.recv_msg(connection) #receptionam semnatura
            if sign.auth_sign(message, keyserver_methods.req(data["V"]), signature): #verificam semnatura userului conform cheii publice primite de la server
                pysocket.send_msg(connection,b'#succesRGS') #confirmam userului ca semnatura e valida
                connection.close()
            else:
                pysocket.send_msg(sock,b'#notsuccesRGS') #in caz ca semnatura nu e valida
                connection.close()
        if type==b'req_currency':
            #datele primite de la seller
            username=pysocket.recv_msg(connection)
            username=crypt.decrypt(username,private_key.exportKey("PEM"))
            semnatura=pysocket.recv_msg(connection)
            semnatura=crypt.decrypt(semnatura,private_key.exportKey("PEM"))
            if username.decode() in database.keys() and sign.auth_sign(username,database[username.decode()]["pub_key"],semnatura):
                pysocket.send_msg(connection,b'#succesRC')
                pysocket.send_msg(connection,crypt.encrypt(hash_functions.int_to_bytes(database[username.decode()]["currency"]),keyserver_methods.req(username.decode())))
            else:
                pysocket.send_msg(connection, b'#invalid username/sign')

        if type==b'upload_hash':
            user=pysocket.recv_msg(connection)
            user=crypt.decrypt(user,private_key.exportKey("PEM"))
            message=pysocket.recv_msg(connection)
            message=crypt.decrypt(message,private_key.exportKey("PEM"))
            signature=pysocket.recv_msg(connection)
            signature=crypt.decrypt(signature,private_key.exportKey("PEM"))
            if sign.auth_sign(message,database[user.decode()]["pub_key"],signature):
                pysocket.send_msg(connection,b'#succesUH')
            else:
                pysocket.send_msg(connection, b'#invalidsign')
            data1=message
            data=pickle.loads(data1)
            database[user.decode()]['hash1']=data[0]
            database[user.decode()]['hash2'] = data[1]
            database[user.decode()]['hash3'] = data[2]
        if type==b'request_payment':
            user=pysocket.recv_msg(connection)
            message=pysocket.recv_msg(connection)
            data1=message
            data=pickle.loads(data1)
            signature=pysocket.recv_msg(connection)
            if sign.auth_sign(message,database[user.decode()]["pub_key"],signature):
                if sign.auth_sign(data[0][0],public_key.exportKey("PEM"),data[0][1]):
                   if hash_functions.check(database[data[0][0]["U"]]["hash1"][0][0],data[1][0],data[1][1]) and hash_functions.check(database[data[0][0]["U"]]["hash2"][0][0],data[2][0],data[2][1]) and hash_functions.check(database[data[0][0]["U"]]["hash3"][0][0],data[3][0],data[3][1]):
                       pysocket.send_msg(connection,b'#succesTM')
                       database[user.decode()]["currency"]+=data[1][1]+data[2][1]*3+data[3][1]*5
                       database[data[0][0]["U"]]["currency"]-=data[1][1]+data[2][1]*3+data[3][1]*5
                       del database[data[0][0]["U"]]["hash1"][:data[1][1]]
                       del database[data[0][0]["U"]]["hash2"][:data[2][1]]
                       del database[data[0][0]["U"]]["hash2"][:data[3][1]]
                   else:
                       pysocket.send_msg(connection, b'#notsuccesTM')

                else:
                    pysocket.send_msg(connection,b'CUinvalid')
            else:
                pysocket.send_msg(connection, b'#invalidsign')
            print(user.decode(),database[user.decode()]["currency"],data[0][0]["U"],database[data[0][0]["U"]]["currency"])
    except IndexError:
        pysocket.send_msg(connection,b'invalid index')
    finally:
        # Clean up the connection
        connection.close()
