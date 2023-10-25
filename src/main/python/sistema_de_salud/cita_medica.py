"""CitaMedica"""
from datetime import datetime
import hashlib


class CitaMedica:
    """Clase que representa una cita médica de un paciente"""

    def __init__(self, id_paciente, id_medico, telefono_paciente, hora_cita, fecha_cita, especialidad):

        # Creamos los atributos
        self.__id_paciente = id_paciente
        self.__id_medico = id_medico
        self.__telefono_paciente = telefono_paciente
        self.__hora_cita = hora_cita
        self.__fecha_cita = fecha_cita
        self.__especialidad = especialidad

    def __str__(self):
        return "RegistroMedico:" + json.dumps(self.__dict__)

    @property
    def id_paciente(self):
        """Property que representa el DNI del paciente"""
        return self.__id_paciente

    @id_paciente.setter
    def id_paciente(self, value):
        self.__id_paciente = value

    @property
    def id_medico(self):
        """Property que representa el DNI del médico"""
        return self.__id_medico

    @id_medico.setter
    def id_medico(self, value):
        self.__id_medico = value

    @property
    def telefono_paciente(self):
        """Property que representa el número de teléfono del pacciente"""
        return self.__telefono_paciente

    @telefono.setter
    def telefono_paciente(self, value):
        self.__telefono_paciente = value

    @property
    def hora_cita(self):
        """Property que representa la hora de la cita médica"""
        return self.__hora_cita

    @telefono.setter
    def hora_cita(self, value):
        self.__hora_cita = value

    @property
    def fecha_cita(self):
        """Property que representa la fecha de la cita médica"""
        return self.__fecha_cita

    @telefono.setter
    def fecha_cita(self, value):
        self.__fecha_cita = value


    @property
    def especialidad(self):
        """Property que representa la especialidad del médico"""
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, value):
        self.__especialidad = value

    pass
