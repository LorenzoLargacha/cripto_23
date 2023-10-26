"""CitaMedica"""
import hashlib
import json
from datetime import datetime
from freezegun import freeze_time

from sistema_de_salud.registro_medico import RegistroMedico
from sistema_de_salud.storage.cita_json_store import CitaJsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor

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
        justnow = datetime.utcnow()
        self.__issued_at = datetime.timestamp(justnow)
        self.__identificador_cita = self.firma_cita
        self.__estado_cita = estado_cita

    def __str__(self):
        return "CitaMedica:" + json.dumps(self.__dict__)

    @classmethod
    def obtener_cita(cls, identificador_cita):
        """Devuelve el objeto CitaMedica para el identificador_cita recibido"""
        store_citas = CitaJsonStore()
        cita_encontrada = store_citas.buscar_cita_store(identificador_cita)
        if cita_encontrada is None:
            raise ExcepcionesGestor("Objeto CitaMedica no encontrado")
        # *** Cuando cifremos con clave pública habrá que descifrar cita_encontrada ***
        # Ponemos el freeze_time a cuando la cita fue registrada para mantener el time_stamp
        freezer = freeze_time(
            datetime.utcfromtimestamp(cita_encontrada["_CitaMedica__issued_at"]))
        freezer.start()
        cita = cls(cita_encontrada["_CitaMedica__id_medico"],
                   cita_encontrada["_CitaMedica__especialidad"],
                   datetime.strptime(cita_encontrada["_CitaMedica__fecha_hora"], "%Y-%m-%d %H:%M:%S"),
                   cita_encontrada["_CitaMedica__id_paciente"],
                   cita_encontrada["_CitaMedica__telefono_paciente"],
                   cita_encontrada["_CitaMedica__motivo_consulta"],
                   cita_encontrada["_CitaMedica__estado_cita"])
        freezer.stop()
        return cita

    def __firma_string(self) -> str:
        """Crea el string utilizado para generar el identificador de la cita"""
        return "{id_medico:" + self.__id_medico + ",especialidad:" + self.__especialidad + ",fecha_hora:" + \
               self.__fecha_hora + ",id_paciente:" + self.__id_paciente + \
               ",motivo_consulta:" + self.__motivo_consulta + ",issuedate:" + self.__issued_at.__str__() + "}"

    def mostrar_info_publica(self) -> str:
        """Devuleve la información pública de la cita como un string"""
        medico = RegistroMedico.obtener_medico(self.id_medico)
        return f"CITA: Fecha: {self.fecha_hora}, Medico: {medico.nombre_completo}, Especialidad: {self.especialidad}"

    def modificar_estado_cita(self) -> None:
        """Modifica el estado de la cita en el objeto CitaMedica"""
        # Comprobamos si la fecha de la cita recibida ya ha pasado
        appointment_days = (datetime.strptime(self.__fecha_hora, "%Y-%m-%d %H:%M:%S").timestamp() / 3600) / 24
        today_time_stamp = datetime.timestamp(datetime.utcnow())
        today_days = (today_time_stamp / 3600) / 24
        try:
            if appointment_days < today_days:
                raise ExcepcionesGestor("\nLa fecha de la cita introducida ya ha pasado")
            # Si la cita esta activa
            if self.__estado_cita == "Activa":
                self.__estado_cita = "Cancelada"
            # Si la cita ya está cancelada
            elif self.__estado_cita == "Cancelada":
                raise ExcepcionesGestor("\nLa cita introducida ya está cancelada")
        except ExcepcionesGestor as e:
            print(e)

    def actualizar_cita_store(self) -> None:
        """Modifica la cita en store_citas"""
        store_citas = CitaJsonStore()
        store_citas.update_item(self, self.__identificador_cita)


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
