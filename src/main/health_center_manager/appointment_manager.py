"""AppointmentManager"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import hashlib

class AppointmentManager:
    """ Class for providing the methods for managing an appointment request """

    def __init__(self):
        pass





################################## version chat gpt con crifrado RSA ######################

usuarios = {
    "usuario1": {
        "clave_privada": None,
        "clave_publica": None,
        "imagen_referencia": None,
        "contraseña": "contraseña1"  # Contraseña de ejemplo
    },
    "usuario2": {
        "clave_privada": None,
        "clave_publica": None,
        "imagen_referencia": None,
        "contraseña": "contraseña2"  # Contraseña de ejemplo
    },
    "usuario3": {
        "clave_privada": None,
        "clave_publica": None,
        "imagen_referencia": None,
        "contraseña": "contraseña3"  # Contraseña de ejemplo
    }
}

# Base de datos de citas (puedes expandirla según tus necesidades)
citas = {}


# Función para generar un par de claves RSA para un usuario
def generar_claves_rsa(usuario):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    usuario["clave_privada"] = private_key
    usuario["clave_publica"] = private_key.public_key()


# Función para cifrar datos utilizando la clave pública
def cifrar_datos(clave_publica, datos):
    datos_cifrados = clave_publica.encrypt(
        datos.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return datos_cifrados


# Función para descifrar datos utilizando la clave privada
def descifrar_datos(clave_privada, datos_cifrados):
    datos_descifrados = clave_privada.decrypt(
        datos_cifrados,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()
    return datos_descifrados


# Función para verificar las credenciales de usuario (reconocimiento facial o contraseña)
def verificar_credenciales():
    usuario = input("Ingrese su nombre de usuario: ")

    # Verificar si el usuario tiene una imagen de referencia para el reconocimiento facial
    if usuarios.get(usuario) and usuarios[usuario]["imagen_referencia"]:
        return autenticar_reconocimiento_facial(usuario)
    else:
        return autenticar_contrasena(usuario)


# Función para autenticar al usuario mediante reconocimiento facial
def autenticar_reconocimiento_facial(usuario):
    imagen_referencia = usuarios[usuario]["imagen_referencia"]

    # Capturar una imagen del usuario para el reconocimiento facial (simplificado)
    # En una implementación real, deberías utilizar bibliotecas como OpenCV o dlib.
    imagen_capturada = input("Capture su imagen para el reconocimiento facial (ruta de la imagen): ")

    # Calcular el hash de ambas imágenes y compararlos
    hash_referencia = hashlib.sha256(open(imagen_referencia, "rb").read()).hexdigest()
    hash_capturada = hashlib.sha256(open(imagen_capturada, "rb").read()).hexdigest()

    if hash_referencia == hash_capturada:
        print("Reconocimiento facial exitoso. Bienvenido.")
        return True
    else:
        print("Reconocimiento facial fallido. Ingrese su contraseña.")
        return autenticar_contrasena(usuario)


# Función para autenticar al usuario mediante contraseña
def autenticar_contrasena(usuario):
    contraseña = input("Ingrese su contraseña: ")
    if usuarios.get(usuario) and usuarios[usuario]["contraseña"] == contraseña:
        print("Contraseña correcta. Bienvenido.")
        return True
    else:
        print("Contraseña incorrecta. Autenticación fallida.")
        return False


# Función principal
def main():
    print("Bienvenido al sistema de citas.")

    # Verificar credenciales y generar claves RSA si es necesario
    usuario = input("Ingrese su nombre de usuario: ")
    if usuario not in usuarios:
        print("Usuario no encontrado. Saliendo del programa.")
        return

    if usuarios[usuario]["clave_privada"] is None:
        print("Generando claves RSA para el usuario...")
        generar_claves_rsa(usuarios[usuario])
        print("Claves generadas con éxito.")

    while True:
        print("\nOpciones disponibles:")
        print("1. Pedir cita")
        print("2. Anular cita")
        print("3. Consultar citas")
        print("4. Salir")
        opcion = input("Seleccione una opción (1/2/3/4): ")

        if opcion == "1":
            pedir_cita()
        elif opcion == "2":
            anular_cita()
        elif opcion == "3":
            consultar_citas()
        elif opcion == "4":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Intente nuevamente.")


# Función para pedir una cita
def pedir_cita():
    nombre_usuario = input("Ingrese su nombre de usuario: ")
    fecha = input("Ingrese la fecha de la cita (formato dd/mm/yyyy): ")
    hora = input("Ingrese la hora de la cita (formato hh:mm): ")

    # Cifrar los detalles de la cita con la clave pública del usuario
    clave_publica = usuarios[nombre_usuario]["clave_publica"]
    datos_cifrados = cifrar_datos(clave_publica, f"Fecha: {fecha}, Hora: {hora}")

    # Almacenar la cita cifrada en la base de datos de citas
    citas[(nombre_usuario, fecha, hora)] = datos_cifrados
    print("Cita programada con éxito.")


# Función para anular una cita
def anular_cita():
    nombre_usuario = input("Ingrese su nombre de usuario: ")
    fecha = input("Ingrese la fecha de la cita que desea anular (formato dd/mm/yyyy): ")
    hora = input("Ingrese la hora de la cita que desea anular (formato hh:mm): ")

    # Verificar si la cita existe
    if (nombre_usuario, fecha, hora) in citas:
        # Descifrar los detalles de la cita con la clave privada del usuario
        clave_privada = usuarios[nombre_usuario]["clave_privada"]
        datos_cifrados = citas[(nombre_usuario, fecha, hora)]
        datos_descifrados = descifrar_datos(clave_privada, datos_cifrados)

        # Mostrar los detalles de la cita
        print(f"Detalles de la cita:\n{datos_descifrados}")

        # Eliminar la cita de la base de datos
        del citas[(nombre_usuario, fecha, hora)]
        print("Cita anulada con éxito.")
    else:
        print("No se encontró ninguna cita para anular.")


# Función para consultar citas
def consultar_citas():
    nombre_usuario = input("Ingrese su nombre de usuario: ")
    print("Sus citas programadas:")
    for cita, datos_cifrados in citas.items():
        if cita[0] == nombre_usuario:
            # Descifrar los detalles de la cita con la clave privada del usuario
            clave_privada = usuarios[nombre_usuario]["clave_privada"]
            datos_descifrados = descifrar_datos(clave_privada, datos_cifrados)
            print(f"Fecha: {cita[1]}, Hora: {cita[2]}\n{datos_descifrados}")

if __name__ == "__main__":
    main()

