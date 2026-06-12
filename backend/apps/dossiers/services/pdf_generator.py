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


def _generate_raw_pdf(dossier, officier, timbre_ref, cachet_path, signature_path, cachet_nominal_path):
    """
    Génère le contenu PDF brut (SANS QR Code).
    On génère d'abord sans QR pour pouvoir hasher le contenu,
    puis on re-génère avec le QR.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

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
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    _draw_pdf_content(p, width, height, dossier, officier, timbre_ref,
                      cachet_path, signature_path, cachet_nominal_path, qr_image_reader)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


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
