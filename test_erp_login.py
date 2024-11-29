from src.erp_client import ERPClient
from dotenv import load_dotenv
import os
import sys
import logging
import signal
import time


# Añadir el directorio raíz al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
client = None


def signal_handler(sig, frame):
    """Maneja el cierre graceful cuando se presiona Ctrl+C"""
    print("\nCerrando navegador...")
    if client:
        client.cleanup()
    sys.exit(0)


def test_erp_login():
    global client

    try:
        # Cargar variables de entorno
        load_dotenv()

        # Inicializar cliente
        client = ERPClient()

        # Intentar login
        client.login()

        print("\nLogin completado. El navegador se mantendrá abierto.")
        print("Presiona Ctrl+C para cerrar el navegador...")

        # Mantener el script corriendo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nCerrando navegador...")
    except Exception as e:
        logger.error(f"Error durante el login: {str(e)}")
    finally:
        if client:
            client.cleanup()


if __name__ == "__main__":
    # Configurar el manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    test_erp_login()
