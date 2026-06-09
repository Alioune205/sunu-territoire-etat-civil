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
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

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


def _generate_raw_pdf(dossier, officier, timbre_ref, cachet_path, signature_path):
    """
    Génère le contenu PDF brut (SANS QR Code).
    On génère d'abord sans QR pour pouvoir hasher le contenu,
    puis on re-génère avec le QR.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    _draw_pdf_content(p, width, height, dossier, officier, timbre_ref,
                      cachet_path, signature_path, qr_image_reader=None)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


def _generate_final_pdf(dossier, officier, timbre_ref, cachet_path,
                        signature_path, verification_url):
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
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    _draw_pdf_content(p, width, height, dossier, officier, timbre_ref,
                      cachet_path, signature_path, qr_image_reader)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


def _draw_pdf_content(p, width, height, dossier, officier, timbre_ref,
                      cachet_path, signature_path, qr_image_reader):
    """Dessine tout le contenu du PDF sur le canvas."""

    # ======== EN-TÊTE OFFICIEL ========
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 2.5 * cm, "RÉPUBLIQUE DU SÉNÉGAL")

    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 3.2 * cm, "Un Peuple — Un But — Une Foi")

    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(width / 2, height - 4 * cm, "MINISTÈRE DE L'INTÉRIEUR ET DE LA SÉCURITÉ PUBLIQUE")

    # Commune
    commune_name = dossier.commune.name if dossier.commune else "N/A"
    p.setFont("Helvetica-Bold", 11)
    p.drawCentredString(width / 2, height - 5 * cm, f"COMMUNE DE {commune_name.upper()}")

    # Ligne de séparation
    p.setStrokeColor(HexColor('#333333'))
    p.setLineWidth(1.5)
    p.line(3 * cm, height - 5.5 * cm, width - 3 * cm, height - 5.5 * cm)

    # ======== TITRE DU DOCUMENT ========
    type_display = dossier.get_type_display().upper()
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 7 * cm, type_display)

    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 7.7 * cm, f"Réf. : {dossier.reference}")

    # ======== TIMBRE FISCAL ========
    if timbre_ref:
        p.saveState()
        p.setFont("Helvetica-Bold", 8)
        p.setFillColor(HexColor('#006633'))
        p.drawString(width - 6 * cm, height - 1.5 * cm, f"TIMBRE : {timbre_ref}")
        p.setFont("Helvetica", 7)
        p.drawString(width - 6 * cm, height - 2 * cm, "500 FCFA — Acquitté")
        p.restoreState()

    # ======== INFORMATIONS DU DOSSIER ========
    y = height - 9.5 * cm
    p.setFont("Helvetica", 11)

    citizen = dossier.citizen
    metadata = dossier.metadata or {}

    infos = [
        ("Nom complet", citizen.full_name),
        ("Numéro de registre", metadata.get('numero_registre', 'N/A')),
        ("Année de registre", str(metadata.get('annee_registre', 'N/A'))),
        ("Commune de déclaration", commune_name),
    ]

    # Ajouter des infos spécifiques selon le type
    if dossier.type == 'marriage_certificate':
        infos.append(("Rôle", metadata.get('role_mariage', 'N/A')))
    if dossier.type == 'death_certificate':
        infos.append(("Lien avec le défunt", metadata.get('lien_defunt', 'N/A')))

    for label, value in infos:
        p.setFont("Helvetica-Bold", 10)
        p.drawString(3.5 * cm, y, f"{label} :")
        p.setFont("Helvetica", 10)
        p.drawString(9 * cm, y, str(value))
        y -= 0.7 * cm

    # ======== DATE DE DÉLIVRANCE ========
    y -= 1 * cm
    p.setFont("Helvetica-Oblique", 10)
    date_str = dossier.completed_at.strftime('%d/%m/%Y') if dossier.completed_at else 'N/A'
    p.drawString(3.5 * cm, y, f"Délivré le : {date_str}")

    # ======== MENTION LÉGALE ========
    y -= 1.5 * cm
    p.setFont("Helvetica-Oblique", 8)
    p.setFillColor(HexColor('#666666'))
    p.drawCentredString(width / 2, y,
                        "Ce document est généré électroniquement et protégé par signature cryptographique HMAC-SHA256.")
    p.setFillColor(HexColor('#000000'))

    # ======== CACHETS ET SIGNATURES (Bas de page) ========
    seal_size = 3.5 * cm
    seal_y = 4 * cm

    # Cachet communal — bas gauche
    _draw_seal(p, cachet_path, 2.5 * cm, seal_y, seal_size)
    p.setFont("Helvetica", 7)
    p.drawCentredString(2.5 * cm + seal_size / 2, seal_y - 0.5 * cm, "Cachet Communal")

    # Signature officier — bas droite
    sig_x = width - 2.5 * cm - seal_size
    _draw_seal(p, signature_path, sig_x, seal_y, seal_size)
    p.setFont("Helvetica", 7)
    if officier:
        p.drawCentredString(sig_x + seal_size / 2, seal_y - 0.5 * cm, officier.full_name)
        p.drawCentredString(sig_x + seal_size / 2, seal_y - 1 * cm, "Officier d'État Civil")

    # ======== QR CODE (bas centre) ========
    if qr_image_reader:
        qr_size = 3 * cm
        qr_x = (width - qr_size) / 2
        qr_y = 4.5 * cm
        p.drawImage(qr_image_reader, qr_x, qr_y, width=qr_size, height=qr_size)
        p.setFont("Helvetica", 7)
        p.drawCentredString(width / 2, qr_y - 0.4 * cm, "Scanner pour vérifier l'authenticité")


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
    cachet_communal_path = os.path.join(ASSETS_DIR, 'cachet_communal.svg')
    signature_officier_path = os.path.join(ASSETS_DIR, 'signature_officier.svg')

    if not os.path.exists(cachet_communal_path):
        cachet_communal_path = ''
    if not os.path.exists(signature_officier_path):
        signature_officier_path = ''

    # --- 3. Générer le PDF brut (sans QR) ---
    raw_pdf_bytes = _generate_raw_pdf(
        dossier, officier, timbre.reference,
        cachet_communal_path, signature_officier_path
    )

    # --- 4. Hash du PDF brut ---
    pdf_hash = compute_pdf_hash(raw_pdf_bytes)

    # --- 5. Construire et signer le payload ---
    commune_name = dossier.commune.name if dossier.commune else 'N/A'
    citizen = dossier.citizen
    metadata = dossier.metadata or {}
    date_naissance = metadata.get('date_naissance_verification', 'N/A')

    payload = build_payload(
        dossier_reference=dossier.reference,
        commune_name=commune_name,
        citizen_name=citizen.full_name,
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
        cachet_communal_path, signature_officier_path,
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
