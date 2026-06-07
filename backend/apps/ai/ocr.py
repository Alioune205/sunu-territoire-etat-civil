import logging
import pytesseract
from PIL import Image
import io

import os

logger = logging.getLogger(__name__)

# Cross-platform compatibility for Tesseract
# In production (Linux), Tesseract is usually in the PATH.
tesseract_path = os.getenv('TESSERACT_CMD', None)
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
elif os.name == 'nt':
    # Fallback for Windows local development
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_file):
    """
    Extrait le texte brut d'un fichier image fourni (upload).
    """
    try:
        # Lire le fichier image en mémoire
        image = Image.open(image_file)
        
        # Optionnel: Prétraitements basiques (conversion en niveaux de gris)
        # image = image.convert('L')
        
        # Extraction du texte (langue française par défaut si installée)
        # On fallback sur l'anglais/défaut si le modèle 'fra' n'est pas présent
        try:
            text = pytesseract.image_to_string(image, lang='fra')
        except pytesseract.TesseractError:
            text = pytesseract.image_to_string(image)
            
        return text.strip()
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction OCR: {e}")
        return ""
