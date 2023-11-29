"""GestorCentroSalud"""
import os
import json
from datetime import datetime

from sistema_de_salud.storage.paciente_json_store import PacienteJsonStore
from sistema_de_salud.storage.medico_json_store import MedicoJsonStore
from sistema_de_salud.storage.cita_json_store import CitaJsonStore

from sistema_de_salud.registro_paciente import RegistroPaciente
from sistema_de_salud.registro_medico import RegistroMedico
from sistema_de_salud.cita_medica import CitaMedica
from sistema_de_salud.criptografia import Criptografia
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH

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
    KEY_LABEL_CITA_MEDICO = "_CitaMedica__id_medico"
    KEY_LABEL_CITA_ESPECIALIDAD = "_CitaMedica__especialidad"

    def __init__(self):
        # Creamos los atributos
        self.__id_centro = "2625"   # Código de centro
        self.__nombre_centro = "Valle de la Oliva"
        self.__pais = "ES"
        self.__provincia = "Madrid"
        self.__municipio = "Majadahonda"
        self.__autoridad_raiz = "ministerioSanidad"
        self.__private_key_file_name = self.__id_centro + "_private_key.pem"
        self.__public_key_file_name = self.__id_centro + "_public_key.pem"
        self.__cert_file_name = self.__id_centro + "_cert.pem"

    @property
    def id_centro(self):
        """Read-only property que devuelve el ID del centro de salud"""
        return self.__id_centro

    @property
    def nombre_centro(self):
        """Read-only property que devuelve el nombre del centro de salud"""
        return self.__nombre_centro

    @property
    def pais(self):
        """Read-only property que devuelve el país del centro de salud"""
        return self.__pais
    @property
    def provincia(self):
        """Read-only property que devuelve la provincia del centro de salud"""
        return self.__provincia

    @property
    def municipio(self):
        """Read-only property que devuelve el municipio del centro de salud"""
        return self.__municipio

    @property
    def autoridad_raiz(self):
        """Read-only property que devuelve el nombre de la autoridad superior al centro de salud"""
        return self.__autoridad_raiz

    @property
    def private_key_file_name(self):
        """Read-only property que devuelve el nombre del fichero de la private_key del centro de salud"""
        return self.__private_key_file_name

    @property
    def public_key_file_name(self):
        """Read-only property que devuelve el nombre del fichero de la public_key del centro de salud"""
        return self.__public_key_file_name

    @property
    def cert_file_name(self):
        """Read-only property que devuelve el nombre del fichero del certificado del centro de salud"""
        return self.__cert_file_name

    def registro_paciente(self, id_paciente: str, nombre_completo: str, telefono: str, edad: str, password: str) -> str:
        """Registra a un paciente"""
        paciente = RegistroPaciente(id_paciente, nombre_completo, telefono, edad)
        store_pacientes = PacienteJsonStore()
        registro = store_pacientes.guardar_paciente_store(paciente)
        # Solo si el paciente es registrado correctamente (y no estaba registrado antes)
        if registro is True:
            criptografia = Criptografia()
            # Derivamos una password segura mediante una KDF y la almacenamos
            criptografia.guardar_password(id_paciente, password)
            # Generamos una pareja de claves con RSA para el paciente
            criptografia.generar_claves_RSA(paciente.private_key_file_name, paciente.public_key_file_name)
            # Crear una Solicitud de Firma de Certificado (CSR) para el paciente
            csr = criptografia.crear_CSR_paciente(paciente)
            # Solicitamos el certificado del paciente a la FNMT (AC3)
            private_key = criptografia.obtener_clave_privada(paciente.private_key_file_name)
            public_key = private_key.public_key()
            criptografia.solicitar_certificado_paciente(csr, public_key, paciente.cert_file_name)
        return paciente.id_paciente

    def registro_medico(self, id_medico: str, nombre_completo: str, telefono: str, edad: str, especialidad: str, password: str) -> str:
        """Registra a un médico"""
        medico = RegistroMedico(id_medico, nombre_completo, telefono, edad, especialidad)
        store_medicos = MedicoJsonStore()
        registro = store_medicos.guardar_medico_store(medico)
        # Solo si el médico es registrado correctamente (y no estaba registrado antes)
        if registro is True:
            criptografia = Criptografia()
            # Derivamos una password segura mediante una KDF y la almacenamos
            criptografia.guardar_password(id_medico, password)
            # Generamos una pareja de claves con RSA para el médico
            criptografia.generar_claves_RSA(medico.private_key_file_name, medico.public_key_file_name)
            # Crear una Solicitud de Firma de Certificado (CSR) para el médico
            csr = criptografia.crear_CSR_medico(self, medico)
            # Solicitamos el certificado del médico al centro de salud (AC2)
            private_key = criptografia.obtener_clave_privada(medico.private_key_file_name)
            public_key = private_key.public_key()
            criptografia.solicitar_certificado_medico(self, csr, public_key, medico.cert_file_name)
        return medico.id_medico

    def registro_cita(self, id_medico: str, especialidad: str, fecha_hora, id_paciente: str, telefono_paciente: str, motivo_consulta: str):
        """Registra una cita médica"""
        cita = CitaMedica(id_medico, especialidad, fecha_hora, id_paciente, telefono_paciente, motivo_consulta)

        # Cifrado simétrico
        print("\nGenerando clave simétrica...")
        key = Fernet.generate_key()
        # ** Asumimos que la clave se transmite entre paciente y médico mediante un sistema asimétrico **

        # Serializamos la cita como un string y lo convertimos a bytes
        bytes_data = json.dumps(cita.__dict__).encode('utf-8')
        # Firmamos la cita con la clave privada del paciente
        criptografia = Criptografia()
        paciente = RegistroPaciente.obtener_paciente(id_paciente)
        firma = criptografia.firmar_mensaje(bytes_data, paciente.private_key_file_name)
        # Encriptamos la cita con Fernet
        print("Encriptando cita...")
        f = Fernet(key)
        token = f.encrypt(bytes_data)                           # obtenemos los datos encriptados como un token
        # Enviamos la cita encriptada al médico
        print("Enviando cita al médico...")
        public_key_paciente = criptografia.obtener_clave_publica(paciente.public_key_file_name)
        confirmacion_encriptada, signature, public_key_medico = self.enviar_cita(token, key, id_medico, firma, public_key_paciente)
        # Recibimos la confirmación y la desencriptamos
        id_cita_confirmada = self.recibir_confirmacion(confirmacion_encriptada, key, id_paciente, signature, public_key_medico)
        if id_cita_confirmada == cita.identificador_cita:
            # Guardamos la información de la cita en la lista mis_citas del paciente
            paciente = RegistroPaciente.obtener_paciente(id_paciente)
            info_cita = {
                self.KEY_LABEL_CITA_ID: cita.identificador_cita,
                self.KEY_LABEL_CITA_FECHA: cita.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                self.KEY_LABEL_CITA_MEDICO: cita.id_medico,
                self.KEY_LABEL_CITA_ESPECIALIDAD: cita.especialidad
            }
            paciente.registrar_cita_paciente(info_cita)
            # Actualizamos el paciente en el fichero JSON
            store_pacientes = PacienteJsonStore()
            store_pacientes.update_item(paciente, paciente.id_paciente)
            # Guardamos la cita en el fichero store_citas
            store_citas = CitaJsonStore()
            store_citas.guardar_cita_store(cita)
        return cita

    def enviar_cita(self, token, key, id_medico, firma, public_key_paciente):
        """Envía una solicitud de cita del paciente al médico"""
        # Desencriptamos la cita con Fernet
        print("Desencriptando cita...")
        f = Fernet(key)
        bytes_data = f.decrypt(token)
        # Comprobamos la firma de la cita
        criptografia = Criptografia()
        criptografia.comprobar_firma(bytes_data, firma, public_key_paciente)
        # Guardamos la información de la cita en la lista mis_citas del médico
        cita_dict = json.loads(bytes_data.decode('utf-8'))
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
        # Firmamos la confirmación de la cita con la clave privada del médico
        confirmacion = identificador_cita.encode('utf-8')
        firma = criptografia.firmar_mensaje(confirmacion, medico.private_key_file_name)
        # Encriptamos la confirmación
        print("Encriptando confirmación...")
        confirmacion_encriptada = f.encrypt(confirmacion)
        # Devolvemos la confirmación
        print("Devolviendo confirmación al paciente...")
        public_key_medico = criptografia.obtener_clave_publica(medico.public_key_file_name)
        return confirmacion_encriptada, firma, public_key_medico

    def recibir_confirmacion(self, token, key, id_paciente, firma, public_key_medico):
        """Recibe la confirmación de la cita del médico"""
        # Desencriptamos la confirmación con Fernet
        print("Desencriptando confirmación...")
        f = Fernet(key)
        bytes_data = f.decrypt(token)
        # Comprobamos la firma de la cita
        criptografia = Criptografia()
        criptografia.comprobar_firma(bytes_data, firma, public_key_medico)
        identificador_cita = bytes_data.decode('utf-8')
        return identificador_cita

    def autenticacion_paciente(self, id_paciente: str, password: str):
        """Autentica a un paciente"""
        # Comprobamos que el paciente esté registrado
        store_pacientes = PacienteJsonStore()
        paciente = store_pacientes.buscar_paciente_store(id_paciente)
        if paciente is None:
            return 1
        criptografia = Criptografia()
        if criptografia.comprobar_password(paciente[self.KEY_LABEL_PACIENTE_ID], password) is False:
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
        criptografia = Criptografia()
        if criptografia.comprobar_password(medico[self.KEY_LABEL_MEDICO_ID], password) is False:
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

    def pedir_cita(self, id_paciente: str):
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
                lista_citas = store_citas.buscar_citas_activas_medico_fecha_store(medico.id_medico, fecha_hora_str)
                if lista_citas:
                    print("\nHoras ocupadas para la fecha introducida: ")
                    for item in lista_citas:
                        print(item["_CitaMedica__fecha_hora"] + " - " + medico.nombre_completo + " - " + item["_CitaMedica__especialidad"] + " -> Ocupado")
                else:
                    print("\nTodas las horas están libres para la fecha introducida ")
                hora_str = input("\nIntroduzca una hora disponible (HH:MM): ")
                fecha_hora_str = fecha_str + " " + hora_str + ":00"  # YYYY-MM-DD HH:MM:SS

                # Consultar si la fecha_hora introducida está libre
                item = store_citas.buscar_citas_activas_medico_fecha_hora_store(medico.id_medico, fecha_hora_str)
                if not item:
                    # Convert the string to a datetime object
                    fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
                    motivo_consulta = input("\nIntroduzca el motivo de la consulta: ")
                    # Iniciamos el registro de la cita
                    paciente = RegistroPaciente.obtener_paciente(id_paciente)
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

    def cancelar_cita(self, id_paciente: str):
        """Cancelar una cita médica"""
        print("\nDatos de la cita que quiere cancelar:\n")
        # Obtenemos la fecha_hora de la cita a borrar
        fecha_str = input("\nIntroduzca la fecha su cita (YYYY-MM-DD): ")
        hora_str = input("Introduzca la hora de su cita (HH:MM): ")
        fecha_hora_str = fecha_str + " " + hora_str + ":00"  # YYYY-MM-DD HH:MM:SS
        # Buscamos la cita en mis_citas del paciente y la borramos
        paciente = RegistroPaciente.obtener_paciente(id_paciente)
        lista_citas_paciente = paciente.mis_citas
        cita_dict = None
        for item in lista_citas_paciente:
            if item[self.KEY_LABEL_CITA_FECHA] == fecha_hora_str:
                cita_dict = item
                break
        if cita_dict is None:
            print("\nCita no encontrada")
            return
        identificador_cita = cita_dict[self.KEY_LABEL_CITA_ID]
        id_medico = cita_dict[self.KEY_LABEL_CITA_MEDICO]
        paciente.borrar_cita_paciente(cita_dict)
        # Actualizamos el paciente en el fichero JSON
        paciente.actualizar_paciente_store()

        # Buscamos la cita en mis_citas del médico y la borramos
        medico = RegistroMedico.obtener_medico(id_medico)
        lista_citas_medico = medico.mis_citas
        for item in lista_citas_medico:
            if item[self.KEY_LABEL_CITA_ID] == identificador_cita:
                medico.borrar_cita_medico(item)
        # Actualizamos el médico en el fichero JSON
        medico.actualizar_medico_store()

        # Cambiamos el estado de la cita a Cancelada
        cita = CitaMedica.obtener_cita(identificador_cita)
        cita.modificar_estado_cita()
        cita.actualizar_cita_store()
        print("\nCita cancelada")

    def consultar_citas_paciente(self, id_paciente: str):
        """Imprime las citas que tiene el paciente"""
        print("\nMis citas:")
        paciente = RegistroPaciente.obtener_paciente(id_paciente)
        lista_citas_paciente = paciente.mis_citas
        for item in lista_citas_paciente:
            medico = RegistroMedico.obtener_medico(item[self.KEY_LABEL_CITA_MEDICO])
            print("CITA: Fecha: " + item[self.KEY_LABEL_CITA_FECHA] + ", Medico: " + medico.nombre_completo + ", Especialidad: " + item[self.KEY_LABEL_CITA_ESPECIALIDAD])

    def consultar_citas_medico(self, id_medico: str):
        """Imprime las citas que tiene el médico"""
        print("\nMis citas:")
        medico = RegistroMedico.obtener_medico(id_medico)
        lista_citas_medico = medico.mis_citas
        for item in lista_citas_medico:
            paciente = RegistroPaciente.obtener_paciente(item[self.KEY_LABEL_CITA_PACIENTE])
            print("CITA: Fecha: " + item[self.KEY_LABEL_CITA_FECHA] + ", Paciente: " + paciente.nombre_completo + ", Motivo Consulta: " + item[self.KEY_LABEL_CITA_MOTIVO])

    def interfaz_paciente(self, paciente: RegistroPaciente):
        # Interfaz paciente
        print("\nINTERFAZ PACIENTE")
        while True:
            print("\nOpciones disponibles:")
            print("1. Pedir cita")
            print("2. Cancelar cita")
            print("3. Consultar mis citas")
            print("4. Cerrar sesión")
            opcion = input("Indique una opción (1/2/3/4): ")

            if opcion == "1":
                self.pedir_cita(paciente.id_paciente)
                print("\nINTERFAZ PACIENTE")
                continue
            elif opcion == "2":
                self.cancelar_cita(paciente.id_paciente)
                print("\nINTERFAZ PACIENTE")
                continue
            elif opcion == "3":
                self.consultar_citas_paciente(paciente.id_paciente)
                print("\nINTERFAZ PACIENTE")
                continue
            elif opcion == "4":
                print("\nCerrando sesión...")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")

    def interfaz_medico(self, medico: RegistroMedico):
        # Interfaz medico
        print("\nINTERFAZ MÉDICO")
        while True:
            print("\nOpciones disponibles:")
            print("1. Consultar mis citas")
            print("2. Cerrar sesión")
            opcion = input("Indique una opción (1/2): ")

            if opcion == "1":
                self.consultar_citas_medico(medico.id_medico)
                continue
            elif opcion == "2":
                print("\nCerrando sesión...")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")

    def main(self):
        """Función Principal"""

        # Preparación del sistema
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
        # Crear Autoridad de Certificación Raíz (Ministerio de Sanidad)
        criptografia = Criptografia()
        ac1_cert = criptografia.crear_autoridad_raiz()
        # Crear Autoridad de Certificación Subordinada (Centro de Salud)
        criptografia.crear_autoridad_subordinada_centro_salud(self, ac1_cert)
        # Crear Autoridad de Certificación Subordinada (FNMT)
        criptografia.crear_autoridad_subordinada_fnmt(ac1_cert)
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
