"""Criptografia"""
import os

from sistema_de_salud.storage.autenticacion_json_store import AutenticacionJsonStore

from sistema_de_salud.cfg.gestor_centro_salud_config import KEY_FILES_PATH

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


class Criptografia:
    """Clase que recoge las principales funciones criptográficas utilizadas"""
    KEY_LABEL_USER_ID =   "_AutenticacionUsuario__id_usuario"
    KEY_LABEL_USER_SALT = "_AutenticacionUsuario__salt"
    KEY_LABEL_USER_KEY =  "_AutenticacionUsuario__key"

    def __init__(self):
        pass

    def guardar_password(self, id_usuario: str, password: str):
        """Deriva y almacena una password segura a partir de la contraseña del usuario"""
        # Derivamos una password segura mediante una KDF (Key Derivation Function)
        salt = os.urandom(16)  # generamos un salt aleatorio, los valores seguros tienen 16 bytes (128 bits) o más
        # Algoritmo de coste variable PBKDF2 (Password Based Key Derivation Function 2)
        # algoritmo: SHA256 ; longitud max: 2^32 - 1
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        # Derivamos la clave criptográfica
        key = kdf.derive(password.encode('utf-8'))      # encode('utf-8') para convertir de string a bytes
        # Convertimos salt y derived key en strings hexadecimales para almacenarlas
        salt_hex = salt.hex()
        key_hex = key.hex()
        # Guardamos la información de autenticación
        usuario = {
            self.KEY_LABEL_USER_ID: id_usuario,
            self.KEY_LABEL_USER_SALT: salt_hex,
            self.KEY_LABEL_USER_KEY: key_hex
        }
        store_credenciales = AutenticacionJsonStore()
        store_credenciales.guardar_credenciales_store(usuario)

    def comprobar_password(self, id_usuario: str, password: str):
        # Obtenemos el salt y la key del paciente almacenados
        store_credenciales = AutenticacionJsonStore()
        item = store_credenciales.buscar_credenciales_store(id_usuario)
        stored_salt_hex = item[self.KEY_LABEL_USER_SALT]
        stored_key_hex = item[self.KEY_LABEL_USER_KEY]
        print("Stored salt: ", stored_salt_hex)
        print("Stored key:   ", stored_key_hex)
        # Convertimos el salt a bytes
        stored_salt = bytes.fromhex(stored_salt_hex)
        # Derivamos la clave a partir del password introducido por el usuario
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=stored_salt, iterations=480000)
        key = kdf.derive(password.encode('utf-8'))
        # Convertimos la key a hexadecimal y comparamos con la key almacenada
        key_hex = key.hex()
        print("Generated key:", key_hex)
        if key_hex != stored_key_hex:
            return False
        return True

    def generar_claves_RSA(self, private_key_file_name: str, public_key_file_name: str):
        """Genera un par de claves (pública y privada) para un usuario con el criptosistema asimétrico RSA"""
        # Generamos una pareja de claves con RSA para el usuario
        private_key = rsa.generate_private_key(
            public_exponent=65537,              # Almost everyone should use 65537
            key_size=2048                       # Se recomienda que la clave sea de al menos 2048 bits (NIST 2016)
        )
        # Serializamos y guardamos la clave privada en un PEM file
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        private_key_path = os.path.join(KEY_FILES_PATH, private_key_file_name)
        with open(private_key_path, 'wb') as private_key_file:
            private_key_file.write(private_key_pem)
        # Serializamos y guardamos la clave pública en un PEM file
        public_key = private_key.public_key()   # Se deriva la public_key de la private_key
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        public_key_path = os.path.join(KEY_FILES_PATH, public_key_file_name)
        with open(public_key_path, 'wb') as public_key_file:
            public_key_file.write(public_key_pem)

