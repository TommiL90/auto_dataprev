from dotenv import load_dotenv
from src.dataprev_client import DataprevClient
import logging
import signal
import sys
import time

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


def test_dataprev_login():
    global client

    try:
        # Cargar variables de entorno
        load_dotenv()

        # Inicializar cliente
        client = DataprevClient()

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
    test_dataprev_login()
