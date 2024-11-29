import os
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class ERPClient:
    def __init__(self):
        self.url = os.getenv("ERP_URL")
        self.user = os.getenv("ERP_USER")
        self.password = os.getenv("ERP_PASSWORD")
        self.browser = None
        self.page = None

    def login(self):
        """Inicia sesión en el ERP."""
        try:
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(
                headless=False,  # Cambiado a False para ver el navegador
                args=['--start-maximized']
            )
            self.page = self.browser.new_page(viewport={'width': 1920, 'height': 1080})

            # Navegar a la página de login
            logger.info(f"Navegando a {self.url}")
            self.page.goto(self.url)

            # Llenar credenciales
            logger.info("Ingresando credenciales...")
            self.page.fill("#username", self.user)
            self.page.fill("#password", self.password)

            # Enviar formulario
            logger.info("Enviando formulario...")
            self.page.click("#login-button")

            # Esperar a que se complete el login
            logger.info("Esperando redirección después del login...")
            self.page.wait_for_selector(".dashboard", timeout=30000)
            
            if "login" in self.page.url:
                raise Exception("Login fallido - Redirigido de vuelta a la página de login")

            logger.info("Login exitoso en ERP")

        except Exception as e:
            logger.error(f"Error en login de ERP: {str(e)}")
            if self.browser:
                self.browser.close()
            raise

    def get_beneficiaries(self):
        """Obtiene la lista de beneficiarios del ERP."""
        try:
            # Navegar a la sección de beneficiarios
            self.page.click("text=CRM")
            self.page.click("text=Dataprev")
            self.page.click("text=Beneficiarios DataPrev")

            # Esperar a que cargue la tabla
            self.page.wait_for_selector(".beneficiarios-table")

            # Obtener datos de beneficiarios
            beneficiaries = []
            rows = self.page.query_selector_all(".beneficiario-row")

            for row in rows:
                # Hacer clic en editar para abrir el modal
                row.query_selector(".edit-button").click()
                self.page.wait_for_selector(".modal-content")

                # Extraer información del modal
                beneficiary = {
                    "cpf": self.page.query_selector("#cpf").input_value(),
                    "nome": self.page.query_selector("#nome").input_value(),
                    # ... extraer otros campos necesarios
                }

                beneficiaries.append(beneficiary)

                # Cerrar modal
                self.page.click(".close-modal")

            return beneficiaries

        except Exception as e:
            logger.error(f"Error obteniendo beneficiarios: {str(e)}")
            raise

    def update_beneficiary(self, cpf, status, dataprev_link=None):
        """Actualiza el estado de un beneficiario en el ERP."""
        try:
            # Buscar beneficiario
            self.page.fill("#search-cpf", cpf)
            self.page.click("#search-button")

            # Abrir modal de edición
            self.page.click(".edit-button")
            self.page.wait_for_selector(".modal-content")

            # Actualizar estado
            self.page.select_option("#status", status)

            # Si hay enlace, actualizarlo
            if dataprev_link:
                self.page.fill("#dataprev-link", dataprev_link)

            # Guardar cambios
            self.page.click("#save-button")
            self.page.wait_for_selector(".success-message")

            logger.info(f"Beneficiario {cpf} actualizado con éxito")

        except Exception as e:
            logger.error(f"Error actualizando beneficiario {cpf}: {str(e)}")
            raise

    def logout(self):
        """Cierra la sesión y el navegador."""
        try:
            if self.page:
                self.page.click("#logout-button")
            if self.browser:
                self.browser.close()
        except Exception as e:
            logger.error(f"Error en logout de ERP: {str(e)}")
