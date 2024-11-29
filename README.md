# Automatización Dataprev

Este proyecto automatiza la interacción entre el sistema Dataprev y el ERP Cliente para la gestión de beneficiarios.

## Requisitos Previos

- Python 3.10 o superior
- Tesseract OCR instalado en el sistema
- Credenciales de acceso para Dataprev y ERP
- Configuración de correo SMTP para notificaciones

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd auto_dataprev
```

2. Crear un entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Instalar Tesseract OCR:
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`
- Windows: Descargar el instalador desde [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

4. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```env
# Credenciales Dataprev
DATAPREV_URL=https://pdma.dataprev.gov.br/pdma
DATAPREV_USER=your_user
DATAPREV_PASSWORD=your_password

# Credenciales ERP
ERP_URL=http://exacttus.cebap.org.br
ERP_USER=your_user
ERP_PASSWORD=your_password

# Configuración de correo para notificaciones
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=recipient@example.com
```

## Uso

1. Activar el entorno virtual:
```bash
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Ejecutar el script:
```bash
python main.py
```

El script se ejecutará automáticamente cada 30 minutos y:
- Verificará nuevos beneficiarios en el ERP
- Consultará su elegibilidad en Dataprev
- Actualizará su estado en el ERP
- Enviará notificaciones por correo en caso de errores

## Estructura del Proyecto

```
auto_dataprev/
├── main.py                 # Script principal
├── requirements.txt        # Dependencias del proyecto
├── .env                    # Variables de entorno
├── automation.log         # Archivo de logs
└── src/
    ├── dataprev_client.py    # Cliente para Dataprev
    ├── erp_client.py         # Cliente para ERP
    ├── notification_manager.py # Gestor de notificaciones
    └── captcha_solver.py     # Solucionador de captchas
```

## Logs y Monitoreo

Los logs se guardan en `automation.log`. En caso de errores, se enviará una notificación por correo electrónico al destinatario configurado.

## Solución de Problemas

1. Si hay problemas con el reconocimiento de captchas:
   - Verificar la instalación de Tesseract
   - Ajustar el preprocesamiento de imágenes en `captcha_solver.py`

2. Si hay problemas de conexión:
   - Verificar las URLs en el archivo `.env`
   - Confirmar acceso a internet
   - Verificar que las credenciales sean correctas

3. Si hay problemas con las notificaciones:
   - Verificar la configuración SMTP
   - Confirmar que el servidor de correo permite el acceso de la aplicación

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
