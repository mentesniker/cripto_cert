#!/usr/bin/env python3

# Paulo Contreras Flores
# paulo.contreras.flores@gmail.com

import pyaes, pbkdf2, binascii, os, secrets, base64, mysql.connector, SecureString
from Crypto.Cipher import AES
import scrypt
import json

def descifra(data, password):
  print("data",{
      'Id:': data[0],
      'Name:': data[1],
      'Diagnosis (base64):': data[2],
      'Medical treatment (base64):': data[3],
      'PasswordSalt': data[4],
      'IV': data[5],
      'Diagnosis tag:': data[6],
      'Medical treatment tag:': data[7],
      })


  # Decodificacion de base64
  diagnosis_ciphertext = base64.b64decode(data[2])
  treatment_ciphertext = base64.b64decode(data[3])
  passwordSalt = base64.b64decode(data[4])
  iv = base64.b64decode(data[5])

  print('Diagnosis encrypted:', binascii.hexlify(diagnosis_ciphertext))
  print('Medical treatment encrypted:', binascii.hexlify(treatment_ciphertext))
  print('IV',iv)

  secretKey = scrypt.hash(password, passwordSalt, N=16384, r=8, p=1, buflen=32)
  print('key',binascii.hexlify(secretKey))

  aesCipher = AES.new(secretKey, AES.MODE_GCM, iv)

  # Descifrado del mensaje en claro
  diagnosis = aesCipher.decrypt_and_verify(diagnosis_ciphertext, base64.b64decode(data[6]))
  aesCipher = AES.new(secretKey, AES.MODE_GCM, iv)
  treatment = aesCipher.decrypt_and_verify(treatment_ciphertext, base64.b64decode(data[7]))

  print('Diagnosis:', diagnosis)
  print('Medical treatment:', treatment)

  # Sobrescribir el contenido de las variables para
  # evitar que se puedan obtener los datos a través de 
  # un volcado de memoria RAM
  SecureString.clearmem(password)
  SecureString.clearmem(diagnosis)
  SecureString.clearmem(treatment)
  SecureString.clearmem(secretKey)

  print('AES encryption key:', binascii.hexlify(secretKey))
  print('Password:', password)
  print('Diagnosis:', binascii.hexlify(diagnosis))
  print('Treatment:', binascii.hexlify(treatment))

def get_datos_conexion():
  with open('base.json') as json_file:
    return json.load(json_file)

def get_password():
  with open('password.json') as json_file:
    archivo_password = json.load(json_file)
    return archivo_password['password']

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
    cursor.execute("SELECT * from expediente;")
    datas = cursor.fetchall()

except mysql.connector.Error as err:
  print("Something went wrong: {}".format(err))

finally:
    if mydb:
        mydb.close()
        print("DBMS connection is closed")
password = get_password()
for data in datas:
  descifra(data, password)