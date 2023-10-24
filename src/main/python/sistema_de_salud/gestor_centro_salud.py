"""GestionCitas"""
import os
import json
import hashlib

from sistema_de_salud.storage.paciente_json_store import PacienteJsonStore
from sistema_de_salud.storage.medico_json_store import MedicoJsonStore
from sistema_de_salud.storage.autenticacion_json_store import AutenticacionJsonStore

from sistema_de_salud.registro_paciente import RegistroPaciente
from sistema_de_salud.registro_medico import RegistroMedico
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#from cryptography.hazmat.primitives.asymmetric import rsa, padding
#from cryptography.hazmat.primitives import serialization


class GestorCentroSalud:
    """Clase que proporciona los métodos para gestionar un Centro de Salud"""
    KEY_LABEL_PACIENTE_ID = "_RegistroPaciente__id_paciente"
    KEY_LABEL_MEDICO_ID = "_RegistroMedico__id_medico"
    KEY_LABEL_USER_ID =   "_AutenticacionUsuario__id_usuario"
    KEY_LABEL_USER_SALT = "_AutenticacionUsuario__salt"
    KEY_LABEL_USER_KEY =  "_AutenticacionUsuario__key"

    def __init__(self):
        pass

    def registro_paciente(self, id_paciente: str, nombre_completo: str, telefono: str, edad: str, password: str) -> str:
        """Registra a un paciente"""
        paciente = RegistroPaciente(id_paciente, nombre_completo, telefono, edad)
        store_pacientes = PacienteJsonStore()
        registro = store_pacientes.guardar_paciente_store(paciente)
        # Solo si el paciente es registrado correctamente (y no estaba registrado antes)
        if registro is True:
            # Derivamos una password segura mediante una KDF (Key Derivation Function)
            salt = os.urandom(16)   # generamos un salt aleatorio, los valores seguros tienen 16 bytes (128 bits) o más
            # Algoritmo de coste variable PBKDF2 (Password Based Key Derivation Function 2)
            # algoritmo: SHA256 ... ; longitud max: 2^32 - 1 ; iteraciones: más iteraciones puede mitigar brute force attacks
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
            # Derivamos la clave criptográfica
            key = kdf.derive(password.encode('utf-8'))      # encode('utf-8') para convertir de string a bytes
            # Convertimos salt y derived key en strings hexadecimales para almacenarlas
            salt_hex = salt.hex()
            key_hex = key.hex()
            # Guardamos la información de autenticación
            usuario = {
                self.KEY_LABEL_USER_ID: id_paciente,
                self.KEY_LABEL_USER_SALT: salt_hex,
                self.KEY_LABEL_USER_KEY: key_hex
            }
            store_credenciales = AutenticacionJsonStore()
            store_credenciales.guardar_credenciales_store(usuario)

        return paciente.id_paciente

    def registro_medico(self, id_medico: str, nombre_completo: str, telefono: str, edad: str, especialidad: str, password: str) -> str:
        """Registra a un médico"""
        medico = RegistroMedico(id_medico, nombre_completo, telefono, edad, especialidad)
        store_medicos = MedicoJsonStore()
        registro_medico = store_medicos.guardar_medico_store(medico)

        # Solo si el paciente es registrado correctamente (y no estaba registrado antes)
        if registro_medico is True:
            # Derivamos una password segura mediante una KDF (Key Derivation Function)
            salt = os.urandom(16)   # generamos un salt aleatorio, los valores seguros tienen 16 bytes (128 bits) o más
            # Algoritmo de coste variable PBKDF2 (Password Based Key Derivation Function 2)
            # algoritmo: SHA256 ... ; longitud max: 2^32 - 1 ; iteraciones: más iteraciones puede mitigar brute force attacks
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
            # Derivamos la clave criptográfica
            key = kdf.derive(password.encode('utf-8'))      # encode('utf-8') para convertir de string a bytes
            # Convertimos salt y derived key en strings hexadecimales para almacenarlas
            salt_hex = salt.hex()
            key_hex = key.hex()
            # Guardamos la información de autenticación
            usuario = {
                self.KEY_LABEL_USER_ID: id_medico,
                self.KEY_LABEL_USER_SALT: salt_hex,
                self.KEY_LABEL_USER_KEY: key_hex
            }
            store_credenciales = AutenticacionJsonStore()
            store_credenciales.guardar_credenciales_store(usuario)

        return medico.id_medico

    def autenticacion_paciente(self, id_paciente: str, password: str):
        """Autentica a un paciente"""
        # Comprobamos que el paciente esté registrado
        store_pacientes = PacienteJsonStore()
        paciente = store_pacientes.buscar_paciente_store(id_paciente)
        if paciente is None:
            return 1
        # Obtenemos el salt y la key del paciente almacenados
        store_credenciales = AutenticacionJsonStore()
        item = store_credenciales.buscar_credenciales_store(paciente[self.KEY_LABEL_PACIENTE_ID])
        stored_salt_hex = item[self.KEY_LABEL_USER_SALT]
        stored_key_hex = item[self.KEY_LABEL_USER_KEY]
        # Convertimos el salt a bytes
        stored_salt = bytes.fromhex(stored_salt_hex)
        print("Stored salt:", stored_salt_hex)
        print("Stored key   :", stored_key_hex)
        # Derivamos la clave a partir del password introducido por el usuario
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=stored_salt, iterations=480000)
        key = kdf.derive(password.encode('utf-8'))
        # Convertimos la key a hexadecimal y comparamos con la key almacenada
        key_hex = key.hex()
        print("Generated key:", key_hex)
        if key_hex != stored_key_hex:
            print("Contraseña incorrecta")
            return 2

        return 0

    def autenticacion_medico(self, id_medico: str, password: str):
        """Autentica a un medico"""
        # Comprobamos que el medico esté registrado
        store_medicos = MedicoJsonStore()
        medico = store_medicos.buscar_medico_store(id_medico)
        if medico is None:
            return 1
        # Obtenemos el salt y la key del medico almacenados
        store_credenciales = AutenticacionJsonStore()
        item = store_credenciales.buscar_credenciales_store(medico[self.KEY_LABEL_MEDICO_ID])
        stored_salt_hex = item[self.KEY_LABEL_USER_SALT]
        stored_key_hex = item[self.KEY_LABEL_USER_KEY]
        # Convertimos el salt a bytes
        stored_salt = bytes.fromhex(stored_salt_hex)
        print("Stored salt:", stored_salt_hex)
        print("Stored key   :", stored_key_hex)
        # Derivamos la clave a partir del password introducido por el usuario
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=stored_salt, iterations=480000)
        key = kdf.derive(password.encode('utf-8'))
        # Convertimos la key a hexadecimal y comparamos con la key almacenada
        key_hex = key.hex()
        print("Generated key:", key_hex)
        if key_hex != stored_key_hex:
            print("Contraseña incorrecta")
            return 2

        return 0

    def autenticacion_usuarios(self):
        """Interfaz de autenticación de usuarios"""
        print("\nINICIO DE SESIÓN\n")
        id_usuario = input("Introduzca su ID de usuario: ")
        for i in range(3):
            password = input("Introduzca su contraseña: ")
            autenticacion = self.autenticacion_paciente(id_usuario, password)
            if autenticacion == 1:
                # usuario no registrado
                print("\nInicio de sesión fallido. Saliendo del programa...")
                exit()
            elif autenticacion == 2:
                # usuario registrado, contraseña incorrecta
                continue
            else:
                print("Autenticación exitosa")
                return
        print("\nInicio de sesión fallido. Saliendo del programa...")
        exit()

    def autenticacion_medicos(self):
        """Interfaz de autenticación de medicos"""
        print("\nINICIO DE SESIÓN\n")
        id_usuario = input("Introduzca su ID de usuario: ")
        for i in range(3):
            password = input("Introduzca su contraseña: ")
            autenticacion = self.autenticacion_medico(id_usuario, password)
            if autenticacion == 1:
                # usuario no registrado
                print("\nInicio de sesión fallido. Saliendo del programa...")
                exit()
            elif autenticacion == 2:
                # usuario registrado, contraseña incorrecta
                continue
            else:
                print("Autenticación exitosa")
                return
        print("\nInicio de sesión fallido. Saliendo del programa...")
        exit()


    def main(self):
        """Función Principal"""
        # Preparación del programa, borrar stores
        store = JSON_FILES_PATH + "store_pacientes.json"
        if os.path.isfile(store):
            os.remove(store)
        store = JSON_FILES_PATH + "store_medicos.json"
        if os.path.isfile(store):
            os.remove(store)
        store = JSON_FILES_PATH + "store_credenciales.json"
        if os.path.isfile(store):
            os.remove(store)

        # Registrar paciente
        id_paciente = self.registro_paciente("54126179V", "Lorenzo Largacha Sanz", "+34111555888", "22", "12345ABC")
        # Registrar médico
        id_medico = self.registro_medico("62108856Y", "Manuel Fernandez Gil", "+34222444777", "53", "Medicina General", "1234asdf")

        # PRUEBAS
        # Buscar password de un paciente
        #store_credenciales = AutenticacionJsonStore()
        #item = store_credenciales.buscar_credenciales_store(id_paciente)
        #print(item[self.KEY_LABEL_USER_KEY])
        # Intento volver a registrar al mismo paciente
        #id_paciente = self.registro_paciente("54126179V", "Lorenzo Largacha Sanz", "+34111555888", "22", "12345ABC")
        #print(id_paciente)
        # Intento buscar un paciente que no existe
        #store_pacientes = PacienteJsonStore()
        #paciente_buscado = store_pacientes.buscar_paciente_store("54126179K")
        #print(paciente_buscado)
        # Autenticar los datos de un paciente
        #self.autenticacion_paciente("54126179V", "12345ABC")
        # Intento autenticar los datos de un paciente con una contraseña incorrecta
        #self.autenticacion_paciente("54126179V", "12345CCC")

        print("\n\n--- Bienvenido al sistema de gestión del Centro de Salud ---")
        tipo = input("\n ¿Es usted paciente o médico? ")
        if tipo == "paciente":
            self.autenticacion_usuarios()

            # Interfaz paciente
            print("\nINTERFAZ PACIENTE")
            while True:
                print("\nOpciones disponibles:")
                print("1. Pedir cita")
                print("2. Anular cita")
                print("3. Consultar mis citas")
                print("4. Salir")
                opcion = input("Indique una opción (1/2/3/4): ")

                if opcion == "1":
                    #pedir_cita()
                    break
                elif opcion == "2":
                    #anular_cita()
                    break
                elif opcion == "3":
                    #consultar_citas()
                    break
                elif opcion == "4":
                    print("\nSaliendo del programa...")
                    break
                else:
                    print("Opción no válida. Inténtelo de nuevo.")

        if tipo == "médico":
            self.autenticacion_medicos()

            # Interfaz paciente
            print("\nINTERFAZ MÉDICO")
            while True:
                print("\nOpciones disponibles:")
                print("1. Consultar mis citas")
                print("2. Salir")
                opcion = input("Indique una opción (1/2): ")

                if opcion == "1":
                    # pedir_cita()
                    break
                elif opcion == "2":
                    print("\nSaliendo del programa...")
                    break
                else:
                    print("Opción no válida. Inténtelo de nuevo.")


if __name__ == "__main__":
    gestor_centro_salud = GestorCentroSalud()
    gestor_centro_salud.main()


################################## version con crifrado RSA ######################
"""
usuarios = {
    "usuario1": {
        "clave_privada": None,
        "clave_publica": None,
        "imagen_referencia": None,
        "contraseña": "contraseña1"  # Contraseña de ejemplo
    },
    "usuario2": {
        "clave_privada": None,
        "clave_publica": None,
        "imagen_referencia": None,
        "contraseña": "contraseña2"  # Contraseña de ejemplo
    },
    "usuario3": {
        "clave_privada": None,
        "clave_publica": None,
        "imagen_referencia": None,
        "contraseña": "contraseña3"  # Contraseña de ejemplo
    }
}

# Base de datos de citas (puedes expandirla según tus necesidades)
citas = {}


# Función para generar un par de claves RSA para un usuario
def generar_claves_rsa(usuario):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    usuario["clave_privada"] = private_key
    usuario["clave_publica"] = private_key.public_key()


# Función para cifrar datos utilizando la clave pública
def cifrar_datos(clave_publica, datos):
    datos_cifrados = clave_publica.encrypt(
        datos.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return datos_cifrados


# Función para descifrar datos utilizando la clave privada
def descifrar_datos(clave_privada, datos_cifrados):
    datos_descifrados = clave_privada.decrypt(
        datos_cifrados,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()
    return datos_descifrados


# Función para verificar las credenciales de usuario (reconocimiento facial o contraseña)
def verificar_credenciales():
    usuario = input("Ingrese su nombre de usuario: ")

    # Verificar si el usuario tiene una imagen de referencia para el reconocimiento facial
    if usuarios.get(usuario) and usuarios[usuario]["imagen_referencia"]:
        return autenticar_reconocimiento_facial(usuario)
    else:
        return autenticar_contrasena(usuario)


# Función para autenticar al usuario mediante reconocimiento facial
def autenticar_reconocimiento_facial(usuario):
    imagen_referencia = usuarios[usuario]["imagen_referencia"]

    # Capturar una imagen del usuario para el reconocimiento facial (simplificado)
    # En una implementación real, deberías utilizar bibliotecas como OpenCV o dlib.
    imagen_capturada = input("Capture su imagen para el reconocimiento facial (ruta de la imagen): ")

    # Calcular el hash de ambas imágenes y compararlos
    hash_referencia = hashlib.sha256(open(imagen_referencia, "rb").read()).hexdigest()
    hash_capturada = hashlib.sha256(open(imagen_capturada, "rb").read()).hexdigest()

    if hash_referencia == hash_capturada:
        print("Reconocimiento facial exitoso. Bienvenido.")
        return True
    else:
        print("Reconocimiento facial fallido. Ingrese su contraseña.")
        return autenticar_contrasena(usuario)


# Función para autenticar al usuario mediante contraseña
def autenticar_contrasena(usuario):
    contraseña = input("Ingrese su contraseña: ")
    if usuarios.get(usuario) and usuarios[usuario]["contraseña"] == contraseña:
        print("Contraseña correcta. Bienvenido.")
        return True
    else:
        print("Contraseña incorrecta. Autenticación fallida.")
        return False


# Función principal
def main():
    print("Bienvenido al sistema de citas.")

    # Verificar credenciales y generar claves RSA si es necesario
    usuario = input("Ingrese su nombre de usuario: ")
    if usuario not in usuarios:
        print("Usuario no encontrado. Saliendo del programa.")
        return

    if usuarios[usuario]["clave_privada"] is None:
        print("Generando claves RSA para el usuario...")
        generar_claves_rsa(usuarios[usuario])
        print("Claves generadas con éxito.")

    while True:
        print("\nOpciones disponibles:")
        print("1. Pedir cita")
        print("2. Anular cita")
        print("3. Consultar citas")
        print("4. Salir")
        opcion = input("Seleccione una opción (1/2/3/4): ")

        if opcion == "1":
            pedir_cita()
        elif opcion == "2":
            anular_cita()
        elif opcion == "3":
            consultar_citas()
        elif opcion == "4":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Intente nuevamente.")


# Función para pedir una cita
def pedir_cita():
    nombre_usuario = input("Ingrese su nombre de usuario: ")
    fecha = input("Ingrese la fecha de la cita (formato dd/mm/yyyy): ")
    hora = input("Ingrese la hora de la cita (formato hh:mm): ")

    # Cifrar los detalles de la cita con la clave pública del usuario
    clave_publica = usuarios[nombre_usuario]["clave_publica"]
    datos_cifrados = cifrar_datos(clave_publica, f"Fecha: {fecha}, Hora: {hora}")

    # Almacenar la cita cifrada en la base de datos de citas
    citas[(nombre_usuario, fecha, hora)] = datos_cifrados
    print("Cita programada con éxito.")


# Función para anular una cita
def anular_cita():
    nombre_usuario = input("Ingrese su nombre de usuario: ")
    fecha = input("Ingrese la fecha de la cita que desea anular (formato dd/mm/yyyy): ")
    hora = input("Ingrese la hora de la cita que desea anular (formato hh:mm): ")

    # Verificar si la cita existe
    if (nombre_usuario, fecha, hora) in citas:
        # Descifrar los detalles de la cita con la clave privada del usuario
        clave_privada = usuarios[nombre_usuario]["clave_privada"]
        datos_cifrados = citas[(nombre_usuario, fecha, hora)]
        datos_descifrados = descifrar_datos(clave_privada, datos_cifrados)

        # Mostrar los detalles de la cita
        print(f"Detalles de la cita:\n{datos_descifrados}")

        # Eliminar la cita de la base de datos
        del citas[(nombre_usuario, fecha, hora)]
        print("Cita anulada con éxito.")
    else:
        print("No se encontró ninguna cita para anular.")


# Función para consultar citas
def consultar_citas():
    nombre_usuario = input("Ingrese su nombre de usuario: ")
    print("Sus citas programadas:")
    for cita, datos_cifrados in citas.items():
        if cita[0] == nombre_usuario:
            # Descifrar los detalles de la cita con la clave privada del usuario
            clave_privada = usuarios[nombre_usuario]["clave_privada"]
            datos_descifrados = descifrar_datos(clave_privada, datos_cifrados)
            print(f"Fecha: {cita[1]}, Hora: {cita[2]}\n{datos_descifrados}")

if __name__ == "__main__":
    main()
"""
