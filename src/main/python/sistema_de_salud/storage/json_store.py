"""Module json_store"""
import json
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor


class JsonStore:
    """Clase con los métodos para gestionar los almacenes"""
    # Ruta fichero store
    _FILE_PATH = ""
    # Key a buscar
    _ID_FIELD = ""

    __ERROR_MESSAGE_FILE_NOT_FOUND = "Nombre del fichero o ruta de archivo incorrectos"
    __ERROR_MESSAGE_JSON_DECODE = "JSON Decode Error - Wrong JSON Format"

    def __init__(self):
        pass

    def save_store(self, data_list: list) -> None:
        """Guarda una lista en un fichero Json"""
        try:
            with open(self._FILE_PATH, "w", encoding="utf-8", newline="") as file:
                json.dump(data_list, file, indent=2)
        except FileNotFoundError as exception:
            raise ExcepcionesGestor(self.__ERROR_MESSAGE_FILE_NOT_FOUND) from exception

    def load_store(self) -> list:
        """Carga el contenido de un fichero Json en una lista"""
        try:
            with open(self._FILE_PATH, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except FileNotFoundError:
            # si el fichero no existe inicializar un data list nuevo
            data_list = []
        except json.JSONDecodeError as exception:
            raise ExcepcionesGestor(self.__ERROR_MESSAGE_JSON_DECODE) from exception
        return data_list

    def find_item(self, key_value: str, key=None):
        """Busca el primer item con item[key]=key_value en un fichero Json"""
        data_list = self.load_store()
        if key is None:     # si no se especifica key será ID_FIELD
            key = self._ID_FIELD
        for item in data_list:
            if item[key] == key_value:
                return item
        return None

    def find_items_list(self, key_value, key=None):
        """Busca todos los items con item[key]=key_value en un fichero Json"""
        data_list = self.load_store()
        if key is None:
            key = self._ID_FIELD
        data_list_result = []
        for item in data_list:
            if item[key] == key_value:
                data_list_result.append(item)
        return data_list_result

    def add_item(self, item: object) -> None:
        """Añade un item a un fichero Json"""
        data_list = self.load_store()
        data_list.append(item.__dict__)
        self.save_store(data_list)
