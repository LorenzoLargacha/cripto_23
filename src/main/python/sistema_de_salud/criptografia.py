"""Criptografia"""
import os
from datetime import datetime, timedelta

import cryptography

from sistema_de_salud.storage.autenticacion_json_store import AutenticacionJsonStore

from sistema_de_salud.cfg.gestor_centro_salud_config import KEY_FILES_PATH
from sistema_de_salud.cfg.gestor_centro_salud_config import CERT_FILES_PATH

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography import exceptions


class Criptografia:
    """Clase que recoge las principales funciones criptográficas utilizadas"""
    KEY_LABEL_USER_ID =   "_AutenticacionUsuario__id_usuario"
    KEY_LABEL_USER_SALT = "_AutenticacionUsuario__salt"
    KEY_LABEL_USER_KEY =  "_AutenticacionUsuario__key"

    def __init__(self):
        pass

    def guardar_password(self, id_usuario: str, password: str):
        """Deriva y almacena una clave segura a partir de la contraseña del usuario"""
        # Derivamos una clave segura mediante una KDF (Key Derivation Function)
        salt = os.urandom(16)  # generamos un salt aleatorio, los valores seguros tienen 16 bytes (128 bits) o más
        # Algoritmo de coste variable PBKDF2 (Password Based Key Derivation Function 2)
        # algoritmo: SHA256 ; longitud max: 2^32 - 1
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        # Derivamos la clave criptográfica a partir del password introducido por el usuario
        key = kdf.derive(password.encode('utf-8'))      # encode('utf-8') para convertir de string a bytes
        # Convertimos el salt y la derived key en strings hexadecimales para almacenarlos
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
        """Comprueba una contraseña introducida por el usuario con la clave derivada almacenada"""
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

    def obtener_clave_privada(self, private_key_file_name: str):
        """Obtiene la clave privada a partir de un archivo pem"""
        private_key_path = os.path.join(KEY_FILES_PATH, private_key_file_name)
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        return private_key

    def obtener_clave_publica(self, public_key_file_name: str):
        """Obtiene la clave pública a partir de un archivo pem"""
        public_key_path = os.path.join(KEY_FILES_PATH, public_key_file_name)
        with open(public_key_path, 'rb') as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read()
            )
        return public_key

    def encriptar_RSA(self, message: bytes, cert):
        """Encripta un mensaje con el criptosistema asimétrico RSA"""
        public_key = cert.public_key()
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def desencriptar_RSA(self, ciphertext: bytes, private_key_file_name):
        """Desencripta un mensaje con el criptosistema asimétrico RSA"""
        private_key = self.obtener_clave_privada(private_key_file_name)
        message = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return message

    def firmar_mensaje(self, message: bytes, private_key_file_name: str):
        """Firma un mensaje con la clave privada del usuario"""
        private_key = self.obtener_clave_privada(private_key_file_name)
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def comprobar_firma(self, message: bytes, signature, public_key):
        """Comprueba la firma de un mensaje con la clave pública de quien lo firmó"""
        # Si la firma no coincide lanza una excepción
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def crear_autoridad_raiz(self):
        """Crea las claves y emite el certificado del Ministerio de Sanidad (Autoridad Raíz - AC1)"""
        # Generamos una pareja de claves con RSA para el Ministerio de Sanidad
        private_key_file_name = "ministerioSanidad_private_key.pem"
        self.generar_claves_RSA(private_key_file_name, "ministerioSanidad_public_key.pem")
        private_key_ac1 = self.obtener_clave_privada(private_key_file_name)
        public_key_ac1 = private_key_ac1.public_key()
        # Creamos el certificado autofirmado
        cert_file_name = "ministerioSanidad_cert.pem"
        # subject e issuer son lo mismo en un certificado autofirmado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ministerio de Sanidad"),
            x509.NameAttribute(NameOID.TITLE, "Autoridad Raiz"),
            x509.NameAttribute(NameOID.COMMON_NAME, "sanidad.gob.es"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
        ])
        # Utiliza su clave privada para firmar su propio certificado
        cert = self.crear_certificado(subject, issuer, 1460, public_key_ac1, private_key_ac1, cert_file_name)
        return cert

    def crear_autoridad_subordinada_centro_salud(self, centro_salud, cert_ac1):
        """Crea las claves y emitir el certificado del Centro de Salud (Autoridad de Certificación - AC2)"""
        # Generamos una pareja de claves con RSA para el centro de salud
        self.generar_claves_RSA(centro_salud.private_key_file_name, centro_salud.public_key_file_name)
        private_key = self.obtener_clave_privada(centro_salud.private_key_file_name)
        # Crear una Solicitud de Firma de Certificado (CSR) para el centro de salud
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            # Información del centro de salud
            x509.NameAttribute(NameOID.USER_ID, centro_salud.id_centro),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, centro_salud.nombre_centro),
            x509.NameAttribute(NameOID.COUNTRY_NAME, centro_salud.pais),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, centro_salud.provincia),
            x509.NameAttribute(NameOID.LOCALITY_NAME, centro_salud.municipio),
        ])).sign(private_key, hashes.SHA256())  # Firmar la CSR con la clave privada del centro de salud
        # Emitir certificado para el centro de salud (AC2) firmado con la clave privada de Ministerio Sanidad (AC1)
        ac1_key = self.obtener_clave_privada(centro_salud.autoridad_raiz + "_private_key.pem")
        cert = self.crear_certificado(csr.subject, cert_ac1.subject, 365, csr.public_key(), ac1_key, centro_salud.cert_file_name)
        return cert

    def crear_autoridad_subordinada_fnmt(self, cert_ac1):
        """Crea las claves y emitir el certificado de la Fábrica Nacional de Moneda y Timbre
        (Autoridad de Certificación - AC3)"""
        # Generamos una pareja de claves con RSA para la FNMT
        private_key_file_name = "fnmt_private_key.pem"
        self.generar_claves_RSA(private_key_file_name, "fnmt_public_key.pem")
        private_key = self.obtener_clave_privada(private_key_file_name)
        # Crear una Solicitud de Firma de Certificado (CSR) para la FNMT
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            # Información de la FNMT
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Fabrica Nacional de Moneda y Timbre"),
            x509.NameAttribute(NameOID.COMMON_NAME, "fnmt.es"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
        ])).sign(private_key, hashes.SHA256())  # Firmar la CSR con la clave privada de la FNMT
        # Emitir certificado para la FNMT (AC3) firmado con la clave privada de Ministerio Sanidad (AC1)
        ac1_key = self.obtener_clave_privada("ministerioSanidad_private_key.pem")
        cert_file_name = "fnmt_cert.pem"
        cert = self.crear_certificado(csr.subject, cert_ac1.subject, 365, csr.public_key(), ac1_key, cert_file_name)
        return cert

    def crear_certificado(self, subject, issuer, duration, public_key_subject, private_key_ac, cert_file_name):
        """Crea un certificado X.509"""
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            public_key_subject
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=duration)
        ).sign(private_key_ac, hashes.SHA256())  # Firmar el certificado con la clave privada de la Autoridad de Certificación
        # Guardamos el certificado en un PEM file
        cert_path = os.path.join(CERT_FILES_PATH, cert_file_name)
        with open(cert_path, 'wb') as cert_file:
            cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
        return cert

    def obtener_certificado(self, cert_file_name: str):
        """Obtiene el certificado a partir de un archivo pem"""
        cert_path = os.path.join(CERT_FILES_PATH, cert_file_name)
        with open(cert_path, 'rb') as cert_file:
            cert = x509.load_pem_x509_certificate(cert_file.read())
        return cert

    def validar_certificado(self, cert_usuario, cert_acs, cert_acr):
        """Validar """
        public_key_acs = cert_acs.public_key()
        # Validar la firma del certificado del usuario con la clave pública de la Autoridad de Certificación Subordinada
        try:
            public_key_acs.verify(
                cert_usuario.signature,
                cert_usuario.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert_usuario.signature_hash_algorithm,
            )
        except cryptography.exceptions.InvalidSignature as e:
            raise ValueError(f"Error al verificar la firma del certificado del usuario: {e}")
        # Validar caducidad del certificado del usuario
        now = datetime.utcnow()
        if not cert_usuario.not_valid_before < now < cert_usuario.not_valid_after:
            raise ValueError("El certificado del usuario ha expirado o aún no es válido.")
        public_key_acr = cert_acr.public_key()
        # Validar la firma del certificado de la ACS con la clave pública de la Autoridad de Certificación Raíz
        try:
            public_key_acr.verify(
                cert_acs.signature,
                cert_acs.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert_acs.signature_hash_algorithm,
            )
        except cryptography.exceptions.InvalidSignature as e:
            raise ValueError(f"Error al verificar la firma del certificado de la ACS: {e}")
        # Validar caducidad del certificado de la ACS
        if not cert_acs.not_valid_before < now < cert_acs.not_valid_after:
            raise ValueError("El certificado de la ACS ha expirado o aún no es válido.")
        # Validar la firma del certificado de la ACR consigo misma
        try:
            public_key_acr.verify(
                cert_acr.signature,
                cert_acr.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert_acr.signature_hash_algorithm,
            )
        except cryptography.exceptions.InvalidSignature as e:
            raise ValueError(f"Error al verificar la firma del certificado de la ACR: {e}")
        # Validar caducidad del certificado de la ACR
        if not cert_acr.not_valid_before < now < cert_acr.not_valid_after:
            raise ValueError("El certificado de la ACR ha expirado o aún no es válido.")
        # Confiamos en la ACR

    def crear_CSR_medico(self, centro_salud, medico):
        """Crea una Solicitud de Firma de Certificado (CSR) para un médico"""
        private_key = self.obtener_clave_privada(medico.private_key_file_name)
        # Generate a CSR
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            # Información del médico y del centro de salud en el que trabaja
            x509.NameAttribute(NameOID.USER_ID, medico.id_medico),
            x509.NameAttribute(NameOID.COMMON_NAME, medico.nombre_completo),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, centro_salud.nombre_centro),
            x509.NameAttribute(NameOID.COUNTRY_NAME, centro_salud.pais),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, centro_salud.provincia),
            x509.NameAttribute(NameOID.LOCALITY_NAME, centro_salud.municipio),
        ])).sign(private_key, hashes.SHA256())       # Firmar la CSR con la clave privada
        return csr

    def crear_CSR_paciente(self, paciente):
        """Crea una Solicitud de Firma de Certificado (CSR) para un paciente"""
        private_key = self.obtener_clave_privada(paciente.private_key_file_name)
        # Generate a CSR
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            # Información del paciente
            x509.NameAttribute(NameOID.USER_ID, paciente.id_paciente),
            x509.NameAttribute(NameOID.COMMON_NAME, paciente.nombre_completo),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
        ])).sign(private_key, hashes.SHA256())       # Firmar la CSR con la clave privada
        return csr

    def solicitar_certificado_medico(self, centro_salud, csr, public_key, cert_file_name):
        """Emitir el certificado de un médico firmado con la clave privada de centro de salud (AC2)"""
        private_key_ac2 = self.obtener_clave_privada(centro_salud.private_key_file_name)
        cert_ac2 = self.obtener_certificado(centro_salud.cert_file_name)
        # Verificar la firma de la CSR con la clave pública del médico, si la firma no coincide lanza una excepción
        public_key.verify(
            csr.signature,
            csr.tbs_certrequest_bytes,
            padding.PKCS1v15(),
            csr.signature_hash_algorithm,
        )
        # Si la firma es correcta emitimos el certificado
        cert = self.crear_certificado(csr.subject, cert_ac2.subject, 365, csr.public_key(), private_key_ac2, cert_file_name)
        return cert

    def solicitar_certificado_paciente(self, csr, public_key, cert_file_name):
        """Emitir el certificado de un paciente firmado con la clave privada de la FNMT (AC3)"""
        private_key_ac3 = self.obtener_clave_privada("fnmt_private_key.pem")
        cert_ac3 = self.obtener_certificado("fnmt_cert.pem")
        # Verificar la firma de la CSR con la clave pública del paciente, si la firma no coincide lanza una excepción
        public_key.verify(
            csr.signature,
            csr.tbs_certrequest_bytes,
            padding.PKCS1v15(),
            csr.signature_hash_algorithm,
        )
        # Si la firma es correcta emitimos el certificado
        cert = self.crear_certificado(csr.subject, cert_ac3.subject, 365, csr.public_key(), private_key_ac3, cert_file_name)
        return cert
