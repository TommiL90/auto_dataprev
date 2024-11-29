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

            # Click en el link para ir al login
            logger.info("Haciendo click en el link de login...")
            login_link = self.page.wait_for_selector(
                '//*[@id="x7cbbd46c873e0210cefaa8630cbb35dd"]/div/div[1]/div/div[2]/a'
            )
            time.sleep(2)  # Pausa para simular comportamiento humano
            login_link.click()
            self.page.wait_for_load_state("networkidle")

            # Esperar y llenar el campo de usuario
            logger.info("Ingresando usuario...")
            account_input = self.page.wait_for_selector('//*[@id="accountId"]')
            time.sleep(1.5)  # Pausa para simular comportamiento humano
            account_input.fill(self.user)

            # Click en el botón para continuar
            time.sleep(1)  # Pausa para simular comportamiento humano
            continue_button = self.page.wait_for_selector('//*[@id="enter-account-id"]')
            continue_button.click()
            self.page.wait_for_load_state("networkidle")

            # Esperar a que el usuario resuelva el captcha manualmente
            logger.info("Esperando resolución manual del captcha...")
            password_input = self.page.wait_for_selector(
                '//*[@id="password"]', timeout=120000
            )  # 2 minutos máximo

            # Una vez resuelto el captcha, esperar y llenar la contraseña
            logger.info("Ingresando contraseña...")
            time.sleep(1.5)  # Pausa para simular comportamiento humano
            password_input.fill(self.password)

            # Click en el botón de submit
            time.sleep(1)  # Pausa para simular comportamiento humano
            submit_button = self.page.wait_for_selector('//*[@id="submit-button"]')
            submit_button.click()
            self.page.wait_for_load_state("networkidle")

            # Verificar login exitoso esperando el elemento del dashboard
            logger.info("Verificando login exitoso...")
            self.page.wait_for_selector('//*[@id="sp-nav-bar"]/ul[2]/li[1]')
            logger.info("Login exitoso en Dataprev")

        except Exception as e:
            logger.error(f"Error en login de Dataprev: {str(e)}")
            raise

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

    def check_eligibility(self, beneficiary_data):
        """Verifica la elegibilidad de un beneficiario."""
        try:
            # Navegar a la página de solicitud
            self.page.goto(f"{self.url}/solicitar-adesao")

            # Llenar formulario con datos del beneficiario
            self.page.fill("#cpf", beneficiary_data["cpf"])
            self.page.fill("#nome", beneficiary_data["nome"])
            # ... llenar otros campos necesarios

            # Enviar formulario
            self.page.click("#verificar-button")

            # Esperar resultado
            self.page.wait_for_selector(".resultado-verificacao")

            # Obtener resultado
            is_eligible = self.page.query_selector(".elegivel") is not None
            status = "ELIGIBLE" if is_eligible else "INELIGIBLE"

            return {"is_eligible": is_eligible, "status": status}

        except Exception as e:
            logger.error(f"Error verificando elegibilidad: {str(e)}")
            raise

    def get_registration_link(self, beneficiary_data):
        """Obtiene el enlace de registro para un beneficiario elegible."""
        try:
            # Implementar lógica para obtener el enlace
            link_element = self.page.query_selector(".link-registro")
            link = link_element.get_attribute("href")
            return link
        except Exception as e:
            logger.error(f"Error obteniendo enlace de registro: {str(e)}")
            raise

    def logout(self):
        """Cierra la sesión y el navegador."""
        try:
            if self.page:
                self.page.click("#logout-button")
            self.cleanup()
        except Exception as e:
            logger.error(f"Error en logout de Dataprev: {str(e)}")
