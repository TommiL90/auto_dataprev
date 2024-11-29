import logging
import pytesseract
from PIL import Image
import io

logger = logging.getLogger(__name__)


class CaptchaSolver:
    def __init__(self):
        # Configurar pytesseract si es necesario
        # pytesseract.pytesseract.tesseract_cmd = r'path_to_tesseract'
        pass

    def preprocess_image(self, image):
        """Preprocesa la imagen del captcha para mejorar el reconocimiento."""
        try:
            # Convertir bytes a imagen PIL
            img = Image.open(io.BytesIO(image))

            # Convertir a escala de grises
            img = img.convert("L")

            # Aumentar el contraste
            # Aquí puedes agregar más preprocesamiento según sea necesario

            return img

        except Exception as e:
            logger.error(f"Error en preprocesamiento de imagen: {str(e)}")
            raise

    def solve(self, image_bytes):
        """Resuelve el captcha usando OCR."""
        try:
            # Preprocesar imagen
            processed_image = self.preprocess_image(image_bytes)

            # Realizar OCR
            text = pytesseract.image_to_string(processed_image)

            # Limpiar resultado
            text = text.strip().replace(" ", "").upper()

            logger.info("Captcha resuelto exitosamente")
            return text

        except Exception as e:
            logger.error(f"Error resolviendo captcha: {str(e)}")
            raise
