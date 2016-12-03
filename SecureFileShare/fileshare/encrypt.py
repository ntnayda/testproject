from Crypto.PublicKey import RSA
from Crypto.Cipher import DES3

import io
import os
from Crypto import Random

random_generator = Random.new().read
key = RSA.generate(1024,random_generator)

def secret_string(string,pkey):
    encryptedString = pkey.encrypt(string.encode(),1)
    return encryptedString




def encrypt_file(filename,thekey):
    iv = b'01234567'
    des3 = DES3.new(thekey,DES3.MODE_CFB,iv)
    chunksize = 8192
    if filename == "": return False

    with open(filename,'rb') as infile:
        with open(filename+".enc",'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk)%16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)
                outfile.write(des3.encrypt(chunk))
    return True



def decrypt_file(filename,thekey):
    iv = b'01234567'
    des3 = DES3.new(thekey,DES3.MODE_CFB,iv)
    chunksize = 8192
    if(filename[-4:0] != ".enc"):
        return False
    if filename == "": return False

    with open(filename,'rb') as infile:
        with open("DEC_"+filename[:-4],'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(des3.decrypt(chunk))
    return True


pubkey = key.publickey()

encrypt_data = secret_string('Poopsie',key.publickey())

print(encrypt_data)

print(key.decrypt(encrypt_data))

print(encrypt_file("encrypt.py",b'0123456789123456'))
print(decrypt_file("encrypt.py",b'0123456789123456'))

opposite = key.decrypt('Poopsie')
print(opposite)
print(key.encrypt(opposite.encode(),1))