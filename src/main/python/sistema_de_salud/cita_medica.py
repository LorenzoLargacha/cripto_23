"""CitaMedica"""
import hashlib
import json
from datetime import datetime


class CitaMedica:
    """Clase que representa una cita médica de un paciente"""
    def __init__(self, id_medico, especialidad, fecha_hora, id_paciente, telefono_paciente, motivo_consulta, estado_cita="Activa"):

        # Creamos los atributos
        self.__id_medico = id_medico
        self.__especialidad = especialidad
        self.__fecha_hora = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        self.__id_paciente = id_paciente
        self.__telefono_paciente = telefono_paciente
        self.__motivo_consulta = motivo_consulta
        self.__identificador_cita = self.firma_cita
        self.__estado_cita = estado_cita

    def __str__(self):
        return "CitaMedica:" + json.dumps(self.__dict__)

    def __firma_string(self) -> str:
        """Crea el string utilizado para generar el identificador de la cita"""
        return "{id_medico:" + self.__id_medico + ",especialidad:" + self.__especialidad + ",fecha_hora:" + \
               self.__fecha_hora + ",id_paciente:" + self.__id_paciente + \
               ",motivo_consulta:" + self.__motivo_consulta + "}"

    def mostrar_info_publica(self) -> str:
        """Devuleve la información pública de la cita como un string"""
        return f"CITA: Fecha: {self.fecha_hora} Medico: {self.id_medico} Especialidad: {self.especialidad}"

    @property
    def id_medico(self):
        """Property que representa el DNI del médico"""
        return self.__id_medico

    @id_medico.setter
    def id_medico(self, value):
        self.__id_medico = value

    @property
    def especialidad(self):
        """Property que representa la especialidad del médico"""
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, value):
        self.__especialidad = value

    @property
    def fecha_hora(self):
        """Property que representa la fecha y hora de la cita médica"""
        # Convert the string to a datetime object
        return datetime.strptime(self.__fecha_hora, "%Y-%m-%d %H:%M:%S")

    @fecha_hora.setter
    def fecha_hora(self, value_date_time):
        self.__fecha_hora = value_date_time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id_paciente(self):
        """Property que representa el DNI del paciente"""
        return self.__id_paciente

    @id_paciente.setter
    def id_paciente(self, value):
        self.__id_paciente = value

    @property
    def telefono_paciente(self):
        """Property que representa el número de teléfono del paciente"""
        return self.__telefono_paciente

    @telefono_paciente.setter
    def telefono_paciente(self, value):
        self.__telefono_paciente = value

    @property
    def motivo_consulta(self):
        """Property que representa el número de teléfono del paciente"""
        return self.__motivo_consulta

    @motivo_consulta.setter
    def motivo_consulta(self, value):
        self.__motivo_consulta = value

    @property
    def firma_cita(self) -> str:
        """Devuelve la firma sha256 de la cita"""
        return hashlib.sha256(self.__firma_string().encode()).hexdigest()

    @property
    def identificador_cita(self) -> str:
        """Devuelve el identificador de la cita"""
        return self.__identificador_cita

    @property
    def estado_cita(self) -> str:
        """Property que representa el estado de una cita"""
        return self.__estado_cita
