import tkinter as tk
import threading
import time
import pystray
from PIL import Image, ImageDraw


class AutomationGUI:
    def __init__(self):
        self.setup_gui()
        self.is_running = False
        self.setup_tray()

    def setup_gui(self):
        """Configura la interfaz gráfica"""
        self.root = tk.Tk()
        self.root.title("Auto Dataprev")
        self.root.geometry("300x250")

        # Frame para los botones
        button_frame = tk.Frame(self.root)
        button_frame.pack(expand=True)

        # Botón de inicio
        self.start_button = tk.Button(
            button_frame,
            text="Iniciar Script",
            width=15,
            height=2,
            command=self.start_automation,
        )
        self.start_button.pack(pady=10)

        # Botón de parada
        self.stop_button = tk.Button(
            button_frame,
            text="Parar Script",
            width=15,
            height=2,
            command=self.stop_automation,
            state=tk.DISABLED,
        )
        self.stop_button.pack(pady=10)

        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    def setup_tray(self):
        """Configura el ícono de la bandeja del sistema"""
        # Crear imagen para el ícono
        image = Image.new("RGB", (64, 64), color="red")
        dc = ImageDraw.Draw(image)
        dc.rectangle([16, 16, 48, 48], fill="white")

        # Crear menú
        menu = (
            pystray.MenuItem("Mostrar", self.show_window),
            pystray.MenuItem("Iniciar", self.start_automation),
            pystray.MenuItem("Parar", self.stop_automation),
            pystray.MenuItem("Salir", self.quit_app),
        )

        # Crear ícono
        self.icon = pystray.Icon("auto_dataprev", image, "Auto Dataprev", menu)

    def show_window(self, icon=None, item=None):
        """Muestra la ventana principal"""
        self.icon.stop()
        self.root.after(0, self.root.deiconify)

    def hide_window(self):
        """Oculta la ventana principal"""
        self.root.withdraw()
        threading.Thread(target=self.icon.run, daemon=True).start()

    def start_automation(self, icon=None, item=None):
        """Inicia la automatización"""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Iniciar thread de automatización
            self.automation_thread = threading.Thread(target=self.run_automation)
            self.automation_thread.daemon = True
            self.automation_thread.start()
            print("Script iniciado")

    def stop_automation(self, icon=None, item=None):
        """Detiene la automatización"""
        if self.is_running:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            print("Script detenido")

    def run_automation(self):
        """Función principal de automatización"""
        while self.is_running:
            print("Script ejecutándose...")
            time.sleep(30)

    def quit_app(self, icon=None, item=None):
        """Cierra la aplicación"""
        self.stop_automation()
        if icon:
            icon.stop()
        self.root.after(0, self.root.destroy)

    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()


def main():
    app = AutomationGUI()
    app.run()


if __name__ == "__main__":
    main()
