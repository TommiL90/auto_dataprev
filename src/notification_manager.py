import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class NotificationManager:
    @staticmethod
    def send_error_notification(subject, error_message):
        """Envía una notificación por correo cuando ocurre un error."""
        try:
            # Configuración del servidor SMTP
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = int(os.getenv("SMTP_PORT"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            recipient_email = os.getenv("NOTIFICATION_EMAIL")

            # Crear mensaje
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = recipient_email
            msg["Subject"] = f"Error en Automatización Dataprev: {subject}"

            # Cuerpo del mensaje
            body = f"""
            Se ha producido un error en la automatización Dataprev:

            Error: {subject}
            Detalles: {error_message}

            Por favor, revise los logs para más información.
            """
            msg.attach(MIMEText(body, "plain"))

            # Enviar correo
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            logger.info(f"Notificación de error enviada: {subject}")

        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")
            # No levantamos la excepción para evitar un ciclo de errores
