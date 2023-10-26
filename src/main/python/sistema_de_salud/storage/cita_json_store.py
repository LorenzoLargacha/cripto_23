"""Module cita_json_store"""
from sistema_de_salud.storage.json_store import JsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH


class CitaJsonStore(JsonStore):
    """Clase hija de JsonStore con los atributos para store_citas"""

    class __CitaJsonStore(JsonStore):
        """Clase privada, patron singleton"""
        _FILE_PATH = JSON_FILES_PATH + "store_citas.json"
        _ID_FIELD = "_CitaMedica__identificador_cita"

        __ERROR_MESSAGE_INVALID_OBJECT = "Objeto CitaMedica invalido"
        __ERROR_MESSAGE_ID_REGISTRADO = "Cita ya registrada"
        __ERROR_MESSAGE_ID_NO_ENCONTRADO = "Cita no registrada"

        def guardar_cita_store(self, cita: object) -> True:
            """Guarda un cita en un fichero Json"""
            # Importamos aquí CitaMedica para evitar import circular
            from sistema_de_salud.cita_medica import CitaMedica
            if not isinstance(cita, CitaMedica):
                raise ExcepcionesGestor(self.__ERROR_MESSAGE_INVALID_OBJECT)

            found = False
            # Buscamos el identificador_cita
            item = self.find_item(cita.identificador_cita)
            if item is not None:
                found = True    # si lo encontramos
            if found is False:
                self.add_item(cita)
            if found is True:
                # Estamos intentando guardar en el store una cita que ya fue guardada
                raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_REGISTRADO)
            return True

        def buscar_cita_store(self, identificador_cita: str):
            """Busca una cita en store_citas"""
            item_found = self.find_item(identificador_cita)
            try:
                if item_found is None:
                    raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_NO_ENCONTRADO)
                return item_found

            except ExcepcionesGestor as e:
                print(e)
                return None

    __instance = None

    def __new__(cls):
        if not CitaJsonStore.__instance:
            CitaJsonStore.__instance = CitaJsonStore.__CitaJsonStore()
        return CitaJsonStore.__instance