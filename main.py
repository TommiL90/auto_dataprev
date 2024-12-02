import logging
from dotenv import load_dotenv
from src.dataprev_client import DataprevClient
from src.erp_client import ERPClient

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    try:
        logger.info("Iniciando proceso de automatización")

        # Inicializar clientes
        erp_client = ERPClient()
        dataprev_client = DataprevClient()

        # Login en ambos sistemas
        logger.info("Iniciando login en ERP...")
        erp_client.login()

        logger.info("Iniciando login en Dataprev...")
        dataprev_client.login()

        # Obtener beneficiarios del ERP
        logger.info("Obteniendo lista de beneficiarios...")
        beneficiaries = erp_client.get_beneficiaries()
        logger.info(f"Se encontraron {len(beneficiaries)} beneficiarios para procesar")

        if not beneficiaries:
            logger.info("No se encontraron beneficiarios para procesar")
            return

        # Procesar solo el primer beneficiario
        first_beneficiary = beneficiaries[0]
        logger.info(
            f"Procesando primer beneficiario con CPF: {first_beneficiary['cpf']}"
        )

        # Obtener número de beneficio
        logger.info("Obteniendo número de beneficio...")
        processed_beneficiary = erp_client.process_beneficiary_details(
            first_beneficiary
        )
        logger.info(
            f"Número de beneficio obtenido: {processed_beneficiary['benefit_number']}"
        )

        # Verificar en Dataprev
        logger.info("Verificando beneficiario en Dataprev...")
        dataprev_client.check_eligibility(processed_beneficiary)
        logger.info("Submit realizado en Dataprev. Deteniendo el proceso...")

    except Exception as e:
        logger.error(f"Error en el proceso principal: {str(e)}")
        raise
    finally:
        # Cerrar sesiones
        try:
            erp_client.logout()
            dataprev_client.logout()
        except Exception as e:
            logger.error(f"Error cerrando sesiones: {str(e)}")


if __name__ == "__main__":
    # Cargar variables de entorno
    load_dotenv()
    main()
