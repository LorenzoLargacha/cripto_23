"""Module medico_json_store"""
from sistema_de_salud.storage.json_store import JsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH


class MedicoJsonStore(JsonStore):
    """Clase hija de JsonStore con los atributos para store_medicos"""

    class __MedicoJsonStore(JsonStore):
        """Clase privada, patron singleton"""
        _FILE_PATH = JSON_FILES_PATH + "store_medicos.json"
        _ID_FIELD = "_RegistroMedico__id_medico"

        __ERROR_MESSAGE_INVALID_OBJECT = "Objeto RegistroMedico invalido"
        __ERROR_MESSAGE_ID_REGISTRADO = "ID del médico ya registrado"
        __ERROR_MESSAGE_ID_NO_ENCONTRADO = "ID del médico no encontrado"

        def guardar_medico_store(self, medico) -> True:
            """Guarda un médico en un fichero Json"""
            # Importamos aquí RegistroMedico para evitar import circular
            from sistema_de_salud.registro_medico import RegistroMedico
            if not isinstance(medico, RegistroMedico):
                raise ExcepcionesGestor(self.__ERROR_MESSAGE_INVALID_OBJECT)

            found = False
            # Buscamos el id_medico
            item = self.find_item(medico.id_medico)
            if item is not None:
                found = True    # si lo encontramos
            try:
                if found is False:
                    self.add_item(medico)
                if found is True:
                    raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_REGISTRADO)
                return True

            except ExcepcionesGestor as e:
                print("ERROR:", e)
                return False

        def buscar_medico_store(self, id_medico: str):
            """Busca un paciente en store_medicos"""
            item_found = self.find_item(id_medico)
            try:
                if item_found is None:
                    raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_NO_ENCONTRADO)
                return item_found

            except ExcepcionesGestor as e:
                print("ERROR:", e)
                return None

    __instance = None

    def __new__(cls):
        if not MedicoJsonStore.__instance:
            MedicoJsonStore.__instance = MedicoJsonStore.__MedicoJsonStore()
        return MedicoJsonStore.__instance
