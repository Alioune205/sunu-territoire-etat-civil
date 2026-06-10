"""
Module OCR unifié — EasyOCR + support PDF via pypdfium2.

Sources acceptées :
  1. Image uploadée  (JPG, PNG, WEBP, BMP...)
  2. PDF uploadé     (toutes les pages sont analysées)
  3. Image base64    (capture caméra WebRTC depuis le frontend)
"""
import logging
import os
import re
import io
import base64
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Initialisation EasyOCR (une seule fois)
# ─────────────────────────────────────────────
ocr_model = None
try:
    import easyocr
    ocr_model = easyocr.Reader(['fr', 'en'], gpu=False)
    logger.info("EasyOCR initialisé avec succès.")
except Exception as e:
    ocr_model = None
    logger.error(f"EasyOCR n'a pas pu être initialisé : {e}")


# ─────────────────────────────────────────────
# Utilitaires internes
# ─────────────────────────────────────────────

def preprocess_image(image: Image.Image) -> Image.Image:
    """Améliore la qualité de l'image avant l'OCR."""
    image = image.convert('L')
    image = image.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    return image


def _run_ocr_on_pil(image: Image.Image) -> str:
    """Lance EasyOCR sur une image PIL et retourne le texte extrait."""
    if not ocr_model:
        return ""
    image = preprocess_image(image)
    image = image.convert('RGB')
    image_np = np.array(image)
    result = ocr_model.readtext(image_np)
    return "\n".join(text for (_, text, conf) in result if conf > 0.2)


def _is_pdf(file_obj) -> bool:
    """Détecte si un fichier est un PDF en lisant ses 4 premiers octets."""
    try:
        header = file_obj.read(4)
        file_obj.seek(0)
        return header == b'%PDF'
    except Exception:
        return False


def _extract_text_from_pdf(file_obj) -> str:
    """
    Extrait le texte de toutes les pages d'un PDF via pypdfium2 + EasyOCR.
    Chaque page est rendue en image haute résolution, puis analysée par OCR.
    """
    try:
        import pypdfium2 as pdfium
        pdf_bytes = file_obj.read()
        pdf = pdfium.PdfDocument(pdf_bytes)
        all_texts = []

        for page_index in range(len(pdf)):
            page = pdf[page_index]
            # Rendu à 200 DPI pour une bonne qualité OCR
            bitmap = page.render(scale=200 / 72)
            pil_image = bitmap.to_pil()
            page_text = _run_ocr_on_pil(pil_image)
            if page_text:
                all_texts.append(f"[Page {page_index + 1}]\n{page_text}")

        pdf.close()
        return "\n\n".join(all_texts).strip()

    except ImportError:
        logger.error("pypdfium2 n'est pas installé. Installez-le avec : pip install pypdfium2")
        return ""
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction PDF : {e}")
        return ""


# ─────────────────────────────────────────────
# Fonctions publiques
# ─────────────────────────────────────────────

def extract_text_from_file(file_obj) -> str:
    """
    Extrait le texte d'un fichier uploadé.
    Détecte automatiquement si c'est un PDF ou une image.
    Accepte : chemin str, InMemoryUploadedFile Django, ou BytesIO.
    """
    if not ocr_model:
        logger.error("EasyOCR n'est pas initialisé.")
        return ""
    try:
        # Si c'est un chemin string, on ouvre le fichier en binaire
        if isinstance(file_obj, str):
            with open(file_obj, 'rb') as f:
                content = f.read()
            file_like = io.BytesIO(content)
            if content[:4] == b'%PDF':
                return _extract_text_from_pdf(file_like)
            else:
                image = Image.open(file_like)
                return _run_ocr_on_pil(image)
        else:
            # C'est un file object (InMemoryUploadedFile ou BytesIO)
            if _is_pdf(file_obj):
                return _extract_text_from_pdf(file_obj)
            else:
                image = Image.open(file_obj)
                return _run_ocr_on_pil(image)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du fichier : {e}")
        return ""


# Alias rétrocompatible (ancienne signature)
def extract_text_from_image(image_file) -> str:
    return extract_text_from_file(image_file)


def extract_text_from_base64(base64_string: str) -> str:
    """
    Extrait le texte d'une image encodée en base64.
    Utilisé pour les captures caméra (WebRTC) depuis le frontend.
    Accepte le format data URI : data:image/jpeg;base64,/9j/...
    """
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]
        image_data = base64.b64decode(base64_string)
        image_file = io.BytesIO(image_data)
        return extract_text_from_file(image_file)
    except Exception as e:
        logger.error(f"Erreur décodage base64 : {e}")
        return ""


# ─────────────────────────────────────────────
# Extraction structurée des données CNI
# ─────────────────────────────────────────────

def _parse_cni_fields(text: str) -> dict:
    """
    Parse les champs structurés d'une CNI sénégalaise CEDEAO
    à partir du texte brut extrait par OCR.
    """
    data = {
        "nom": "",
        "prenom": "",
        "numero_cni": "",
        "date_naissance": "",
        "lieu_naissance": "",
        "date_expiration": ""
    }

    # --- NOM ---
    match = re.search(r'(?:^|\n)(?:NOM|Nom)\s*[:\n\r]+\s*([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜÇ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜÇ\s\-]+)', text, re.IGNORECASE | re.MULTILINE)
    if not match:
        match = re.search(r'(?:NOM|Nom)[\s:]+([A-Z][A-Z\s\-]+)', text, re.IGNORECASE)
    if match:
        data["nom"] = match.group(1).strip().split('\n')[0]

    # --- PRENOM ---
    match = re.search(r'(?:PRENOM|Prenom|Prénom|Prénoms)[\s:\n\r]+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜÇ][A-Za-zÀ-ÿ\s\-]+)', text, re.IGNORECASE)
    if match:
        data["prenom"] = match.group(1).strip().split('\n')[0]

    # --- NUMERO CNI (format sénégalais) ---
    match = re.search(r'\b(\d[\s]?\d{2}[\s]?\d{8}[\s]?\d{5})\b', text)
    if match:
        data["numero_cni"] = match.group(1).strip()

    # --- DATES ---
    dates = re.findall(r'\b(\d{2}/\d{2}/\d{4})\b', text)

    match_dob = re.search(r'(?:Date de naissance|Né\(e\) le)[\s:\n\r]+(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if match_dob:
        data["date_naissance"] = match_dob.group(1).strip()
    elif dates:
        data["date_naissance"] = dates[0]

    match_exp = re.search(r"(?:Expire le|Date.{0,10}expiration|dexpiration|d'expiration)[\s:\n\r]+(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
    if match_exp:
        data["date_expiration"] = match_exp.group(1).strip()
    elif len(dates) >= 2:
        data["date_expiration"] = dates[-1]

    # --- LIEU DE NAISSANCE ---
    match = re.search(r'(?:Lieu de naissance|Lleu de naissance)[\s:\n\r]+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜÇ][A-Za-zÀ-ÿ\s\-]+)', text, re.IGNORECASE)
    if match:
        data["lieu_naissance"] = match.group(1).strip().split('\n')[0]

    return data


def extract_cni_data(file_obj) -> dict:
    """Extrait les données structurées d'une CNI depuis un fichier image ou PDF."""
    text = extract_text_from_file(file_obj)
    return _parse_cni_fields(text)


def extract_cni_data_from_base64(base64_string: str) -> dict:
    """Extrait les données structurées d'une CNI depuis une image base64 (caméra)."""
    text = extract_text_from_base64(base64_string)
    return _parse_cni_fields(text)
