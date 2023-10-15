"""RegistroMedico"""
import hashlib
import json
from datetime import datetime


class RegistroMedico:
    """Clase que representa el registro de un nuevo médico en el sistema"""

    def __init__(self, id_medico, nombre_completo, telefono, edad, especialidad):
        # Creamos los atributos
        self.__id_medico = id_medico
        self.__nombre_completo = nombre_completo
        self.__telefono = telefono
        self.__edad = edad
        self.__especialidad = especialidad
        justnow = datetime.utcnow()
        self.__time_stamp = datetime.timestamp(justnow)

        # evitamos que cambie la hora (borrar despues, solo sirve para los tests)
        # self.__time_stamp = 1646300783.846215

        # añadimos el atributo usuario_sys_id para que se guarde en store_medicos
        #self.__usuario_sys_id = self.user_system_id

    def __str__(self):
        return "RegistroMedico:" + json.dumps(self.__dict__)

    @property
    def id_medico(self):
        """Property que representa el DNI del usuario que se registra (registrado)"""
        return self.__id_medico

    @id_medico.setter
    def id_medico(self, value):
        self.__id_medico = value

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
    def especialidad(self):
        """Property que representa la especialidad del médico registrado"""
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, value):
        self.__especialidad = value

    @property
    def time_stamp(self):
        """Read-only property que devuelve el timestamp del registro"""
        return self.__time_stamp

    #@property
    #def user_system_id(self):
    #    """Returns the md5 signature"""
    #    return hashlib.md5(self.__str__().encode()).hexdigest()

    #@property
    #def usuario_sys_id(self):
    #    """Read-only property que devuelve el usuario_sys_id"""
    #    return self.__usuario_sys_id
