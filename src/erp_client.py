import os
import logging
import time
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class ERPClient:
    def __init__(self):
        self.url = os.getenv("ERP_URL")
        self.user = os.getenv("ERP_USER")
        self.password = os.getenv("ERP_PASSWORD")
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _setup_browser(self) -> None:
        """Configura el navegador con los parámetros correctos."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                channel="chrome",  # Usar Chrome instalado en el sistema
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ],
            )
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 "
                    "(Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/119.0.0.0 "
                    "Safari/537.36"
                ),
            )
            self.page = self.context.new_page()

            # Configurar timeouts más largos
            self.page.set_default_timeout(60000)  # 60 segundos
            self.page.set_default_navigation_timeout(60000)  # 60 segundos

        except Exception as e:
            logger.error(f"Error configurando el navegador: {str(e)}")
            self.cleanup()
            raise

    def login(self) -> None:
        """Inicia sesión en el ERP."""
        try:
            if not self.browser:
                self._setup_browser()

            # Navegar a la página inicial
            logger.info(f"Navegando a {self.url}")
            self.page.goto(self.url, wait_until="networkidle")

            # Esperar y llenar credenciales
            logger.info("Ingresando credenciales...")
            username_input = self.page.wait_for_selector('//*[@id="P101_USERNAME"]')
            time.sleep(1.5)  # Pausa para simular comportamiento humano
            username_input.fill(self.user)

            password_input = self.page.wait_for_selector('//*[@id="P101_PASSWORD"]')
            time.sleep(1)  # Pausa para simular comportamiento humano
            password_input.fill(self.password)

            # Click en el botón de login
            logger.info("Enviando formulario...")
            time.sleep(1)  # Pausa para simular comportamiento humano
            login_button = self.page.wait_for_selector('//*[@id="B224579857434482981"]')
            login_button.click()
            self.page.wait_for_load_state("networkidle")

            # Verificar login exitoso
            logger.info("Verificando login exitoso...")
            self.page.wait_for_selector('//*[@id="224579043665482962"]/li[1]')

            if "login" in self.page.url:
                raise Exception("Login fallido - Redirigido de vuelta a la página de login")

            logger.info("Login exitoso en ERP")

        except Exception as e:
            logger.error(f"Error en login de ERP: {str(e)}")
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
            self.cleanup()
        except Exception as e:
            logger.error(f"Error en logout de ERP: {str(e)}")

    def cleanup(self) -> None:
        """Limpia los recursos de Playwright de manera segura."""
        try:
            if self.page and not self.page.is_closed():
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error durante la limpieza: {str(e)}")
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None

    def __del__(self):
        """Destructor para asegurar la limpieza de recursos."""
        self.cleanup()
