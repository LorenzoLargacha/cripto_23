"""Module cita_json_store"""
from datetime import datetime
from sistema_de_salud.storage.json_store import JsonStore
from sistema_de_salud.exception.excepciones_gestor import ExcepcionesGestor
from sistema_de_salud.cfg.gestor_centro_salud_config import JSON_FILES_PATH


class CitaJsonStore(JsonStore):
    """Clase hija de JsonStore con los atributos para store_citas"""

    class __CitaJsonStore(JsonStore):
        """Clase privada, patron singleton"""
        _FILE_PATH = JSON_FILES_PATH + "store_citas.json"
        _ID_FIELD = "_CitaMedica__identificador_cita"
        __MEDICO_FIELD = "_CitaMedica__id_medico"
        __FECHA_FIELD = "_CitaMedica__fecha_hora"
        __ESTADO_FIELD = "_CitaMedica__estado_cita"

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
                # *** Cuando cifremos con clave pública habrá que crear nuestro propio add_item que cifre ***
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

        def buscar_cita_fecha_hora_store(self, fecha_hora_str: str):
            """Busca una cita con una fecha y hora determinadas en store_citas"""
            item_found = self.find_item(fecha_hora_str, self.__FECHA_FIELD)
            if item_found is None:
                return None
            return item_found

        def buscar_citas_activas_medico_fecha_store(self, id_medico: str, fecha_hora_str: str) -> list:
            """Busca todas las citas de un médico para una fecha en store_citas"""
            items_found = self.find_items_list(id_medico, self.__MEDICO_FIELD)
            if not items_found:
                # si la lista está vacía
                return items_found
            lista_citas = []
            for item in items_found:
                if item[self.__ESTADO_FIELD] == "Activa":
                    # Convertimos la fecha y hora a objeto datetime
                    fecha_hora_item = datetime.strptime(item[self.__FECHA_FIELD], "%Y-%m-%d %H:%M:%S")
                    fecha_item = (fecha_hora_item.year, fecha_hora_item.month, fecha_hora_item.day)
                    fecha_hora_solicitada = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
                    fecha_solicitada = (fecha_hora_solicitada.year, fecha_hora_solicitada.month, fecha_hora_solicitada.day)
                    if fecha_item == fecha_solicitada:
                        lista_citas.append(item)
            return lista_citas

        def buscar_citas_activas_medico_fecha_hora_store(self, id_medico: str, fecha_hora_str: str) -> list:
            """Busca todas las citas de un médico para una fecha_hora en store_citas"""
            items_found = self.find_items_list(id_medico, self.__MEDICO_FIELD)
            if not items_found:
                # si la lista está vacía
                return items_found
            lista_citas = []
            for item in items_found:
                if item[self.__ESTADO_FIELD] == "Activa":
                    # Convertimos la fecha y hora a objeto datetime
                    fecha_hora_item = datetime.strptime(item[self.__FECHA_FIELD], "%Y-%m-%d %H:%M:%S")
                    fecha_hora_solicitada = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
                    if fecha_hora_item == fecha_hora_solicitada:
                        lista_citas.append(item)
            return lista_citas

    __instance = None

    def __new__(cls):
        if not CitaJsonStore.__instance:
            CitaJsonStore.__instance = CitaJsonStore.__CitaJsonStore()
        return CitaJsonStore.__instance