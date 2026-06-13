"""
pdf_generator.py — Génération de certificats officiels avec liaison cryptographique
====================================================================================
Processus en 5 étapes :
  1. Dessiner le PDF avec ReportLab (texte, cachets SVG, signature SVG, timbre)
  2. Calculer le SHA-256 du PDF brut
  3. Construire le payload canonique (données + pdf_hash)
  4. Signer le payload avec HMAC-SHA256
  5. Générer le QR Code pointant vers l'endpoint de vérification publique
  6. Re-générer le PDF final avec le QR Code inclus
"""
import os
import io
import logging
from io import BytesIO

import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import hashlib

from django.conf import settings
from django.core.files.base import ContentFile

from apps.documents.models import GeneratedCertificate, TimbreFiscal
from apps.documents.crypto import compute_pdf_hash, build_payload, sign_payload

logger = logging.getLogger(__name__)

# Répertoire des assets (cachets, signatures)
ASSETS_DIR = os.path.join(settings.BASE_DIR, 'assets', 'seals')


def _try_draw_svg(c, svg_path, x, y, width, height):
    """
    Tente de dessiner un fichier SVG sur le canvas ReportLab.
    Fallback silencieux si le fichier n'existe pas ou si svglib échoue.
    """
    if not svg_path or not os.path.exists(svg_path):
        logger.warning(f"[PDF] Fichier SVG introuvable: {svg_path}")
        return False
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
        drawing = svg2rlg(svg_path)
        if drawing:
            # Redimensionner le dessin
            sx = width / drawing.width
            sy = height / drawing.height
            scale = min(sx, sy)
            drawing.width = drawing.width * scale
            drawing.height = drawing.height * scale
            drawing.scale(scale, scale)
            renderPDF.draw(drawing, c, x, y)
            return True
    except Exception as e:
        logger.warning(f"[PDF] Erreur rendu SVG {svg_path}: {e}")
    return False


def _try_draw_image(c, img_path, x, y, width, height):
    """
    Tente de dessiner un fichier image (PNG/JPG) sur le canvas.
    Fallback silencieux si le fichier n'existe pas.
    """
    if not img_path or not os.path.exists(img_path):
        return False
    try:
        c.drawImage(img_path, x, y, width=width, height=height, mask='auto')
        return True
    except Exception as e:
        logger.warning(f"[PDF] Erreur rendu image {img_path}: {e}")
    return False


def _draw_seal(c, path, x, y, size):
    """Dessine un cachet (SVG ou PNG) à la position donnée."""
    if path and path.endswith('.svg'):
        if not _try_draw_svg(c, path, x, y, size, size):
            _draw_placeholder_seal(c, x, y, size, "CACHET")
    elif path:
        if not _try_draw_image(c, path, x, y, size, size):
            _draw_placeholder_seal(c, x, y, size, "CACHET")
    else:
        _draw_placeholder_seal(c, x, y, size, "CACHET")


def _draw_placeholder_seal(c, x, y, size, label):
    """Dessine un cercle pointillé comme placeholder de cachet."""
    cx = x + size / 2
    cy = y + size / 2
    c.saveState()
    c.setStrokeColor(HexColor('#999999'))
    c.setDash(3, 3)
    c.circle(cx, cy, size / 2 - 2, stroke=1, fill=0)
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor('#999999'))
    c.drawCentredString(cx, cy - 3, f"[{label}]")
    c.restoreState()


def _generate_raw_pdf(dossier, officier, timbre_ref, cachet_path, signature_path, cachet_nominal_path):
    """
    Génère le contenu PDF brut (SANS QR Code).
    On génère d'abord sans QR pour pouvoir hasher le contenu,
    puis on re-génère avec le QR.
    """
    buffer = BytesIO()
    pagesize = landscape(A4) if dossier.type == 'residence_certificate' else A4
    p = canvas.Canvas(buffer, pagesize=pagesize)
    width, height = pagesize

    if dossier.type == 'residence_certificate':
        _draw_residence_pdf_content(p, width, height, dossier, officier, timbre_ref,
                          cachet_path, signature_path, cachet_nominal_path, qr_image_reader=None)
    elif dossier.type == 'marriage_certificate':
        _draw_mariage_pdf_content(p, width, height, dossier, officier, timbre_ref,
                          cachet_path, signature_path, cachet_nominal_path, qr_image_reader=None)
    elif dossier.type == 'death_certificate':
        _draw_deces_pdf_content(p, width, height, dossier, officier, timbre_ref,
                          cachet_path, signature_path, cachet_nominal_path, qr_image_reader=None)
    else:
        _draw_pdf_content(p, width, height, dossier, officier, timbre_ref,
                          cachet_path, signature_path, cachet_nominal_path, qr_image_reader=None)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


def _generate_final_pdf(dossier, officier, timbre_ref, cachet_path,
                        signature_path, cachet_nominal_path, verification_url):
    """
    Génère le PDF final AVEC le QR Code de vérification.
    """
    # Générer le QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")

    qr_buffer = BytesIO()
    img_qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image_reader = ImageReader(qr_buffer)

    # Générer le PDF final
    buffer = BytesIO()
    pagesize = landscape(A4) if dossier.type == 'residence_certificate' else A4
    p = canvas.Canvas(buffer, pagesize=pagesize)
    width, height = pagesize

    if dossier.type == 'residence_certificate':
        _draw_residence_pdf_content(p, width, height, dossier, officier, timbre_ref,
                          cachet_path, signature_path, cachet_nominal_path, qr_image_reader)
    elif dossier.type == 'marriage_certificate':
        _draw_mariage_pdf_content(p, width, height, dossier, officier, timbre_ref,
                          cachet_path, signature_path, cachet_nominal_path, qr_image_reader)
    elif dossier.type == 'death_certificate':
        _draw_deces_pdf_content(p, width, height, dossier, officier, timbre_ref,
                          cachet_path, signature_path, cachet_nominal_path, qr_image_reader)
    else:
        _draw_pdf_content(p, width, height, dossier, officier, timbre_ref,
                          cachet_path, signature_path, cachet_nominal_path, qr_image_reader)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


def _draw_residence_pdf_content(p, width, height, dossier, officier, timbre_ref,
                                cachet_path, signature_path, cachet_nominal_path, qr_image_reader):
    """Dessine le certificat de résidence au format A4 Paysage."""
    VERT = HexColor('#00853F')
    NOIR = HexColor('#000000')
    BLEU_FONCE = HexColor('#0F172A')
    ROUGE = HexColor('#E31B23')

    metadata = dossier.metadata or {}
    citizen = dossier.citizen

    # En-tête gauche
    y = height - 2 * cm
    p.setFillColor(NOIR)
    p.setFont("Helvetica-Bold", 11)
    p.drawCentredString(5 * cm, y, "Un Peuple - Un But - Une Foi")
    y -= 0.6 * cm
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(BLEU_FONCE)
    region = dossier.commune.region if dossier.commune and dossier.commune.region else "DAKAR"
    p.drawCentredString(5 * cm, y, f"REGION DE {region.upper()}")
    y -= 0.5 * cm
    p.setFont("Helvetica-Bold", 11)
    commune_name = dossier.commune.name if dossier.commune else "INCONNUE"
    p.drawCentredString(5 * cm, y, "COMMUNE D'ARRONDISSEMENT DES")
    y -= 0.5 * cm
    p.drawCentredString(5 * cm, y, commune_name.upper())

    # Titre droit
    p.setFont("Helvetica-Bold", 26)
    p.setFillColor(BLEU_FONCE)
    p.drawString(14 * cm, height - 3 * cm, "CERTIFICAT DE RESIDENCE")
    p.setStrokeColor(NOIR)
    p.setLineWidth(1)
    p.line(18.5 * cm, height - 3.4 * cm, 23.5 * cm, height - 3.4 * cm)

    # Référence
    y_ref = height - 5 * cm
    p.setFont("Helvetica", 14)
    p.setFillColor(NOIR)
    p.drawString(15 * cm, y_ref, f"N° Pièce portée : {dossier.reference}")

    # Données
    prenoms = metadata.get('prenoms_requerant') or (citizen.first_name if citizen else "")
    nom = metadata.get('nom_requerant') or (citizen.last_name if citizen else "")
    nom_complet = f"{prenoms} {nom}".strip()
    date_naissance = metadata.get('date_naissance') or (str(citizen.profile.date_of_birth) if citizen and hasattr(citizen, 'profile') else "")
    lieu_naissance = metadata.get('lieu_naissance') or (citizen.profile.place_of_birth if citizen and hasattr(citizen, 'profile') else "")
    adresse = metadata.get('adresse') or (citizen.profile.address if citizen and hasattr(citizen, 'profile') else "")
    quartier = metadata.get('quartier', '')
    date_installation = metadata.get('date_installation', '')

    # --- 4. CORPS DU TEXTE ---
    TEXT_X = 3 * cm
    TEXT_Y = height - 11.5 * cm
    TEXT_W = width - 6 * cm
    TEXT_H = 5 * cm

    style_center = ParagraphStyle(
        name='Center', fontName='Helvetica', fontSize=19, leading=28, alignment=TA_CENTER
    )
    
    texte_complet = (
        f"Nous soussigné(e) Maire de la Commune de {commune_name.capitalize()} certifions "
        f"que {nom_complet} né(e) le {date_naissance} à {lieu_naissance} et qu'il (elle) "
        f"réside à {adresse} au quartier {quartier} depuis {date_installation}."
    )
    
    para = Paragraph(texte_complet, style_center)
    para.wrap(TEXT_W, TEXT_H)
    para.drawOn(p, TEXT_X, TEXT_Y)

    # --- 5. CADRE ETAT CIVIL ---
    CADRE_W = 8.5 * cm
    CADRE_H = 4.5 * cm
    CADRE_X = 2 * cm
    CADRE_Y = 4 * cm 

    p.setDash([3, 3], 0)
    p.setLineWidth(1.5)
    p.setStrokeColor(NOIR)
    p.roundRect(CADRE_X, CADRE_Y, CADRE_W, CADRE_H, 5, fill=0)
    p.setDash([], 0)
    
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(CADRE_X + 3.5*cm, CADRE_Y + 3.8*cm, "REPUBLIQUE DU SENEGAL")
    p.setFont("Helvetica-Bold", 7)
    p.drawCentredString(CADRE_X + 3.5*cm, CADRE_Y + 3.4*cm, "COMMUNE DE")
    p.drawCentredString(CADRE_X + 3.5*cm, CADRE_Y + 3.1*cm, commune_name.upper().replace("COMMUNE DE ", "").replace("COMMUNE DES ", ""))
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(CADRE_X + 3.5*cm, CADRE_Y + 2.4*cm, "ETAT CIVIL")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(CADRE_X + 0.5*cm, CADRE_Y + 1*cm, "S/D")
    p.setDash([1, 2], 0)
    p.setLineWidth(1)
    p.line(CADRE_X + 1.5*cm, CADRE_Y + 1*cm, CADRE_X + 3.5*cm, CADRE_Y + 1*cm)
    p.setDash([], 0)
    p.drawString(CADRE_X + 4*cm, CADRE_Y + 1*cm, "N°")
    p.setDash([1, 2], 0)
    p.line(CADRE_X + 4.5*cm, CADRE_Y + 1*cm, CADRE_X + 6*cm, CADRE_Y + 1*cm)
    p.setDash([], 0)

    # --- 6. TIMBRE FISCAL (INTÉRIEUR DU CADRE) ---
    TIMBRE_W = 1.5 * cm
    TIMBRE_H = 2 * cm
    TIMBRE_X = CADRE_X + CADRE_W - TIMBRE_W - 0.5 * cm
    TIMBRE_Y = CADRE_Y + CADRE_H - TIMBRE_H - 0.5 * cm
    _draw_secure_timbre(p, TIMBRE_X, TIMBRE_Y, timbre_ref)

    # --- 7. BLOC SIGNATURE ---
    SIG_TEXT_W = 8 * cm
    SIG_TEXT_H = 2.5 * cm
    SIG_TEXT_X = 14 * cm
    SIG_TEXT_Y = 6.5 * cm

    p.setFont("Helvetica", 14)
    p.setFillColor(NOIR)
    date_str = dossier.updated_at.strftime("%d/%m/%Y") if dossier.updated_at else ""
    p.drawCentredString(SIG_TEXT_X + SIG_TEXT_W/2, SIG_TEXT_Y + 1.5*cm, f"Fait à {commune_name.capitalize()}, le {date_str}")
    p.drawCentredString(SIG_TEXT_X + SIG_TEXT_W/2, SIG_TEXT_Y + 0.5*cm, "P. le Maire et P.O")
    p.drawCentredString(SIG_TEXT_X + SIG_TEXT_W/2, SIG_TEXT_Y, "l'Officier de l'Etat Civil")

    # Image Signature
    SIG_IMG_W = 4 * cm
    SIG_IMG_H = 2 * cm
    SIG_IMG_X = SIG_TEXT_X + SIG_TEXT_W/2 - SIG_IMG_W/2
    SIG_IMG_Y = SIG_TEXT_Y - SIG_IMG_H - 0.2*cm
    
    # Cachet Nominal (à côté de la signature)
    CACHET_NOM_W = 3.5 * cm
    CACHET_NOM_H = 1.5 * cm
    CACHET_NOM_X = SIG_IMG_X - CACHET_NOM_W - 0.2*cm
    CACHET_NOM_Y = SIG_IMG_Y + 0.2*cm
    
    if cachet_nominal_path and os.path.exists(cachet_nominal_path):
        p.drawImage(ImageReader(cachet_nominal_path), CACHET_NOM_X, CACHET_NOM_Y, width=CACHET_NOM_W, height=CACHET_NOM_H, mask='auto')

    if signature_path and os.path.exists(signature_path):
        p.drawImage(ImageReader(signature_path), SIG_IMG_X, SIG_IMG_Y, width=SIG_IMG_W, height=SIG_IMG_H, mask='auto')
    
    # --- 8. CACHET ROND ---
    # Doit être à DROITE du bloc signature
    CACHET_ROND_W = 4.5 * cm
    CACHET_ROND_H = 4.5 * cm
    CACHET_ROND_X = SIG_TEXT_X + SIG_TEXT_W + 0.5 * cm
    CACHET_ROND_Y = SIG_IMG_Y - 0.5*cm
    
    if cachet_path and os.path.exists(cachet_path):
        p.drawImage(ImageReader(cachet_path), CACHET_ROND_X, CACHET_ROND_Y, width=CACHET_ROND_W, height=CACHET_ROND_H, mask='auto')

    # --- 9. QR CODE & TEXTE ---
    QR_W = 2.5 * cm
    QR_H = 2.5 * cm
    QR_X = width / 2 - QR_W / 2
    QR_Y = 1.5 * cm # 1.5cm marge depuis le bas de page
    
    QR_TEXT_Y = QR_Y - 0.5 * cm # Texte sous le QR
    
    if qr_image_reader:
        p.drawImage(qr_image_reader, QR_X, QR_Y, width=QR_W, height=QR_H)
    else:
        # Placeholder fonctionnel pour le test sans API complète
        hash_content = f"{dossier.reference}{nom_complet}{date_naissance}{commune_name}".encode('utf-8')
        doc_hash = hashlib.sha256(hash_content).hexdigest()
        qr_data = f"https://teranga-civil.sn/verify/{doc_hash}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        img_qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        p.drawImage(ImageReader(qr_buffer), QR_X, QR_Y, width=QR_W, height=QR_H)

    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, QR_TEXT_Y + 0.1*cm, "Scannez pour vérifier l'authenticité de ce document")

def _draw_mariage_pdf_content(p, width, height, dossier, officier, timbre_ref,
                              cachet_path, signature_path, cachet_nominal_path, qr_image_reader):
    """Dessine le certificat de mariage au format A4 Portrait."""
    NOIR = HexColor('#000000')
    VERT = HexColor('#00853F')
    
    metadata = dossier.metadata or {}
    commune_name = dossier.commune.name if dossier.commune else "INCONNUE"
    region_name = dossier.commune.region if dossier.commune and dossier.commune.region else "DAKAR"
    officier_name = officier.full_name if officier else "L'Officier de l'État Civil"
    
    registre_no = metadata.get('registre_marriage') or metadata.get('registre', 'N/A')
    annee_marriage = metadata.get('annee_marriage', 'N/A')
    
    # Rendu des textes
    style_normal = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=12, leading=16)

    p.setFillColor(NOIR)
    
    # En-tête gauche
    p.setFont("Helvetica-Bold", 10)
    p.drawString(2 * cm, height - 2 * cm, f"REGION DE {region_name.upper()}")
    p.drawString(2 * cm, height - 2.5 * cm, "VILLE DE DAKAR") # TODO: rendre dynamique selon région
    p.drawString(2 * cm, height - 3 * cm, "COMMUNE D'ARRONDISSEMENT")
    p.drawString(2 * cm, height - 3.5 * cm, f"DE {commune_name.upper()}")
    p.drawString(2 * cm, height - 4 * cm, "CENTRE D'ÉTAT CIVIL")
    
    # En-tête droit
    p.setFont("Helvetica-Bold", 10)
    p.drawString(14 * cm, height - 2 * cm, "REPUBLIQUE DU SENEGAL")
    p.setFont("Helvetica", 10)
    p.drawString(14 * cm, height - 2.5 * cm, "Un Peuple - Un But - Une Foi")

    # Informations Registre
    y_reg = height - 6.5 * cm
    p.setFont("Helvetica-Bold", 11)
    p.drawString(2 * cm, y_reg, f"Registre N° {registre_no}")
    
    p.setFont("Helvetica", 11)
    p.drawString(2 * cm, y_reg - 0.7 * cm, f"L'an {annee_marriage},")
    p.drawString(2 * cm, y_reg - 1.4 * cm, "Date d'enregistrement non précisée.")

    # Titre
    y_titre = height - 9.5 * cm
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y_titre, "CERTIFICAT DE MARIAGE CONSTATÉ")

    # Corps du texte
    y_body = y_titre - 1.5 * cm
    
    para_intro = Paragraph(
        f"Nous, <b>{officier_name}</b>, Officier d'État civil du <b>CENTRE D'ÉTAT CIVIL DE {commune_name.upper()}</b>, certifions à tous ceux "
        "qu'il appartiendra que :", style_normal)
    para_intro.wrap(width - 4 * cm, 5 * cm)
    para_intro.drawOn(p, 2 * cm, y_body - para_intro.height)
    y_body -= para_intro.height + 0.8 * cm

    # Mari
    mari_nom = metadata.get('nom_epoux', 'Nom non précisé')
    mari_prof = metadata.get('profession_epoux', 'Non précisée')
    mari_domicile = metadata.get('domicile_epoux', 'Non précisé')
    mari_date_naiss = metadata.get('date_naissance_epoux', 'Non précisée')
    mari_lieu_naiss = metadata.get('lieu_naissance_epoux', 'Non précisé')
    mari_pere = metadata.get('prenom_pere_epoux', 'Non précisé')
    mari_mere = metadata.get('prenom_mere_epoux', 'Non précisé')

    mari_text = (
        f"<b>Monsieur {mari_nom},</b><br/>"
        f"Profession : <b>{mari_prof}</b>, domicilié à <b>{mari_domicile}</b>,<br/>"
        f"Né le {mari_date_naiss} à {mari_lieu_naiss},<br/>"
        f"Fils de <b>{mari_pere}</b> et de <b>{mari_mere}</b>,<br/>"
        "D'une part,"
    )
    para_mari = Paragraph(mari_text, style_normal)
    para_mari.wrap(width - 4 * cm, 5 * cm)
    para_mari.drawOn(p, 2 * cm, y_body - para_mari.height)
    y_body -= para_mari.height + 0.5 * cm
    
    p.drawString(2 * cm, y_body, "Et")
    y_body -= 0.8 * cm

    # Epouse
    epouse_nom = metadata.get('nom_epouse', 'Nom non précisé')
    epouse_prof = metadata.get('profession_epouse', 'Non précisée')
    epouse_domicile = metadata.get('domicile_epouse', 'Non précisée')
    epouse_date_naiss = metadata.get('date_naissance_epouse', 'Non précisée')
    epouse_lieu_naiss = metadata.get('lieu_naissance_epouse', 'Non précisé')
    epouse_pere = metadata.get('prenom_pere_epouse', 'Non précisé')
    epouse_mere = metadata.get('prenom_mere_epouse', 'Non précisé')

    epouse_text = (
        f"<b>Mademoiselle {epouse_nom},</b><br/>"
        f"Profession : <b>{epouse_prof}</b>, domiciliée à <b>{epouse_domicile}</b>,<br/>"
        f"Née le <b>{epouse_date_naiss}</b> à {epouse_lieu_naiss},<br/>"
        f"Fille de <b>{epouse_pere}</b> et de <b>{epouse_mere}</b>,<br/>"
        "D'autre part,"
    )
    para_epouse = Paragraph(epouse_text, style_normal)
    para_epouse.wrap(width - 4 * cm, 5 * cm)
    para_epouse.drawOn(p, 2 * cm, y_body - para_epouse.height)
    y_body -= para_epouse.height + 0.8 * cm

    # Conclusion
    date_marriage = metadata.get('date_marriage', 'Non précisée')
    option = metadata.get('option_souscrite', 'Monogamie')
    regime = metadata.get('regime_matrimonial', 'séparation des biens')

    concl_text = (
        f"Ont contracté mariage entre eux selon la coutume, <b>le {date_marriage}</b>,<br/>"
        f"Option souscrite : <b>{option}</b>,<br/>"
        f"Et que ce mariage a été enregistré par nous sur leur demande le {date_marriage} à {region_name.capitalize()},<br/>"
        f"Régime matrimonial choisi : <b>{regime}</b>."
    )
    para_concl = Paragraph(concl_text, style_normal)
    para_concl.wrap(width - 4 * cm, 5 * cm)
    para_concl.drawOn(p, 2 * cm, y_body - para_concl.height)
    y_body -= para_concl.height + 1.2 * cm

    # ======= RÉORGANISATION EN 5 ZONES SÉPARÉES =======
    # y_body est la ligne où le texte se termine. 
    # On place toutes les zones d'authentification en bas (max 4.5 cm de haut)
    # pour dégager la zone de texte.
    zone_y = min(1.5 * cm, y_body - 4.5 * cm) 
    
    from datetime import datetime
    date_str = dossier.updated_at.strftime("%d/%m/%Y") if dossier.updated_at else datetime.now().strftime("%d/%m/%Y")
    
    # === ZONE 1 : QR Code + Textes ===
    z1_x = 1.0 * cm
    qr_size = 2.5 * cm
    qr_y = zone_y + 0.8 * cm
    if qr_image_reader:
        p.drawImage(qr_image_reader, z1_x + 0.5*cm, qr_y, width=qr_size, height=qr_size)
    p.setFont("Helvetica", 6)
    p.drawCentredString(z1_x + 1.7*cm, qr_y - 0.2 * cm, "Scannez pour vérifier")
    p.drawCentredString(z1_x + 1.7*cm, qr_y - 0.5 * cm, "l'authenticité")
    p.drawCentredString(z1_x + 1.7*cm, qr_y - 0.8 * cm, f"Réf : {dossier.reference}")

    # === ZONE 2 : Timbre Fiscal (Option 1) ===
    z2_x = z1_x + 3.5 * cm
    if timbre_ref:
        _draw_secure_timbre(p, z2_x, zone_y + 0.8 * cm, timbre_ref)

    # === ZONE 3 : Tampon rond (Cachet Communal) ===
    z3_x = z2_x + 3.5 * cm
    cachet_y = zone_y + 0.2 * cm
    if cachet_path and os.path.exists(cachet_path):
        p.drawImage(ImageReader(cachet_path), z3_x, cachet_y, width=4.0*cm, height=4.0*cm, mask='auto')

    # === ZONE 4 : Texte Officier ===
    z4_x = z3_x + 4.2 * cm
    text_y = zone_y + 3.5 * cm
    p.setFont("Helvetica", 9)
    p.drawCentredString(z4_x + 1.5*cm, text_y, f"Fait à {commune_name.capitalize()},")
    p.drawCentredString(z4_x + 1.5*cm, text_y - 0.4*cm, f"le {date_str}")
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(z4_x + 1.5*cm, text_y - 1.2*cm, officier_name)
    p.setFont("Helvetica", 9)
    p.drawCentredString(z4_x + 1.5*cm, text_y - 1.6*cm, "Officier de l'Etat Civil")

    # === ZONE 5 : Tampon Ovale (Nominal) + Signature manuscrite ===
    z5_x = z4_x + 3.0 * cm
    # Le tampon nominal
    cachet_nom_w = 3.5 * cm
    cachet_nom_h = 1.5 * cm
    cachet_nom_y = zone_y + 1.8 * cm
    if cachet_nominal_path and os.path.exists(cachet_nominal_path):
        p.drawImage(ImageReader(cachet_nominal_path), z5_x, cachet_nom_y, width=cachet_nom_w, height=cachet_nom_h, mask='auto')
    
    # La signature EN DESSOUS (ou au-dessus) du tampon nominal pour ne pas chevaucher
    sig_w = 3.5 * cm
    sig_h = 1.5 * cm
    sig_y = cachet_nom_y - sig_h - 0.2*cm
    if signature_path and os.path.exists(signature_path):
        p.drawImage(ImageReader(signature_path), z5_x, sig_y, width=sig_w, height=sig_h, mask='auto')


def _draw_deces_pdf_content(p, width, height, dossier, officier, timbre_ref,
                              cachet_path, signature_path, cachet_nominal_path, qr_image_reader):
    """Dessine le certificat de décès au format A4 Portrait."""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY

    NOIR = HexColor('#000000')
    VERT = HexColor('#00853F')
    
    metadata = dossier.metadata or {}
    commune_name = dossier.commune.name if dossier.commune else "INCONNUE"
    region_name = dossier.commune.region if dossier.commune and dossier.commune.region else "DAKAR"
    officier_name = officier.full_name if officier else "L'Officier de l'État Civil"
    
    style_normal = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=12, leading=18, alignment=TA_JUSTIFY)
    
    # ---------------- EN-TÊTE ----------------
    p.setFillColor(NOIR)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(2 * cm, height - 2 * cm, f"REGION DE {region_name.upper()}")
    p.drawString(2 * cm, height - 2.5 * cm, "VILLE DE DAKAR")
    p.drawString(2 * cm, height - 3 * cm, "COMMUNE D'ARRONDISSEMENT")
    p.drawString(2 * cm, height - 3.5 * cm, f"DE {commune_name.upper()}")
    p.drawString(2 * cm, height - 4 * cm, "CENTRE D'ÉTAT CIVIL")
    
    p.setFont("Helvetica-Bold", 10)
    p.drawString(14 * cm, height - 2 * cm, "REPUBLIQUE DU SENEGAL")
    p.setFont("Helvetica", 10)
    p.drawString(14 * cm, height - 2.5 * cm, "Un Peuple - Un But - Une Foi")
    
    # ---------------- TITRE ----------------
    y_titre = height - 6.5 * cm
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, y_titre, "CERTIFICAT DE DÉCÈS")
    p.setLineWidth(1)
    p.line(width / 2 - 4 * cm, y_titre - 0.2 * cm, width / 2 + 4 * cm, y_titre - 0.2 * cm)
    
    # ---------------- TEXTE ADMINISTRATIF ----------------
    y_body = y_titre - 2.0 * cm
    
    nom = metadata.get('nom_defunt', '{nom_defunt}')
    prenom = metadata.get('prenom_defunt', '{prenom_defunt}')
    sexe = metadata.get('sexe_defunt', '{sexe}')
    titre = "Monsieur" if str(sexe).lower().startswith('m') else "Madame"
    date_naiss = metadata.get('date_naissance_defunt', '{date_naissance}')
    lieu_naiss = metadata.get('lieu_naissance_defunt', '{lieu_naissance}')
    date_deces = metadata.get('date_deces', '{date_deces}')
    heure_deces = metadata.get('heure_deces', '{heure_deces}')
    lieu_deces = metadata.get('lieu_deces', '{lieu_deces}')
    
    nationalite = metadata.get('nationalite_defunt', '{nationalite}')
    profession = metadata.get('profession_defunt', '{profession}')
    adresse = metadata.get('adresse_defunt', '{adresse}')
    declarant = metadata.get('nom_declarant', '{declarant}')
    lien = metadata.get('lien_declarant', '{lien}')
    cni = metadata.get('cni_declarant', '{cni}')
    
    texte_intro = (
        f"Je soussigné(e), <b>{officier_name}</b>, Officier de l'État Civil de la Commune de "
        f"<b>{commune_name.capitalize()}</b>, certifie que :<br/><br/>"
        f"<b>{titre} {prenom} {nom}</b>, de nationalité <b>{nationalite}</b>, exerçant la profession de <b>{profession}</b>, et domicilié(e) à <b>{adresse}</b>, "
        f"né(e) le <b>{date_naiss}</b> à <b>{lieu_naiss}</b>, "
        f"est décédé(e) le <b>{date_deces}</b> à <b>{heure_deces}</b>, à <b>{lieu_deces}</b>.<br/><br/>"
        f"L'enregistrement de ce décès a été effectué sur la déclaration de <b>{declarant}</b>, <b>{lien}</b> du défunt, titulaire de la pièce d'identité N° <b>{cni}</b>."
    )
    
    para_intro = Paragraph(texte_intro, style_normal)
    para_intro.wrap(width - 8 * cm, 10 * cm)
    para_intro.drawOn(p, 4 * cm, y_body - para_intro.height)
    
    # ---------------- CONCLUSION ----------------
    y_body -= 1.5 * cm
    texte_concl = "Le présent certificat est délivré à l'intéressé(e) ou à ses ayants droit pour servir et valoir ce que de droit."
    para_concl = Paragraph(texte_concl, style_normal)
    para_concl.wrap(width - 4 * cm, 5 * cm)
    para_concl.drawOn(p, 2 * cm, y_body - para_concl.height)
    y_body -= para_concl.height + 0.8 * cm
    
    # ---------------- 5 ZONES DE VALIDATION (Réutilisées) ----------------
    zone_y = min(1.5 * cm, y_body - 4.5 * cm) 
    
    from datetime import datetime
    date_str = dossier.updated_at.strftime("%d/%m/%Y") if dossier.updated_at else datetime.now().strftime("%d/%m/%Y")
    
    # ZONE 1 : QR Code + Textes
    z1_x = 1.0 * cm
    qr_size = 2.5 * cm
    qr_y = zone_y + 0.8 * cm
    if qr_image_reader:
        p.drawImage(qr_image_reader, z1_x + 0.5*cm, qr_y, width=qr_size, height=qr_size)
    p.setFont("Helvetica", 6)
    p.drawCentredString(z1_x + 1.7*cm, qr_y - 0.2 * cm, "Scannez pour vérifier")
    p.drawCentredString(z1_x + 1.7*cm, qr_y - 0.5 * cm, "l'authenticité")
    p.drawCentredString(z1_x + 1.7*cm, qr_y - 0.8 * cm, f"Réf : {dossier.reference}")

    # ZONE 2 : Timbre Fiscal
    z2_x = z1_x + 3.5 * cm
    if timbre_ref:
        _draw_secure_timbre(p, z2_x, zone_y + 0.8 * cm, timbre_ref)

    # ZONE 3 : Tampon rond (Cachet Communal)
    z3_x = z2_x + 3.5 * cm
    cachet_y = zone_y + 0.2 * cm
    if cachet_path and os.path.exists(cachet_path):
        p.drawImage(ImageReader(cachet_path), z3_x, cachet_y, width=4.0*cm, height=4.0*cm, mask='auto')

    # ZONE 4 : Texte Officier
    z4_x = z3_x + 4.2 * cm
    text_y = zone_y + 3.5 * cm
    p.setFont("Helvetica", 9)
    p.drawCentredString(z4_x + 1.5*cm, text_y, f"Fait à {commune_name.capitalize()},")
    p.drawCentredString(z4_x + 1.5*cm, text_y - 0.4*cm, f"le {date_str}")
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(z4_x + 1.5*cm, text_y - 1.2*cm, officier_name)
    p.setFont("Helvetica", 9)
    p.drawCentredString(z4_x + 1.5*cm, text_y - 1.6*cm, "Officier de l'Etat Civil")

    # ZONE 5 : Tampon Ovale (Nominal) + Signature manuscrite
    z5_x = z4_x + 3.0 * cm
    cachet_nom_w = 3.5 * cm
    cachet_nom_h = 1.5 * cm
    cachet_nom_y = zone_y + 1.8 * cm
    if cachet_nominal_path and os.path.exists(cachet_nominal_path):
        p.drawImage(ImageReader(cachet_nominal_path), z5_x, cachet_nom_y, width=cachet_nom_w, height=cachet_nom_h, mask='auto')
    
    sig_w = 3.5 * cm
    sig_h = 1.5 * cm
    sig_y = cachet_nom_y - sig_h - 0.2*cm
    if signature_path and os.path.exists(signature_path):
        p.drawImage(ImageReader(signature_path), z5_x, sig_y, width=sig_w, height=sig_h, mask='auto')


def _draw_pdf_content(p, width, height, dossier, officier, timbre_ref,
                      cachet_path, signature_path, cachet_nominal_path, qr_image_reader):
    """Dessine tout le contenu du PDF sur le canvas."""
    
    # Couleurs du Sénégal
    VERT = HexColor('#00853F')
    JAUNE = HexColor('#FDEF42')
    ROUGE = HexColor('#E31B23')
    NOIR = HexColor('#000000')
    GRIS = HexColor('#444444')
    GRIS_CLAIR = HexColor('#DDDDDD')

    metadata = dossier.metadata or {}
    citizen = dossier.citizen

    # --- FILIGRANE (Baobab/Cachet de la commune) ---
    if cachet_path and os.path.exists(cachet_path):
        p.saveState()
        # Opacité très faible pour le filigrane
        p.setFillAlpha(0.08)
        p.setStrokeAlpha(0.08)
        try:
            # We can't easily set image alpha in standard ReportLab without extending Canvas, 
            # but drawing it very lightly if it's an SVG works. If it's a PNG, ReportLab doesn't support alpha directly on drawImage unless using ImageReader with alpha channel.
            # As a workaround, we'll draw a large light grey circle and text to simulate a watermark if alpha fails.
            p.translate(width/2, height/2)
            p.rotate(30)
            p.setFont("Helvetica-Bold", 80)
            p.setFillColor(HexColor('#F0F0F0'))
            p.drawCentredString(0, 0, "BAOBAB - ÉTAT CIVIL")
        except:
            pass
        p.restoreState()
    else:
        p.saveState()
        p.translate(width/2, height/2)
        p.rotate(45)
        p.setFont("Helvetica-Bold", 60)
        p.setFillColor(HexColor('#F4F4F4'))
        p.drawCentredString(0, 0, "ÉTAT CIVIL DU SÉNÉGAL")
        p.restoreState()

    # ======== EN-TÊTE OFFICIEL ========
    y = height - 2.5 * cm
    p.setFillColor(NOIR)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, y, "RÉPUBLIQUE DU SÉNÉGAL")
    
    y -= 0.6 * cm
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, y, "Un Peuple — Un But — Une Foi")

    y -= 0.7 * cm
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(width / 2, y, "MINISTÈRE DE L'INTÉRIEUR ET DE LA SÉCURITÉ PUBLIQUE")

    commune_name = dossier.commune.name if dossier.commune else "N/A"
    region_name = dossier.commune.region if dossier.commune else "N/A"
    dept_name = dossier.commune.department if hasattr(dossier.commune, 'department') and dossier.commune.department else "N/A"

    y -= 0.7 * cm
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(VERT)
    p.drawCentredString(width / 2, y, f"CENTRE D'ÉTAT CIVIL DE {commune_name.upper()}")

    p.setStrokeColor(GRIS_CLAIR)
    p.setLineWidth(1)
    y -= 0.3 * cm
    p.line(3 * cm, y, width - 3 * cm, y)

    # ======== TIMBRE FISCAL (Sécurisé - En attente d'être dessiné en bas) ========
    # Nous le dessinerons plus tard avec les cachets.

    # ======== TITRE DU DOCUMENT ========
    y -= 1.2 * cm
    type_display = dossier.get_type_display().upper()
    p.setFillColor(NOIR)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, y, "EXTRAIT DU REGISTRE DES ACTES DE NAISSANCE")
    
    y -= 0.6 * cm
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, y, f"Réf. Document : {dossier.reference}")

    # Helper function to draw a section box
    def draw_section(title, start_y, lines_data):
        """Dessine un bloc encadré avec des lignes de données"""
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(VERT)
        p.drawString(1.5 * cm, start_y, title.upper())
        
        box_y = start_y - 0.2 * cm
        p.setStrokeColor(VERT)
        p.setLineWidth(0.5)
        
        current_y = box_y - 0.6 * cm
        p.setFillColor(NOIR)
        
        for left_label, left_val, right_label, right_val in lines_data:
            p.setFont("Helvetica-Bold", 9)
            p.drawString(1.7 * cm, current_y, f"{left_label} :")
            p.setFont("Helvetica", 9)
            p.drawString(4.5 * cm, current_y, str(left_val))
            
            if right_label:
                p.setFont("Helvetica-Bold", 9)
                p.drawString(11 * cm, current_y, f"{right_label} :")
                p.setFont("Helvetica", 9)
                p.drawString(14.5 * cm, current_y, str(right_val))
                
            current_y -= 0.6 * cm
            
        # Draw the box around
        height_box = box_y - current_y
        p.rect(1.5 * cm, current_y, width - 3 * cm, height_box)
        return current_y - 0.5 * cm

    # --- Fallback & Extraction Logic ---
    prenoms_enfant = metadata.get('prenoms_enfant')
    nom_enfant = metadata.get('nom_enfant')
    date_naissance_personne = metadata.get('date_naissance_personne')
    lieu_naissance = metadata.get('lieu_naissance')
    sexe = metadata.get('sexe')

    if not dossier.is_for_third_party and citizen:
        prenoms_enfant = prenoms_enfant or citizen.first_name
        nom_enfant = nom_enfant or citizen.last_name
        if hasattr(citizen, 'profile'):
            date_naissance_personne = date_naissance_personne or str(citizen.profile.date_of_birth)
            lieu_naissance = lieu_naissance or citizen.profile.place_of_birth
            sexe = sexe or citizen.profile.get_gender_display()
        
    nom_enfant = nom_enfant or metadata.get('nom') or 'N/A'
    prenoms_enfant = prenoms_enfant or 'N/A'
    date_naissance_personne = date_naissance_personne or metadata.get('date_naissance') or 'N/A'
    lieu_naissance = lieu_naissance or 'N/A'
    sexe = sexe or 'N/A'

    annee_registre = str(metadata.get('annee_registre', 'N/A'))
    numero_registre = str(metadata.get('numero_registre') or metadata.get('registre', 'N/A'))

    # --- Infos Admin ---
    y -= 1 * cm
    y = draw_section("Informations Administratives", y, [
        ("Région", region_name, "Département", dept_name),
        ("Commune", commune_name, "Centre État Civil", commune_name),
        ("Année Registre", annee_registre, "Numéro Registre", numero_registre),
    ])

    # --- Infos Enfant ---
    y = draw_section("Informations de l'Enfant", y, [
        ("Prénoms", prenoms_enfant, "Nom", nom_enfant),
        ("Né(e) le", date_naissance_personne, "Heure", metadata.get('heure_naissance', 'Non précisée')),
        ("Lieu", lieu_naissance, "Sexe", sexe),
    ])

    # --- Infos Parents ---
    y = draw_section("Informations des Parents", y, [
        ("Prénom Père", metadata.get('prenom_pere', 'N/A'), "", ""),
        ("Prénoms Mère", metadata.get('prenom_mere', 'N/A'), "Nom Mère", metadata.get('nom_mere', 'N/A')),
    ])

    # --- Jugement Supplétif ---
    if metadata.get('est_jugement_suppletif'):
        y = draw_section("Jugement d'Autorisation d'Inscription", y, [
            ("Tribunal", metadata.get('tribunal_competent', 'N/A'), "N° Jugement", metadata.get('numero_jugement', 'N/A')),
            ("Date Jugement", metadata.get('date_jugement', 'N/A'), "Date Inscription", f"{metadata.get('date_inscription', 'N/A')} ({metadata.get('annee_inscription', '')})"),
        ])

    # ======== CERTIFICATION ET CACHETS ========
    y -= 0.5 * cm
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(GRIS)
    p.drawCentredString(width / 2, y, "Extrait certifié conforme aux indications du registre des naissances.")
    
    y -= 0.6 * cm
    date_str = dossier.completed_at.strftime('%d/%m/%Y') if dossier.completed_at else 'N/A'
    p.setFillColor(NOIR)
    p.setFont("Helvetica", 10)
    p.drawString(2 * cm, y, f"Délivré à : {commune_name}")
    p.drawString(14 * cm, y, f"Le : {date_str}")
    
    y -= 0.6 * cm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(12 * cm, y, "L'Officier de l'État Civil")

    # CACHETS ET TIMBRE EN BAS
    seal_size = 3.5 * cm
    seal_y = y - 4 * cm

    # Signature — droite
    sig_x = width - 2 * cm - seal_size
    _draw_seal(p, signature_path, sig_x, seal_y, seal_size)
    if officier:
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(sig_x + seal_size / 2, seal_y - 0.4 * cm, officier.full_name)

    # Cachet Nominal — centre-droit
    if cachet_nominal_path:
        nom_x = width - 6.5 * cm - seal_size
        _draw_seal(p, cachet_nominal_path, nom_x, seal_y, seal_size)

    # Cachet communal — centre-gauche
    _draw_seal(p, cachet_path, 6.5 * cm, seal_y, seal_size)
    p.setFont("Helvetica", 7)
    p.drawCentredString(6.5 * cm + seal_size / 2, seal_y - 0.4 * cm, "Cachet Communal")

    # Timbre Fiscal - Bas gauche
    if timbre_ref:
        p.saveState()
        stamp_width = 4 * cm
        stamp_height = 2.2 * cm
        stamp_x = 1.5 * cm
        stamp_y = seal_y + 0.5 * cm
        
        # Fond légèrement jaune
        p.setFillColor(HexColor('#FFFFF0'))
        p.setStrokeColor(VERT)
        p.setLineWidth(1.5)
        p.roundRect(stamp_x, stamp_y, stamp_width, stamp_height, 4, stroke=1, fill=1)
        
        # Guillochis (lignes intérieures)
        p.setStrokeColor(HexColor('#E0F0E0'))
        p.setLineWidth(0.5)
        for i in range(0, int(stamp_width), 5):
            p.line(stamp_x + i, stamp_y, stamp_x + i, stamp_y + stamp_height)
        
        p.setFillColor(VERT)
        p.setFont("Helvetica-Bold", 7)
        p.drawCentredString(stamp_x + stamp_width / 2, stamp_y + 1.6 * cm, "TIMBRE FISCAL ÉLECTRONIQUE")
        
        p.setFillColor(ROUGE)
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(stamp_x + stamp_width / 2, stamp_y + 0.9 * cm, "500 FCFA")
        
        p.setFillColor(NOIR)
        p.setFont("Courier-Bold", 6)
        p.drawCentredString(stamp_x + stamp_width / 2, stamp_y + 0.3 * cm, f"Réf: {timbre_ref}")
        p.restoreState()

    # QR CODE - très bas gauche (sous le timbre)
    qr_y = 1.5 * cm
    if qr_image_reader:
        qr_size = 2.5 * cm
        qr_x = 2 * cm
        p.drawImage(qr_image_reader, qr_x, qr_y, width=qr_size, height=qr_size)
        p.setFont("Helvetica", 7)
        p.drawCentredString(qr_x + qr_size / 2, qr_y - 0.3 * cm, "Vérifier")

    # MENTION LEGALE - tout en bas, centrée
    p.setFont("Helvetica-Oblique", 7)
    p.setFillColor(HexColor('#888888'))
    p.drawCentredString(width / 2, 0.8 * cm, "Ce document est sécurisé par une empreinte cryptographique (HMAC-SHA256). Toute modification l'invalide.")


def generate_signed_certificate(dossier, officier):
    """
    Fonction principale : génère un certificat PDF signé cryptographiquement.

    Processus :
      1. Crée un timbre fiscal
      2. Génère le PDF brut (sans QR)
      3. Hash le PDF brut (SHA-256)
      4. Construit le payload : ref|commune|nom|date|officier_id|pdf_sha256
      5. Signe le payload avec HMAC-SHA256
      6. Génère le QR Code avec l'URL de vérification
      7. Régénère le PDF final avec le QR Code
      8. Sauvegarde le GeneratedCertificate en BDD

    Returns:
        GeneratedCertificate: L'objet certificat créé avec sa signature.
    """
    # --- 1. Créer le timbre fiscal ---
    timbre = TimbreFiscal.objects.create(is_used=True)

    # --- 2. Résoudre les chemins des cachets ---
    # Map commune codes to folder names
    commune_folder_map = {
        'DKR-PLT': 'dakar_plateau',
        'DKR-KMS': 'keur_massar',
        'THS-NDG': 'ndiaganiao'
    }
    
    cachet_communal_path = ''
    signature_officier_path = ''
    cachet_nominal_path = ''

    if dossier.commune and dossier.commune.code in commune_folder_map:
        folder = commune_folder_map[dossier.commune.code]
        folder_path = os.path.join(ASSETS_DIR, folder)
        
        # On cherche dynamiquement les fichiers PNG correspondants dans le dossier
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.startswith('Cachet_Communal') and file.endswith('.png'):
                    cachet_communal_path = os.path.join(folder_path, file)
                elif file.startswith('Signarure_Officier') and file.endswith('.png'):
                    signature_officier_path = os.path.join(folder_path, file)
                elif file.startswith('Cachet_Nominal') and file.endswith('.png'):
                    cachet_nominal_path = os.path.join(folder_path, file)
                    
    # FALLBACK FOR DEMO/DEV: If cachets are still missing, use dakar_plateau as fallback
    if not cachet_communal_path or not signature_officier_path or not cachet_nominal_path:
        folder_path = os.path.join(ASSETS_DIR, 'dakar_plateau')
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.startswith('Cachet_Communal') and file.endswith('.png'):
                    cachet_communal_path = os.path.join(folder_path, file)
                elif file.startswith('Signarure_Officier') and file.endswith('.png'):
                    signature_officier_path = os.path.join(folder_path, file)
                elif file.startswith('Cachet_Nominal') and file.endswith('.png'):
                    cachet_nominal_path = os.path.join(folder_path, file)

    # --- Règle Métier R3 : Vérification des 4 éléments de validation ---
    if not cachet_communal_path or not signature_officier_path or not cachet_nominal_path or not timbre:
        raise ValueError(
            "Règle R3 non respectée : Un extrait sans les 4 éléments de validation "
            "(signature + cachet Baobab + cachet nominal + Timbre) est invalide "
            "et ne peut être délivré."
        )

    # --- 3. Générer le PDF brut (sans QR) ---
    raw_pdf_bytes = _generate_raw_pdf(
        dossier, officier, timbre.reference,
        cachet_communal_path, signature_officier_path, cachet_nominal_path
    )

    # --- 4. Hash du PDF brut ---
    pdf_hash = compute_pdf_hash(raw_pdf_bytes)

    # --- 5. Construire et signer le payload ---
    commune_name = dossier.commune.name if dossier.commune else 'N/A'
    
    # Gérer le cas du Guichet Rapide où citizen est None et citoyen_guichet est utilisé
    citizen_name = "N/A"
    if dossier.citizen:
        citizen_name = dossier.citizen.full_name
    elif hasattr(dossier, 'citoyen_guichet') and dossier.citoyen_guichet:
        citizen_name = dossier.citoyen_guichet.nom_complet
        
    metadata = dossier.metadata or {}
    date_naissance = metadata.get('date_naissance_verification', 'N/A')

    payload = build_payload(
        dossier_reference=dossier.reference,
        commune_name=commune_name,
        citizen_name=citizen_name,
        date_naissance=str(date_naissance),
        officier_id=str(officier.id) if officier else 'N/A',
        pdf_sha256=pdf_hash,
    )
    signature = sign_payload(payload)

    # --- 6. Construire l'URL de vérification ---
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    verification_url = f"{frontend_url}/verify/{dossier.reference}?sig={signature}"

    # --- 7. Régénérer le PDF final avec le QR ---
    final_pdf_bytes = _generate_final_pdf(
        dossier, officier, timbre.reference,
        cachet_communal_path, signature_officier_path, cachet_nominal_path,
        verification_url
    )

    # --- 8. Sauvegarder en BDD ---
    cert = GeneratedCertificate(
        dossier=dossier,
        officier=officier,
        data_payload=payload,
        pdf_sha256=pdf_hash,
        hmac_signature=signature,
        timbre=timbre,
        cachet_communal_svg=cachet_communal_path,
        signature_officier_svg=signature_officier_path,
    )

    pdf_filename = f"Certificat_{dossier.reference}.pdf"
    cert.pdf_file.save(pdf_filename, ContentFile(final_pdf_bytes), save=False)
    cert.save()

    logger.info(
        f"[CRYPTO][OK] Certificat généré pour {dossier.reference}. "
        f"PDF Hash: {pdf_hash[:16]}... Signature: {signature[:16]}..."
    )

    return cert
