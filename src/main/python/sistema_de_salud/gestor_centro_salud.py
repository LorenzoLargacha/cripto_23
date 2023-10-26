"""GestionCitas"""
import os
import json
from datetime import datetime

from sistema_de_salud.storage.paciente_json_store import PacienteJsonStore
from sistema_de_salud.storage.medico_json_store import MedicoJsonStore
from sistema_de_salud.storage.autenticacion_json_store import AutenticacionJsonStore
from sistema_de_salud.storage.cita_json_store import CitaJsonStore

from sistema_de_salud.registro_paciente import RegistroPaciente
from sistema_de_salud.registro_medico import RegistroMedico
from sistema_de_salud.cita_medica import CitaMedica
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


class GestorCentroSalud:
    """Clase que proporciona los métodos para gestionar un Centro de Salud"""
    KEY_LABEL_PACIENTE_ID = "_RegistroPaciente__id_paciente"
    KEY_LABEL_MEDICO_ID =   "_RegistroMedico__id_medico"
    KEY_LABEL_USER_ID =     "_AutenticacionUsuario__id_usuario"
    KEY_LABEL_USER_SALT =   "_AutenticacionUsuario__salt"
    KEY_LABEL_USER_KEY =    "_AutenticacionUsuario__key"
    KEY_LABEL_CITA_ID =     "_CitaMedica__identificador_cita"
    KEY_LABEL_CITA_FECHA =  "_CitaMedica__fecha_hora"
    KEY_LABEL_CITA_PACIENTE = "_CitaMedica__id_paciente"
    KEY_LABEL_CITA_MOTIVO = "_CitaMedica__motivo_consulta"

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

    def registro_cita(self, id_medico: str, especialidad: str, fecha_hora, id_paciente: str, telefono_paciente: str, motivo_consulta: str):
        """Registra una cita médica"""
        cita = CitaMedica(id_medico, especialidad, fecha_hora, id_paciente, telefono_paciente, motivo_consulta)

        # Cifrado simétrico
        print("\nGenerando clave simétrica...")
        key = Fernet.generate_key()
        # ** Asumimos que la clave se transmite entre paciente y médico mediante un sistema asimétrico **
        # Encriptamos la cita con Fernet
        print("Encriptando cita...")
        f = Fernet(key)
        bytes_data = json.dumps(cita.__dict__).encode('utf-8')  # serializamos la cita como un string y lo convertimos a bytes
        token = f.encrypt(bytes_data)                           # obtenemos los datos encriptados como un token
        # Enviamos la cita encriptada al médico
        print("Enviando cita al médico...")
        confirmacion_encriptada = self.enviar_cita(token, key, id_medico)
        # Recibimos la confirmación y la desencriptamos
        cita_confirmada = self.recibir_confirmacion(confirmacion_encriptada, key, id_paciente)
        if cita_confirmada is True:
            store_citas = CitaJsonStore()
            store_citas.guardar_cita_store(cita)
        return cita

    def enviar_cita(self, token, key, id_medico):
        """Envía una cita de un paciente al médico"""
        # Desencriptamos la cita con Fernet
        print("Desencriptando cita...")
        f = Fernet(key)
        bytes_data = f.decrypt(token)
        cita_dict = json.loads(bytes_data.decode('utf-8'))
        # Guardamos la información de la cita en la lista mis_citas del médico
        medico = RegistroMedico.obtener_medico(id_medico)
        identificador_cita = cita_dict[self.KEY_LABEL_CITA_ID]
        info_cita = {
            self.KEY_LABEL_CITA_ID: identificador_cita,
            self.KEY_LABEL_CITA_FECHA: cita_dict[self.KEY_LABEL_CITA_FECHA],
            self.KEY_LABEL_CITA_PACIENTE: cita_dict[self.KEY_LABEL_CITA_PACIENTE],
            self.KEY_LABEL_CITA_MOTIVO: cita_dict[self.KEY_LABEL_CITA_MOTIVO]
        }
        medico.registrar_cita_medico(info_cita)
        # Actualizamos el médico en el fichero JSON
        store_medicos = MedicoJsonStore()
        store_medicos.update_item(medico, medico.id_medico)
        # Encriptamos la confirmación
        print("Encriptando confirmación...")
        confirmacion_encriptada = f.encrypt(identificador_cita.encode('utf-8'))
        # Devolvemos la confirmación
        print("Devolviendo confirmación al paciente...")
        return confirmacion_encriptada

    def recibir_confirmacion(self, token, key, id_paciente):
        """Recibe la confirmación de la cita del médico"""
        # Desencriptamos la confirmación con Fernet
        print("Desencriptando confirmación...")
        f = Fernet(key)
        bytes_data = f.decrypt(token)
        identificador_cita = bytes_data.decode('utf-8')
        # Guardamos el identificador de la cita en la lista mis_citas del paciente
        paciente = RegistroPaciente.obtener_paciente(id_paciente)
        paciente.registrar_cita_paciente(identificador_cita)
        # Actualizamos el paciente en el fichero JSON
        store_pacientes = PacienteJsonStore()
        store_pacientes.update_item(paciente, paciente.id_paciente)
        return True

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
            print("Contraseña incorrecta\n")
            return 2
        return 0

    def autenticacion_medico(self, id_medico: str, password: str):
        """Autentica a un médico"""
        # Comprobamos que el médico esté registrado
        store_medicos = MedicoJsonStore()
        medico = store_medicos.buscar_medico_store(id_medico)
        if medico is None:
            return 1
        # Obtenemos el salt y la key del médico almacenados
        store_credenciales = AutenticacionJsonStore()
        item = store_credenciales.buscar_credenciales_store(medico[self.KEY_LABEL_MEDICO_ID])
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
            print("Contraseña incorrecta\n")
            return 2
        return 0

    def autenticacion_usuarios(self, tipo_usuario: str):
        """Interfaz de autenticación de usuarios"""
        print("\nINICIO DE SESIÓN\n")
        for i in range(3):
            id_usuario = input("Introduzca su ID de usuario: ")
            password = input("Introduzca su contraseña: ")
            if tipo_usuario == "paciente":
                autenticacion = self.autenticacion_paciente(id_usuario, password)
            elif tipo_usuario == "medico":
                autenticacion = self.autenticacion_medico(id_usuario, password)

            if autenticacion == 1:
                # usuario no registrado
                print("\nInicio de sesión fallido. Volviendo al inicio...")
                return None
            elif autenticacion == 2:
                # usuario registrado, contraseña incorrecta
                continue
            else:
                print("Autenticación exitosa\n")
                if tipo_usuario == "paciente":
                    usuario = RegistroPaciente.obtener_paciente(id_usuario)
                elif tipo_usuario == "medico":
                    usuario = RegistroMedico.obtener_medico(id_usuario)
                return usuario
        print("Inicio de sesión fallido. Volviendo al inicio...")
        return None

    def pedir_cita(self, paciente: RegistroPaciente):
        """Solicitar una cita médica"""
        print("\nSOLICITUD CITA")
        while True:
            cancelar = False
            print("\nCon qué médico desea pedir cita:")
            print("1. Manuel Fernandez Gil - Atención Primaria")
            print("2. Isabel Gómez Rivas - Pediatría")
            print("3. Juan Martín Pérez - Odontología")
            print("4. Candela Martínez Sanchéz - Matrona")
            print("5. Cancelar")
            opcion = input("Indique una opción (1/2/3/4...): ")

            if opcion == "1":
                id_medico = "76281872A"
            elif opcion == "2":
                id_medico = "84202258V"
            elif opcion == "3":
                id_medico = "92213124Y"
            elif opcion == "4":
                id_medico = "67720890N"
            elif opcion == "5":
                print("\nCancelando solicitud...")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")
                continue

            while True:
                cambiarMedico = False
                medico = RegistroMedico.obtener_medico(id_medico)

                fecha_str = input("\nIntroduzca una fecha (YYYY-MM-DD): ")
                fecha_hora_str = fecha_str + " " + "00:00:00"

                # Mostrar citas ocupadas para ese médico en esa fecha
                store_citas = CitaJsonStore()
                lista_citas = store_citas.buscar_citas_medico_fecha_store(medico.id_medico, fecha_hora_str)
                if lista_citas:
                    print("\nHoras ocupadas para la fecha introducida: ")
                    for item in lista_citas:
                        print(item["_CitaMedica__fecha_hora"] + " - " + medico.nombre_completo + " - " + item["_CitaMedica__especialidad"] + " -> Ocupado")
                print("\nTodas las horas estás libres para la fecha introducida ")
                hora_str = input("\nIntroduzca una hora libre (HH:MM): ")
                fecha_hora_str = fecha_str + " " + hora_str + ":00"  # YYYY-MM-DD HH:MM:SS

                # Consultar si la fecha_hora introducida está libre
                item = store_citas.buscar_cita_fecha_hora_store(fecha_hora_str)
                if item is None:
                    # Convert the string to a datetime object
                    fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
                    motivo_consulta = input("\nIntroduzca el motivo de la consulta: ")
                    # Iniciamos el registro de la cita
                    cita = self.registro_cita(medico.id_medico, medico.especialidad, fecha_hora, paciente.id_paciente, paciente.telefono, motivo_consulta)
                    print("\nCita reservada con éxito")
                    print(cita.mostrar_info_publica())
                    return

                # Si la fecha no está libre
                print("\nCita no disponible\n")
                while True:
                    print("1. Cambiar fecha")
                    print("2. Cambiar médico")
                    print("3. Cancelar")
                    opcion = input("Indique una opción (1/2/3): ")
                    if opcion == "1":
                        break
                    elif opcion == "2":
                        cambiarMedico = True
                        break
                    elif opcion == "3":
                        cambiarMedico = True
                        cancelar = True
                        print("\nCancelando solicitud...")
                        break
                    else:
                        print("Opción no válida. Inténtelo de nuevo.")
                        continue
                    break
                if cambiarMedico is True:
                    break
            if cancelar is True:
                break
        return

    def interfaz_paciente(self, paciente: RegistroPaciente):
        # Interfaz paciente
        print("\nINTERFAZ PACIENTE")
        while True:
            print("\nOpciones disponibles:")
            print("1. Pedir cita")
            print("2. Anular cita")
            print("3. Consultar mis citas")
            print("4. Cerrar sesión")
            opcion = input("Indique una opción (1/2/3/4): ")

            if opcion == "1":
                self.pedir_cita(paciente)
                print("\nINTERFAZ PACIENTE")
                continue
            elif opcion == "2":
                # anular_cita(paciente)
                continue
            elif opcion == "3":
                # consultar_citas(paciente)
                continue
            elif opcion == "4":
                print("\nCerrando sesión...")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")

    def interfaz_medico(self, medico: object):
        # Interfaz medico
        print("\nINTERFAZ MÉDICO")
        while True:
            print("\nOpciones disponibles:")
            print("1. Consultar mis citas")
            print("2. Cerrar sesión")
            opcion = input("Indique una opción (1/2): ")

            if opcion == "1":
                # consultar citas
                continue
            elif opcion == "2":
                print("\nCerrando sesión...")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")

    def main(self):
        """Función Principal"""
        # Preparación del programa
        # Borrar stores
        store = JSON_FILES_PATH + "store_pacientes.json"
        if os.path.isfile(store):
            os.remove(store)
        store = JSON_FILES_PATH + "store_medicos.json"
        if os.path.isfile(store):
            os.remove(store)
        store = JSON_FILES_PATH + "store_credenciales.json"
        if os.path.isfile(store):
            os.remove(store)
        store = JSON_FILES_PATH + "store_citas.json"
        if os.path.isfile(store):
            os.remove(store)

        # Registrar pacientes
        self.registro_paciente("54026189V", "Lorenzo Largacha Sanz", "+34666888166", "22", "12345ABC")
        self.registro_paciente("58849111T", "Pedro Hernandez Bernaldo", "+34111555888", "22", "12345ABC")
        # Registrar médicos
        self.registro_medico("76281872A", "Manuel Fernandez Gil", "+34222444777", "51", "Atencion Primaria", "1234asdf")
        self.registro_medico("84202258V", "Isabel Gomez Rivas", "+34333444666", "42", "Pediatria", "1234asdf")
        self.registro_medico("92213124Y", "Juan Martin Perez", "+34555444222", "36", "Odontologia", "1234asdf")
        self.registro_medico("67720890N", "Candela Martinez Sanchez", "+34888444111", "38", "Matrona", "1234asdf")
        # Registrar cita
        fecha_hora = datetime(2023, 10, 31, 14, 30)
        self.registro_cita("76281872A", "Atencion Primaria", fecha_hora, "54026189V", "+34666888166", "Dolor de cabeza")

        # Menu de inicio
        while True:
            print("\n\n--- Bienvenido al sistema de gestión del Centro de Salud ---")
            print("\nOpciones disponibles:")
            print("1. Acceso Pacientes")
            print("2. Acceso Médicos")
            print("3. Acceso Administrador")
            print("4. Salir del sistema")
            opcion = input("Indique una opción (1/2/3/4): ")

            tipo_usuario = ""
            if opcion == "1":
                tipo_usuario = "paciente"
                usuario = self.autenticacion_usuarios(tipo_usuario)
                if usuario is None:
                    continue
                self.interfaz_paciente(usuario)
            elif opcion == "2":
                tipo_usuario = "medico"
                usuario = self.autenticacion_usuarios(tipo_usuario)
                if usuario is None:
                    continue
                self.interfaz_medico(usuario)
            elif opcion == "3":
                # Acceso Administrador
                break
            elif opcion == "4":
                print("\nSaliendo del sistema...")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")


if __name__ == "__main__":
    gestor_centro_salud = GestorCentroSalud()
    gestor_centro_salud.main()
