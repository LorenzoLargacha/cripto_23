"""Module paciente_json_store"""
from sistema_de_salud.storage.json_store import JsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH


class CitasJsonStore(JsonStore):
    """Clase hija de JsonStore con los atributos para store_pacientes"""

    class __CitasJsonStore(JsonStore):
        """Clase privada, patron singleton"""
        _FILE_PATH = JSON_FILES_PATH + "store_citas.json"
        _ID_FIELD = "_RegistroCita__id_paciente"

        __ERROR_MESSAGE_INVALID_OBJECT = "Objeto RegistroCita invalido"
        __ERROR_MESSAGE_ID_REGISTRADO = "Cita ya registrada"
        __ERROR_MESSAGE_ID_NO_ENCONTRADO = "Cita no registrada"

        def guardar_cita_store(self, cita) -> True:
            """Guarda un paciente en un fichero Json"""
            # Importamos aquí RegistroPaciente para evitar import circular
            from sistema_de_salud.cita_medica import RegistroCita
            if not isinstance(paciente, RegistroCita):
                raise ExcepcionesGestor(self.__ERROR_MESSAGE_INVALID_OBJECT)

            found = False
            # Buscamos el id_cita
            item = self.find_item(cita.id_cita)
            if item is not None:
                found = True    # si lo encontramos
            try:
                if found is False:
                    self.add_item(cita)
                if found is True:
                    raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_REGISTRADO)
                return True

            except ExcepcionesGestor as e:
                print("ERROR:", e)
                return False

        def buscar_cita_store(self, id_cita: str):
            """Busca un paciente en store_citas"""
            item_found = self.find_item(id_cita)
            try:
                if item_found is None:
                    raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_NO_ENCONTRADO)
                return item_found

            except ExcepcionesGestor as e:
                print(e)
                return None

    __instance = None

    def __new__(cls):
        if not CitasJsonStore.__instance:
            CitasJsonStore.__instance = CitasJsonStore.__CitasJsonStore()
        return CitasJsonStore.__instance