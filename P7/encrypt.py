#!/usr/bin/env python3

# Paulo Contreras Flores
# paulo.contreras.flores@gmail.com

import pyaes, pbkdf2, binascii, os, secrets, base64, mysql.connector, SecureString
from Crypto.Cipher import AES
import binascii, os
import scrypt
import json

def get_datos_conexion():
  with open('base.json') as json_file:
    return json.load(json_file)

def get_password():
  with open('password.json') as json_file:
    archivo_password = json.load(json_file)
    return archivo_password['password']


# El password necesita guardarse en un archivo separado
# y que no se suba a git
password = get_password()

# La idea es que estos datos vengan de otro lado como parte
# de una app mas completa, pero para la practica lo
# podrian dejar asi directo al codigo
name = "Jhon Connor"
diagnosis = b'Heridas por ataque de T-800'
treatment = b'Paracetamol cada 8 hrs'

# El algoritmo de derivacion de llaves PBKDF2 necesita
# una salt, se genera una salt pseudorandon de 16 bytes, 
# el min requerido son 8 bytes, y el max de 16 bytes
passwordSalt = os.urandom(16)

# Algoritmo de derivacion de llaves PBKDF2, se toman
# 32 bytes o 256 bits. Entonces se va a cifrar AES con
# una llave de 256 bits, o AES-256

secretKey = scrypt.hash(password, passwordSalt, N=16384, r=8, p=1, buflen=32)

# El modo de operacion CTR necesita un nonce (number
# once) o mejor conocido como vector de inicializacion
# o IV (initialization vector), de 256 bits para este
# ejemplo. Se recomienda generarlo "aleatoriamente"
# Para indicar a Pyaes que se va a usar un IV propio,
# se usa la función pyaes.Counter()
aes = AES.new(secretKey, AES.MODE_GCM)

# Cifrado del mensaje en claro. La separacion por bloques
# lo realiza la propia funcion
diagnosis_ciphertext,diagnosis_auth = aes.encrypt_and_digest(diagnosis)
aes = AES.new(secretKey, AES.MODE_GCM, nonce=aes.nonce)
treatment_ciphertext,treatment_auth = aes.encrypt_and_digest(treatment)


print('Password:', password)
print('Diagnosis:', diagnosis)
print('Medical treatment:', treatment)
print('PasswordSalt:', binascii.hexlify(passwordSalt))
print('AES encryption key:', binascii.hexlify(secretKey))
print('IV:', binascii.hexlify(aes.nonce))
print('Diagnosis encrypted:', binascii.hexlify(diagnosis_ciphertext))
print('Medical treatment encrypted:', binascii.hexlify(treatment_ciphertext))
print('Diagnosis tag:', binascii.hexlify(diagnosis_auth))
print('Medical treatment tag:', binascii.hexlify(treatment_auth))


# Se codifica en base 64 tanto la passwordSalt como el 
# criptograma para guardarlos en la base de datos
passwordSalt = base64.b64encode(passwordSalt)
diagnosis_ciphertext = base64.b64encode(diagnosis_ciphertext)
diagnosis_auth = base64.b64encode(diagnosis_auth)
treatment_ciphertext = base64.b64encode(treatment_ciphertext)
treatment_auth = base64.b64encode(treatment_auth)
iv = base64.b64encode(aes.nonce)

print('PasswordSalt (base64):', passwordSalt)
print('Diagnosis encrypted (base64):', diagnosis_ciphertext)
print('Medical treatment encrypted (base64):', treatment_ciphertext)
print('Diagnosis tag:',diagnosis_auth)
print('Medical treatment tag:', treatment_auth)


# Guardar los datos en una base de datos relacional
try:
    # Estos datos necesitan estar en un archivo separado 
    # del programa y tampoco deben subirse a git
    # El cifrado de la conexion se realizara en otra practica
    archivo_base = get_datos_conexion()
    mydb = mysql.connector.connect(
                                 user=archivo_base["user"],
                                 password=archivo_base["password"],
                                 host=archivo_base["host"],
                                 port=archivo_base["puerto"],
                                 database=archivo_base["base"])
    cursor = mydb.cursor()
    insert_query = """ INSERT INTO expediente (nombre, diagnostico, tratamiento, passwordSalt, iv, diagnostico_tag, treatment_tag) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    record_to_insert = (name, diagnosis_ciphertext, treatment_ciphertext, passwordSalt, iv,diagnosis_auth,treatment_auth)
    cursor.execute(insert_query, record_to_insert)

    mydb.commit()
    count = cursor.lastrowid

    print("Record inserted successfully with id ", count)


except mysql.connector.Error as err:
  print("Something went wrong: {}".format(err))


finally:
    if mydb:
        cursor.close()
        mydb.close()
        print("DBMS connection is closed")

# Sobrescribir el contenido de las variables para
# evitar que se puedan obtener los datos a través de 
# un volcado de memoria RAM
SecureString.clearmem(password)
SecureString.clearmem(diagnosis)
SecureString.clearmem(treatment)
SecureString.clearmem(secretKey)

print('AES encryption key:', binascii.hexlify(secretKey))
print('Password:', password)
print('Diagnosis:', diagnosis)
print('Treatment:', treatment)
