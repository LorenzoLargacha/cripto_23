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
        """Guarda un data list en un json file"""
        try:
            with open(self._FILE_PATH, "w", encoding="utf-8", newline="") as file:
                json.dump(data_list, file, indent=2)
        except FileNotFoundError as exception:
            raise ExcepcionesGestor(self.__ERROR_MESSAGE_FILE_NOT_FOUND) from exception

    def load_store(self) -> list:
        """Carga el contenido de un fichero json en una lista"""
        try:
            with open(self._FILE_PATH, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except FileNotFoundError:
            # si el fichero no existe inicializar un data list nuevo
            data_list = []
        except json.JSONDecodeError as exception:
            raise ExcepcionesGestor(self.__ERROR_MESSAGE_JSON_DECODE) from exception
        return data_list

    def find_item(self, item_to_find: str) -> any:
        """Busca el valor de un item key en un fichero json"""
        data_list = self.load_store()
        for item in data_list:
            if item[self._ID_FIELD] == item_to_find:
                return item
        return None

    def add_item(self, item: object) -> None:
        """Añade un item a un fichero json"""
        data_list = self.load_store()
        data_list.append(item.__dict__)
        self.save_store(data_list)
