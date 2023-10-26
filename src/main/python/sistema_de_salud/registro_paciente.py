"""RegistroPaciente"""
import json
from datetime import datetime
from freezegun import freeze_time

from sistema_de_salud.storage.paciente_json_store import PacienteJsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor

class RegistroPaciente:
    """Clase que representa el registro de un nuevo paciente en el sistema"""

    def __init__(self, id_paciente, nombre_completo, telefono, edad):
        # Creamos los atributos
        self.__id_paciente = id_paciente
        self.__nombre_completo = nombre_completo
        self.__telefono = telefono
        self.__edad = edad
        justnow = datetime.utcnow()
        self.__time_stamp = datetime.timestamp(justnow)
        self.__mis_citas = []

        # añadimos el atributo usuario_sys_id para que se guarde en store_pacientes
        #self.__usuario_sys_id = self.user_system_id

    def __str__(self):
        return "RegistroPaciente:" + json.dumps(self.__dict__)

    @classmethod
    def obtener_paciente(cls, id_paciente):
        """Devuelve el objeto RegistroPaciente para el id_paciente recibido"""
        store_pacientes = PacienteJsonStore()
        paciente_encontrado = store_pacientes.buscar_paciente_store(id_paciente)
        if paciente_encontrado is None:
            raise ExcepcionesGestor("Objeto RegistroPaciente no encontrado")
        # Ponemos el freeze_time cuando el paciente fue registrado para mantener el time_stamp
        freezer = freeze_time(
            datetime.fromtimestamp(paciente_encontrado["_RegistroPaciente__time_stamp"]).date())
        freezer.start()
        paciente = cls(paciente_encontrado["_RegistroPaciente__id_paciente"],
                       paciente_encontrado["_RegistroPaciente__nombre_completo"],
                       paciente_encontrado["_RegistroPaciente__telefono"],
                       paciente_encontrado["_RegistroPaciente__edad"])
        freezer.stop()
        lista_citas = paciente_encontrado["_RegistroPaciente__mis_citas"]
        for item in lista_citas:
            paciente.registrar_cita_paciente(item)
        return paciente

    @property
    def id_paciente(self):
        """Property que representa el DNI del usuario que se registra (registrado)"""
        return self.__id_paciente

    @id_paciente.setter
    def id_paciente(self, value):
        self.__id_paciente = value

    @property
    def nombre_completo(self):
        """Property que representa el nombre y el apellido del registrado"""
        return self.__nombre_completo

    @nombre_completo.setter
    def nombre_completo(self, value):
        self.__nombre_completo = value

    @property
    def telefono(self):
        """Property que representa el número de teléfono del registrado"""
        return self.__telefono

    @telefono.setter
    def telefono(self, value):
        self.__telefono = value

    @property
    def edad(self):
        """Read-only property que devuelve la edad del registrado"""
        return self.__edad

    @property
    def time_stamp(self):
        """Read-only property que devuelve el timestamp del registro"""
        return self.__time_stamp

    @property
    def mis_citas(self):
        """Property que representa las citas del paciente"""
        return self.__mis_citas

    def registrar_cita_paciente(self, identificador_cita):
        """Añade una cita a la lista mis_citas del paciente"""
        self.__mis_citas.append(identificador_cita)

    def borrar_cita_paciente(self, identificador_cita):
        """Borra una cita de la lista mis_citas del paciente"""
        self.__mis_citas.remove(identificador_cita)

    #@property
    #def user_system_id(self):
    #    """Returns the md5 signature"""
    #    return hashlib.md5(self.__str__().encode()).hexdigest()

    #@property
    #def usuario_sys_id(self):
    #    """Read-only property que devuelve el usuario_sys_id"""
    #    return self.__usuario_sys_id
