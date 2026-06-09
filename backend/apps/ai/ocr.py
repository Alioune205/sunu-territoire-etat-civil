import logging
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import io
import re

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

def preprocess_image(image):
    image = image.convert('L')           # Niveaux de gris
    image = image.filter(ImageFilter.SHARPEN)  # Netteté
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)        # Contraste x2
    return image

def extract_text_from_image(image_file):
    """
    Extrait le texte brut d'un fichier image fourni (upload).
    """
    try:
        # Lire le fichier image en mémoire
        image = Image.open(image_file)
        
        # Prétraitements
        image = preprocess_image(image)
        
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

def extract_cni_data(image_file) -> dict:
    """
    Retourne :
    {
      "nom": "DIALLO",
      "prenom": "Moussa",
      "numero_cni": "1 2345 67890 12345",
      "date_naissance": "15/03/1990",
      "lieu_naissance": "Dakar",
      "date_expiration": "15/03/2030"
    }
    """
    text = extract_text_from_image(image_file)
    data = {
        "nom": "",
        "prenom": "",
        "numero_cni": "",
        "date_naissance": "",
        "lieu_naissance": "",
        "date_expiration": ""
    }
    
    # Expressions régulières basiques pour l'extraction CNI
    match_nom = re.search(r'(?:NOM|Nom)[\s:]*([A-Z]+)', text)
    if match_nom:
        data["nom"] = match_nom.group(1).strip()
        
    match_prenom = re.search(r'(?:PRENOM|Prenom|Prénom)[\s:]*([A-Z][a-z]+(?:[ -][A-Z][a-z]+)*)', text, re.IGNORECASE)
    if match_prenom:
        data["prenom"] = match_prenom.group(1).strip()
        
    match_cni = re.search(r'\b(\d{1}\s?\d{4}\s?\d{5}\s?\d{5})\b', text)
    if match_cni:
        data["numero_cni"] = match_cni.group(1).strip()
        
    match_dob = re.search(r'(?:Né\(e\) le|Date de naissance)[\s:]*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if not match_dob:
        match_dob = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', text)
    if match_dob:
        data["date_naissance"] = match_dob.group(1).strip()
        
    match_lieu = re.search(r'(?:à|Lieu de naissance)[\s:]*([A-Za-z]+)', text, re.IGNORECASE)
    if match_lieu:
        data["lieu_naissance"] = match_lieu.group(1).strip()
        
    match_exp = re.search(r'(?:Expire le|Date d\'expiration)[\s:]*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if match_exp:
        data["date_expiration"] = match_exp.group(1).strip()
        
    return data
