"""Exception module"""


class ExcepcionesGestor(Exception):
    """Excepciones personalizadas para GestorCentroSalud"""
    def __init__(self, message: str) -> None:
        self.__message = message
        super().__init__(self.message)

    @property
    def message(self) -> str:
        """Devuelve el valor de message"""
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        self.__message = value
