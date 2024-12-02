import os
import logging
import time
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class DataprevClient:
    def __init__(self):
        self.url = os.getenv("DATAPREV_URL")
        self.user = os.getenv("DATAPREV_USER")
        self.password = os.getenv("DATAPREV_PASSWORD")
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
        """Inicia sesión en Dataprev."""
        try:
            if not self.browser:
                self._setup_browser()

            # Navegar a la página inicial
            logger.info(f"Navegando a {self.url}")
            self.page.goto(self.url, wait_until="networkidle")

            # Esperar y llenar credenciales
            logger.info("Ingresando credenciales...")
            username_input = self.page.wait_for_selector('input[name="username"]')
            time.sleep(1.5)  # Pausa para simular comportamiento humano
            username_input.fill(self.user)

            password_input = self.page.wait_for_selector('input[name="password"]')
            time.sleep(1)  # Pausa para simular comportamiento humano
            password_input.fill(self.password)

            # Click en el botón de login
            logger.info("Enviando formulario...")
            time.sleep(1)  # Pausa para simular comportamiento humano
            login_button = self.page.wait_for_selector('button[type="submit"]')
            login_button.click()
            self.page.wait_for_load_state("networkidle")

            # Verificar login exitoso
            logger.info("Verificando login exitoso...")
            # Ajustar este selector según la página de Dataprev
            self.page.wait_for_selector('.dashboard-container')

            if "login" in self.page.url:
                raise Exception(
                    "Login fallido - Redirigido de vuelta a la página de login"
                )

            logger.info("Login exitoso en Dataprev")

        except Exception as e:
            logger.error(f"Error en login de Dataprev: {str(e)}")
            raise

    def check_benefit(self, cpf: str, benefit_number: str) -> dict:
        """Consulta el estado de un beneficio específico."""
        try:
            # Navegar a la página de consulta
            logger.info("Navegando a la página de consulta...")
            self.page.click('a[href="/consulta"]')
            self.page.wait_for_load_state("networkidle")

            # Llenar formulario de consulta
            logger.info(f"Consultando beneficio {benefit_number} para CPF {cpf}")
            
            cpf_input = self.page.wait_for_selector('input[name="cpf"]')
            time.sleep(1)
            cpf_input.fill(cpf)

            benefit_input = self.page.wait_for_selector('input[name="benefit_number"]')
            time.sleep(1)
            benefit_input.fill(benefit_number)

            # Enviar consulta
            submit_button = self.page.wait_for_selector('button[type="submit"]')
            time.sleep(1)
            submit_button.click()
            self.page.wait_for_load_state("networkidle")

            # Extraer resultado
            result = {
                "cpf": cpf,
                "benefit_number": benefit_number,
                "status": self.page.text_content('.benefit-status'),
                "details": self.page.text_content('.benefit-details'),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            return result

        except Exception as e:
            logger.error(f"Error consultando beneficio: {str(e)}")
            raise

    def logout(self):
        """Cierra la sesión y el navegador."""
        try:
            if self.page:
                logout_button = self.page.wait_for_selector('a[href="/logout"]')
                logout_button.click()
                self.page.wait_for_load_state("networkidle")
            self.cleanup()
        except Exception as e:
            logger.error(f"Error en logout de Dataprev: {str(e)}")

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
