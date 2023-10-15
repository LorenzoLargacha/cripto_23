"""Module autenticacion_json_store"""
import json
from sistema_de_salud.storage.json_store import JsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH


class AutenticacionJsonStore(JsonStore):
    """Clase hija de JsonStore con los atributos para store_autenticaciones"""

    class __AutenticacionJsonStore(JsonStore):
        """Clase privada, patron singleton"""
        _FILE_PATH = JSON_FILES_PATH + "store_autenticaciones.json"
        _ID_FIELD = "_AutenticacionUsuario__id_usuario"
        _PASSWORD_FIELD = "_AutenticacionUsuario__password"

        __ERROR_MESSAGE_ID_REGISTRADO = "Autenticación de usuario ya registrada"
        __ERROR_MESSAGE_ID_NO_ENCONTRADO = "Autenticación de usuario no encontrada"

        def add_item(self, usuario: dict) -> None:
            """Añade un diccionario a un fichero Json"""
            data_list = self.load_store()
            data_list.append(usuario)
            self.save_store(data_list)

        def guardar_password_store(self, usuario) -> True:
            """Guarda la autenticación de un usuario en un fichero Json"""
            found = False
            # Buscamos el id_usuario
            item = self.find_item(usuario[self._ID_FIELD])
            if item is not None:
                found = True    # si lo encontramos

            if found is False:
                self.add_item(usuario)
            if found is True:
                raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_REGISTRADO)

            return True

        def buscar_password_store(self, id_usuario: str):
            """Busca una password en store_autenticaciones"""
            item_found = self.find_item(id_usuario)
            try:
                if item_found is None:
                    raise ExcepcionesGestor(self.__ERROR_MESSAGE_ID_NO_ENCONTRADO)
                return item_found[self._PASSWORD_FIELD]

            except ExcepcionesGestor as e:
                print("ERROR:", e)
                return None

    __instance = None

    def __new__(cls):
        if not AutenticacionJsonStore.__instance:
            AutenticacionJsonStore.__instance = AutenticacionJsonStore.__AutenticacionJsonStore()
        return AutenticacionJsonStore.__instance
