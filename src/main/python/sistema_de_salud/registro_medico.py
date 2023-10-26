"""RegistroMedico"""
import json
from datetime import datetime
from freezegun import freeze_time

from sistema_de_salud.storage.medico_json_store import MedicoJsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor

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
        self.__mis_citas = []

        # añadimos el atributo usuario_sys_id para que se guarde en store_medicos
        #self.__usuario_sys_id = self.user_system_id

    def __str__(self):
        return "RegistroMedico:" + json.dumps(self.__dict__)

    @classmethod
    def obtener_medico(cls, id_medico):
        """Devuelve el objeto RegistroMedico para el id_medico recibido"""
        store_medicos = MedicoJsonStore()
        medico_encontrado = store_medicos.buscar_medico_store(id_medico)
        if medico_encontrado is None:
            raise ExcepcionesGestor("Objeto RegistroMedico no encontrado")
        # Ponemos el freeze_time a cuando el paciente fue registrado para mantener el time_stamp
        freezer = freeze_time(
            datetime.utcfromtimestamp(medico_encontrado["_RegistroMedico__time_stamp"]))
        freezer.start()
        medico = cls(medico_encontrado["_RegistroMedico__id_medico"],
                     medico_encontrado["_RegistroMedico__nombre_completo"],
                     medico_encontrado["_RegistroMedico__telefono"],
                     medico_encontrado["_RegistroMedico__edad"],
                     medico_encontrado["_RegistroMedico__especialidad"])
        freezer.stop()
        lista_citas = medico_encontrado["_RegistroMedico__mis_citas"]
        for item in lista_citas:
            medico.registrar_cita_medico(item)
        return medico

    def actualizar_medico_store(self) -> None:
        """Modifica el médico en store_medicos"""
        store_medicos = MedicoJsonStore()
        store_medicos.update_item(self, self.__id_medico)

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

    @property
    def mis_citas(self):
        """Property que representa las citas del médico"""
        return self.__mis_citas

    def registrar_cita_medico(self, info_cita):
        """Añade la información de una cita a la lista mis_citas del médico"""
        self.__mis_citas.append(info_cita)

    def borrar_cita_medico(self, info_cita):
        """Borra la información de una cita de la lista mis_citas del médico"""
        self.__mis_citas.remove(info_cita)

    #@property
    #def user_system_id(self):
    #    """Returns the md5 signature"""
    #    return hashlib.md5(self.__str__().encode()).hexdigest()

    #@property
    #def usuario_sys_id(self):
    #    """Read-only property que devuelve el usuario_sys_id"""
    #    return self.__usuario_sys_id
