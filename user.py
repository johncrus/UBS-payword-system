import keyserver_methods
from Crypto.PublicKey import RSA
import sign
import broker_methods
import seller_methods
import hash_functions
import datetime
import pickle
import pysocket
import crypt


now = datetime.datetime.now()

alreadyexist=input("Have an account?: ")
if alreadyexist=='no':

      nume=input("Identitate = ")
      #generare chei RSA priv/pub
      private_key = RSA.generate(2048)
      public_key=private_key.publickey()

      #trimitem cheia publica la serverul de key publice
      print(keyserver_methods.reg(nume,public_key.exportKey("PEM")))

      #structura cu data personale inclusiv cheia publica
      data_for_broker={"currency":500}
      data_for_broker["U"]=nume
      data_for_broker["card_number"]=hash_functions.random_with_N_digits(16)
      data_for_broker["key"]=public_key.exportKey(format="PEM")


      #dict -> pickle pentru a putea semna si trimite prin socket
      data_string_for_broker=pickle.dumps( data_for_broker, -1 )

      #semnam mesajul
      signature_for_broker=sign.get_sign(data_string_for_broker,private_key)

      #inregistrare la broker pentru a primi certificatul
      certificat,semnatura=broker_methods.register(crypt.encrypt(data_string_for_broker,keyserver_methods.req("banca")), crypt.encrypt(signature_for_broker,keyserver_methods.req("banca")))
      #print(certificat)
      certificat=crypt.decrypt(certificat,private_key.exportKey("PEM"))
      semnatura=crypt.decrypt(semnatura,private_key.exportKey("PEM"))
      #transformare certificatul primit  in dictionar
      certificat=pickle.loads(certificat)


      #verificare semnatura broker
      print(sign.auth_sign(certificat,keyserver_methods.req(certificat["B"]),semnatura))
      data_file={'nume':nume,'private_key':private_key.exportKey("PEM"),'certificat':certificat,'semnatura':semnatura}
      filename=nume+'.pickle'
      with open(filename, 'wb') as handle:
            pickle.dump(data_file, handle, protocol=pickle.HIGHEST_PROTOCOL)

else:
      filename = input("Numele fisierului:  ")
      with open(filename, 'rb') as handle:
            data_loaded = pickle.load(handle)
      nume=data_loaded["nume"]
      private_key=RSA.import_key(data_loaded["private_key"])
      certificat=data_loaded["certificat"]
      semnatura=data_loaded["semnatura"]

identitate_bytes=nume.encode()
semnatura_identitate=sign.get_sign(identitate_bytes,private_key)
response=broker_methods.request_currency(crypt.encrypt(identitate_bytes,keyserver_methods.req("banca")),crypt.encrypt(semnatura_identitate,keyserver_methods.req("banca")))
n=crypt.decrypt(response,private_key.exportKey("PEM"))
n=hash_functions.int_from_bytes(n)//10

lant1=[hash_functions.generate_hash(n),0]
lant2=[hash_functions.generate_hash(n),0]
lant3=[hash_functions.generate_hash(n),0]

hashuri=[[[i,0] for i in lant1[0]],[[i,0] for i in lant2[0]],[[i,0] for i in lant3[0]]]
data_string_hash=pickle.dumps(hashuri,-1)
signature_for_hash=sign.get_sign(data_string_hash,private_key)
#upload hash la banca

broker_methods.upload_hash(crypt.encrypt(identitate_bytes,keyserver_methods.req("banca")),crypt.encrypt(data_string_hash,keyserver_methods.req("banca")),crypt.encrypt(signature_for_hash,keyserver_methods.req("banca")))

angajament={"V":"vanzator"}
angajament["U"]=nume
angajament["cCU"]=certificat
angajament["sCU"]=semnatura
angajament["c0"]=(lant1[0][0],lant2[0][0],lant3[0][0])
angajament["d"]=str(now.strftime("%Y-%m-%d"))
angajament["info"]=hash_functions.int_to_bytes(n)


data_string_for_seller=pickle.dumps(angajament,-1)

signature_for_seller=sign.get_sign(data_string_for_seller,private_key)


succes,sock=seller_methods.comm(data_string_for_seller,signature_for_seller)
while succes:
      j,lant1[1],lant2[1],lant3[1]=seller_methods.payment(sock,lant1,lant2,lant3)
      if not j:
            pysocket.send_msg(sock, b'close')
            sock.close()
            break
      x=input("Close session?: ")
      if x=='yes':
            pysocket.send_msg(sock, b'close')
            sock.close()
            break
else:
      print("Comm invalid")






