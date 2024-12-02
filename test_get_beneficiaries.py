from src.erp_client import ERPClient
from dotenv import load_dotenv
import os
import sys
import logging
import signal
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


def test_get_beneficiaries():
    global client

    try:
        # Cargar variables de entorno
        load_dotenv()

        # Verificar variables requeridas
        required_vars = ["ERP_URL", "ERP_USER", "ERP_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Faltan variables de entorno: {', '.join(missing_vars)}")

        # Inicializar cliente y hacer login
        logger.info("Iniciando cliente ERP...")
        client = ERPClient()

        logger.info("Iniciando sesión...")
        client.login()
        logger.info("Login exitoso")

        # Obtener beneficiarios
        logger.info("Obteniendo lista de beneficiarios...")
        beneficiaries = client.get_beneficiaries()

        # Mostrar resultados
        logger.info(f"Se encontraron {len(beneficiaries)} beneficiarios para hoy")
        for i, beneficiary in enumerate(beneficiaries, 1):
            logger.info(f"Beneficiario {i}:")
            logger.info(f"  CPF: {beneficiary['cpf']}")
            logger.info(f"  Dialog ID: {beneficiary['dialog_id']}")

            # Procesar detalles del beneficiario
            logger.info(f"Procesando detalles del beneficiario {i}...")
            details = client.process_beneficiary_details(beneficiary)
            logger.info(f"  Número de Beneficio: {details['benefit_number']}")
            logger.info("---")

            # Pequeña pausa entre beneficiarios
            time.sleep(1)

        logger.info("\nPrueba completada exitosamente")
        logger.info("Presiona Ctrl+C para cerrar el navegador...")

        # Mantener el script corriendo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\nPrueba interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error durante la prueba: {str(e)}")
        raise
    finally:
        if client:
            logger.info("Limpiando recursos...")
            client.cleanup()
            logger.info("Recursos liberados")


if __name__ == "__main__":
    # Configurar el manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    test_get_beneficiaries()
