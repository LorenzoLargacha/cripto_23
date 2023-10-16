"""Module paciente_json_store"""
from sistema_de_salud.storage.json_store import JsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH


class PacienteJsonStore(JsonStore):
    """Clase hija de JsonStore con los atributos para store_pacientes"""

    class __PacienteJsonStore(JsonStore):
        """Clase privada, patron singleton"""
        _FILE_PATH = JSON_FILES_PATH + "store_pacientes.json"
        _ID_FIELD = "_RegistroPaciente__id_paciente"

        __ERROR_MESSAGE_INVALID_OBJECT = "Objeto RegistroPaciente invalido"
        __ERROR_MESSAGE_ID_REGISTRADO = "ID del paciente ya registrado"
        __ERROR_MESSAGE_ID_NO_ENCONTRADO = "Paciente no registrado"

        def guardar_paciente_store(self, paciente) -> True:
            """Guarda un paciente en un fichero Json"""
            # Importamos aquí RegistroPaciente para evitar import circular
            from sistema_de_salud.registro_paciente import RegistroPaciente
            if not isinstance(paciente, RegistroPaciente):
                raise ExcepcionesGestor(self.__ERROR_MESSAGE_INVALID_OBJECT)

            found = False
            # Buscamos el id_paciente
            item = self.find_item(paciente.id_paciente)
            if item is not None:
                found = True    # si lo encontramos
            try:
                if found is False:
                    self.add_item(paciente)
                if found is True:
                    raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_REGISTRADO)
                return True

            except ExcepcionesGestor as e:
                print("ERROR:", e)
                return False

        def buscar_paciente_store(self, id_paciente: str):
            """Busca un paciente en store_pacientes"""
            item_found = self.find_item(id_paciente)
            try:
                if item_found is None:
                    raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_NO_ENCONTRADO)
                return item_found

            except ExcepcionesGestor as e:
                print(e)
                return None

    __instance = None

    def __new__(cls):
        if not PacienteJsonStore.__instance:
            PacienteJsonStore.__instance = PacienteJsonStore.__PacienteJsonStore()
        return PacienteJsonStore.__instance
