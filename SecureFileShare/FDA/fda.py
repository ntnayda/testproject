from contextlib import closing
from urllib.request import urlopen
from http.client import HTTPConnection
import sys
import json
import os
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
import io

print ("------------------------SecureFileShare's File Download Application----------------------------" +"\n")
print ("Use this application to encrypt files and upload files or to decrypt and download files." + "\n" + "Please enter your username and password from your" +
		" SecureFileShare account to begin.")
username = input('Enter Userid: ')
password = input('Enter Password: ')


def hashfile(afile):
	blocksize = 4096
	hasher = hashlib.sha256()
	with open(afile, "rb") as f:
		for chunk in iter(lambda: f.read(blocksize), b""):
			hasher.update(chunk)
	return hasher.hexdigest()

def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key, key_size=256):
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

def encrypt_file(file_name, key):
    with open(file_name, 'rb') as fo:
        plaintext = fo.read()
    enc = encrypt(plaintext, key)
    with open(file_name + ".enc", 'wb') as fo:
        fo.write(enc)

def decrypt_file(file_name, key):
    with open(file_name, 'rb') as fo:
        ciphertext = fo.read()
    dec = decrypt(ciphertext, key)
    file_ending = file_name.split(".")
    with io.FileIO(file_name.replace(".enc", "_decrypted.") + file_ending[1], "w") as file:
        file.write(dec)
    # with open(file_name[:-4], 'wb') as fo:
    #     fo.write(dec)


def display_report_files(report_id):
	key = '00112233445566778899aabbccddeeff'
	url="http://localhost:8000/fda_report_files/" + report_id
	with closing(urlopen(url)) as response:
		#print(response.read().decode())
		json_data = response.read().decode()
	
	print("")
	print("List of files that can be downloaded.")
	print("-------------------------------------------------------------------")
	files = json.loads(json_data)
	for file in files:
		print("id:" + str(file["id"]) + ", is_encrypted:" + str(file['is_encrypted']) + ", file_name:" + file["file_name"] + "\n\t" + " ,file_hash:" + file["file_hash"] + "\n")

	print("")
	print("-------------------------------------------------------------------")
	file_id = input("Please enter an id of a file to download: ")
	file_url = ""
	file_name = ""
	for file in files:
		if str(file["id"]) == file_id:
			file_url = "http://localhost:8000/media/" + file["file_name"]
			file_url_parts = file["file_name"].split('/')
			file_name = file_url_parts[len(file_url_parts)-1]
			file_hash_db = file["file_hash"]

			if(file['is_encrypted']):
				answer = input(file_name + " is encrypted. You must decrypt it to view the file. Would you like to decrypt?" + "\n")
				if(answer == 'y'):
					decrypt_file(file_name, key)
					print (file_name + " has been decrypted")
				else:
					print("Failed to download " + file_name + "Need to encrypt this file to view.")


			print("")
			#print(file_url)
			print("downloading " + file_name)
			break

	with closing(urlopen(file_url)) as response:
		data = response.read()

	with open(file_name, 'wb') as f:
		f.write(data)

	file_hash = hashfile(file_name)
	print("")
	print("-------------------------------------------------------------------")
	print("calculated file hash: " + file_hash)
	print("  original file hash: " + file_hash_db)
	if file_hash == file_hash_db:
		print("")
		print("File validated! File hash matches!")
	print("-------------------------------------------------------------------")
	with open(file_name + ".sha256", 'w') as f:
		f.write(file_hash)
	
	print("")
	print("Done!")
	
def display_reports():
	key = '00112233445566778899aabbccddeeff'
	url="http://localhost:8000/fda_login/" + username + "/" + password
	with closing(urlopen(url)) as response:
		#print(response.read().decode())
		json_data = response.read().decode()
	
	answer = (int)(input("Select an option:" + "\n" + "1. Encrypt a file to upload,"+ "\n" + "2. Decrypt a file to download" + "\n" + "3. Quit" + "\n"))
	if (answer == 1):
		file_to_encrypt = input("Enter the name of the file you want to encrypt: ")
		encrypt_file(file_to_encrypt, key)
		print(file_to_encrypt + "has been encrypted! Upload the desired file with the '.enc' ending.")
	elif (answer ==2):
		print("List of reports.")
		print("-------------------------------------------------------------------")
		reports = json.loads(json_data)
		for report in reports:
			print("report_id:" + str(report["report_id"]) + ", title:" + report["title"] + ", attachments:" + str(report["attachments"]))
		
		print("")
		print("-------------------------------------------------------------------")
		report_id = input("Please enter a report_id with attachments to download: ")
		print("-------------------------------------------------------------------")
		display_report_files(report_id)
	elif (answer==3):
		sys.exit(0)
	else:
		answer = (int)(input("Select an option:" + "\n" + "1. Encrypt a file to upload,"+ "\n" + "2. Decrypt a file to download" + "\n" + "3. Quit" + "\n"))
	
display_reports()





# from contextlib import closing
# from urllib.request import urlopen
# from http.client import HTTPConnection
# import sys
# import json
# import os
# import hashlib

# username = input('Enter Userid: ')
# password = input('Enter Password: ')

# def hashfile(afile):
# 	blocksize = 4096
# 	hasher = hashlib.sha256()
# 	with open(afile, "rb") as f:
# 		for chunk in iter(lambda: f.read(blocksize), b""):
# 			hasher.update(chunk)
# 	return hasher.hexdigest()


# def display_report_files(report_id):
# 	url="http://localhost:8000/fda_report_files/" + report_id
# 	with closing(urlopen(url)) as response:
# 		#print(response.read().decode())
# 		json_data = response.read().decode()
	
# 	print("")
# 	print("List of files that can be downloaded.")
# 	print("-------------------------------------------------------------------")
# 	files = json.loads(json_data)
# 	for file in files:
# 		print("id:" + str(file["id"]) + ", is_encrypted:" + str(file['is_encrypted']) + ", file_name:" + file["file_name"])

# 	print("")
# 	print("-------------------------------------------------------------------")
# 	file_id = input("Please enter an id of a file to download: ")
# 	file_url = ""
# 	file_name = ""
# 	for file in files:
# 		if str(file["id"]) == file_id:
# 			file_url = "http://localhost:8000/media/" + file["file_name"]
# 			file_url_parts = file["file_name"].split('/')
# 			file_name = file_url_parts[len(file_url_parts)-1]
# 			print("")
# 			#print(file_url)
# 			print("downloading " + file_name)
# 			break

# 	with closing(urlopen(file_url)) as response:
# 		data = response.read()

# 	with open(file_name, 'wb') as f:
# 		f.write(data)

# 	file_hash = hashfile(file_name)
# 	print("")
# 	print("-------------------------------------------------------------------")
# 	print("file hash: " + file_hash)
# 	print("-------------------------------------------------------------------")
# 	with open(file_name + ".sha256", 'w') as f:
# 		f.write(file_hash)
	
# 	print("")
# 	print("Done!")
	
# def display_reports():
# 	url="http://localhost:8000/fda_login/" + username + "/" + password
# 	with closing(urlopen(url)) as response:
# 		#print(response.read().decode())
# 		json_data = response.read().decode()
		
# 	print("Lis of reports.")
# 	print("-------------------------------------------------------------------")
# 	reports = json.loads(json_data)
# 	for report in reports:
# 		print("report_id:" + str(report["report_id"]) + ", title:" + report["title"] + ", attachments:" + str(report["attachments"]))
	
# 	print("")
# 	print("-------------------------------------------------------------------")
# 	report_id = input("Please enter a repor_id with attachments to download: ")
# 	print("-------------------------------------------------------------------")
# 	display_report_files(report_id)

	
# display_reports()



