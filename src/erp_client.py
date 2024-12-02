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
        self.processed_cpfs = set()
        self.headless = False  # Agregar propiedad headless

    def _setup_browser(self) -> None:
        """Configura el navegador con los parámetros correctos."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                channel="chrome",  # Usar Chrome instalado en el sistema
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ],
            )
            self.context = self.browser.new_context(
                viewport={
                    "width": 1366,
                    "height": 768,
                },  # Resolución estándar de laptop
                user_agent=(
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
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
            # time.sleep(1.5)  # Pausa para simular comportamiento humano
            username_input.fill(self.user)

            password_input = self.page.wait_for_selector('//*[@id="P101_PASSWORD"]')
            # time.sleep(1)  # Pausa para simular comportamiento humano
            password_input.fill(self.password)

            # Click en el botón de login
            logger.info("Enviando formulario...")
            # time.sleep(1)  # Pausa para simular comportamiento humano
            login_button = self.page.wait_for_selector('//*[@id="B224579857434482981"]')
            login_button.click()
            self.page.wait_for_load_state("networkidle")

            # Verificar login exitoso
            logger.info("Verificando login exitoso...")
            self.page.wait_for_selector('//*[@id="224579043665482962"]/li[1]')

            if "login" in self.page.url:
                raise Exception(
                    "Login fallido - Redirigido de vuelta a la página de login"
                )

            logger.info("Login exitoso en ERP")

        except Exception as e:
            logger.error(f"Error en login de ERP: {str(e)}")
            raise

    def get_beneficiaries(self):
        """Obtiene la lista de beneficiarios del día."""
        try:
            # Navegar al menú de beneficiarios
            logger.info("Navegando al menú de beneficiarios...")

            self.page.click('//*[@id="t_MenuNav_0"]')
            logger.info("1")
            time.sleep(5)
            logger.info("2")

            # Esperar que todos los estados de carga se completen
            logger.info("Esperando carga completa de la página...")
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_load_state("load", timeout=30000)

            # Esperar que no haya solicitudes de red pendientes
            time.sleep(2)
            self.page.wait_for_load_state("networkidle", timeout=30000)

            # Verificar que el DOM esté estable
            self.page.evaluate(
                """() => {
                return new Promise((resolve) => {
                    const observer = new MutationObserver((mutations, obs) => {
                        obs.disconnect();
                        resolve(true);
                    });

                    observer.observe(document.body, {
                        childList: true,
                        subtree: true,
                        attributes: true,
                        characterData: true
                    });

                    // Si no hay cambios en 5 segundos, consideramos que el DOM está estable
                    setTimeout(() => {
                        observer.disconnect();
                        resolve(true);
                    }, 5000);
                });
            }"""
            )

            logger.info("2.1")

            logger.info("Haciendo click en el botón de navegación...")

            # Esperar a que el botón esté presente en el DOM
            button = self.page.locator('#t_Button_navControl')
            
            try:
                # Esperar a que el botón esté adjunto al DOM
                button.wait_for(state="attached", timeout=5000)
                logger.info("Botón encontrado en el DOM")
                
                # Click directo
                button.click(force=True, timeout=5000)
                logger.info("Click realizado")
                
                # Esperar a que el botón cambie de estado
                self.page.wait_for_selector('#t_Button_navControl[aria-expanded="true"]', timeout=5000)
                logger.info("Botón expandido correctamente")
                
            except Exception as e:
                logger.error(f"Error al interactuar con el botón: {str(e)}")
                self.page.screenshot(path="debug_nav_button_error.png")
                raise Exception("No se pudo activar el botón de navegación")

            # Ahora esperar a que el TreeView esté visible
            logger.info("Esperando que aparezca el TreeView...")
            try:
                self.page.wait_for_selector(
                    'div.a-TreeView#t_TreeNav[aria-hidden="false"]',
                    state="visible",
                    timeout=5000,
                )
                logger.info("TreeView encontrado y visible")
            except Exception as e:
                logger.error(f"TreeView no apareció o no está visible: {str(e)}")
                self.page.screenshot(path="debug_treeview.png")
                raise Exception("TreeView no apareció después del click")

            # Esperar un momento para que el DOM se estabilice
            time.sleep(2)

            # Click en el nodo Dataprev usando JavaScript
            logger.info("Haciendo click en el nodo Dataprev...")
            dataprev_clicked = self.page.evaluate(
                """() => {
                const node = document.getElementById('t_TreeNav_1');
                if (node) {
                    const toggle = node.querySelector('.a-TreeView-toggle');
                    if (toggle) {
                        toggle.click();
                        return true;
                    }
                }
                return false;
            }"""
            )

            if not dataprev_clicked:
                logger.error("No se pudo hacer click en el nodo Dataprev")
                self.page.screenshot(path="debug_dataprev.png")
                raise Exception("No se pudo expandir el nodo Dataprev")

            # Esperar a que el menú se expanda
            time.sleep(2)

            data_prev_button = self.page.wait_for_selector('//*[@id="t_TreeNav_1"]')
            logger.info("6")
            if not data_prev_button:
                # self.page.click('//*[@id="t_Button_navControl"]')
                time.sleep(1)
                data_prev_button = self.page.wait_for_selector('//*[@id="t_TreeNav_1"]')
            logger.info("7")
            data_prev_button.click()
            self.page.wait_for_load_state("networkidle")
            logger.info("8")
            time.sleep(5)
            # Pausa para simular comportamiento humano
            self.page.click('//*[@id="t_TreeNav_1"]')
            logger.info("4")
            time.sleep(1)
            self.page.click('//*[@id="t_TreeNav_2"]')
            self.page.wait_for_load_state("networkidle")

            # Esperar a que la tabla cargue
            logger.info("Esperando que la tabla cargue...")
            table = self.page.wait_for_selector(
                '//*[@id="36052098998664950_orig"]/tbody'
            )

            # Obtener todas las filas
            rows = table.query_selector_all("tr")
            beneficiaries = []
            today = time.strftime("%d/%m/%Y")

            logger.info(f"Procesando {len(rows)} filas de la tabla...")
            for row in rows:
                date_cell = row.query_selector("td:nth-child(9)")
                if not date_cell:
                    continue

                date_text = date_cell.inner_text().strip()

                if date_text == today:
                    cpf_cell = row.query_selector("td:nth-child(5)")
                    if not cpf_cell:
                        continue

                    cpf = cpf_cell.inner_text().strip()

                    if cpf not in self.processed_cpfs:
                        dialog_button = row.query_selector("td:nth-child(1) button")
                        if not dialog_button:
                            continue

                        dialog_id = dialog_button.get_attribute("id")
                        beneficiaries.append({"cpf": cpf, "dialog_id": dialog_id})

            logger.info(
                f"Encontrados {len(beneficiaries)} beneficiarios nuevos para hoy"
            )
            return beneficiaries

        except Exception as e:
            logger.error(f"Error obteniendo beneficiarios: {str(e)}")
            raise

    def process_beneficiary_details(self, beneficiary):
        """Procesa los detalles de un beneficiario específico."""
        try:
            logger.info(f"Procesando detalles para CPF: {beneficiary['cpf']}")

            # Click en el botón de diálogo
            self.page.click(f'#{beneficiary["dialog_id"]}')
            self.page.wait_for_selector(".modal-dialog")
            time.sleep(1)  # Esperar a que el diálogo se abra completamente

            # Obtener el número de beneficio
            benefit_number = self.page.inner_text(
                '//*[@id="P73_NUMERO_BENEFICIO_DISPLAY"]'
            ).strip()

            # Cerrar el diálogo
            self.page.click(".modal-dialog .close")
            time.sleep(0.5)  # Esperar a que el diálogo se cierre

            # Marcar el CPF como procesado
            self.processed_cpfs.add(beneficiary["cpf"])

            logger.info(f"Beneficio encontrado: {benefit_number}")
            return {"cpf": beneficiary["cpf"], "benefit_number": benefit_number}

        except Exception as e:
            logger.error(f"Error procesando detalles del beneficiario: {str(e)}")
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
