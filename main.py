import logging
import schedule
import time
from dotenv import load_dotenv
from src.dataprev_client import DataprevClient
from src.erp_client import ERPClient
from src.notification_manager import NotificationManager
# from src.captcha_solver import CaptchaSolver

# Configuración de logging
logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def process_beneficiary(dataprev_client, erp_client, beneficiary_data):
    """Procesa un beneficiario individual."""
    try:
        # Verificar elegibilidad en Dataprev
        eligibility = dataprev_client.check_eligibility(beneficiary_data)

        if eligibility["is_eligible"]:
            # Obtener enlace de Dataprev
            link = dataprev_client.get_registration_link(beneficiary_data)
            # Actualizar en ERP
            erp_client.update_beneficiary(
                beneficiary_data["cpf"], status="ELIGIBLE", dataprev_link=link
            )
        else:
            # Marcar como inelegible en ERP
            erp_client.update_beneficiary(beneficiary_data["cpf"], status="INELIGIBLE")

        logger.info(
            f"Procesado beneficiario {beneficiary_data['cpf']} - Status: {eligibility['status']}"
        )

    except Exception as e:
        logger.error(
            f"Error procesando beneficiario {beneficiary_data['cpf']}: {str(e)}"
        )
        NotificationManager.send_error_notification(
            f"Error procesando beneficiario {beneficiary_data['cpf']}", str(e)
        )


def main_process():
    """Proceso principal de automatización."""
    try:
        logger.info("Iniciando proceso de automatización")

        # Inicializar clientes
        dataprev_client = DataprevClient()
        erp_client = ERPClient()

        # Login en ambos sistemas
        dataprev_client.login()
        erp_client.login()

        # Obtener lista de beneficiarios del ERP
        beneficiaries = erp_client.get_beneficiaries()

        # Procesar cada beneficiario
        for beneficiary in beneficiaries:
            process_beneficiary(dataprev_client, erp_client, beneficiary)

        logger.info("Proceso completado exitosamente")

    except Exception as e:
        error_msg = f"Error en el proceso principal: {str(e)}"
        logger.error(error_msg)
        NotificationManager.send_error_notification(
            "Error en automatización", error_msg
        )
    finally:
        # Cerrar sesiones
        dataprev_client.logout()
        erp_client.logout()


def run_scheduled_task():
    """Ejecuta el proceso principal y maneja cualquier error."""
    try:
        main_process()
    except Exception as e:
        logger.error(f"Error en la tarea programada: {str(e)}")
        NotificationManager.send_error_notification("Error en tarea programada", str(e))


if __name__ == "__main__":
    # Cargar variables de entorno
    load_dotenv()

    # Programar la ejecución cada 30 minutos
    schedule.every(30).minutes.do(run_scheduled_task)

    # Ejecutar una vez al inicio
    run_scheduled_task()

    # Mantener el script corriendo
    while True:
        schedule.run_pending()
        time.sleep(1)
