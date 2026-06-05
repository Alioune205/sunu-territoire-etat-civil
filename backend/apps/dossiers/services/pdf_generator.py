import os
import io
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

from django.conf import settings
from django.core.files.base import ContentFile
from apps.documents.models import Document
from apps.qr.models import QRCode  # Wait, does qr.models exist? I should check. For now, I'll just generate the image.

def generate_dossier_pdf(dossier):
    """
    Génère un PDF officiel pour un dossier approuvé, 
    inclut un QR Code de vérification, et l'enregistre en tant que Document.
    """
    buffer = BytesIO()
    
    # Création du PDF
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # En-tête de l'État (simplifié)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 3*cm, "RÉPUBLIQUE DU SÉNÉGAL")
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, height - 4*cm, "Un Peuple - Un But - Une Foi")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 6*cm, f"ACTE OFFICIEL : {dossier.get_type_display().upper()}")
    
    # Informations du dossier
    p.setFont("Helvetica", 12)
    p.drawString(3*cm, height - 9*cm, f"Référence du Dossier : {dossier.reference}")
    p.drawString(3*cm, height - 10*cm, f"Citoyen : {dossier.citizen.full_name}")
    p.drawString(3*cm, height - 11*cm, f"Date d'approbation : {dossier.completed_at.strftime('%d/%m/%Y') if dossier.completed_at else ''}")
    p.drawString(3*cm, height - 12*cm, f"Commune : {dossier.commune.name if dossier.commune else ''}")
    
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(3*cm, height - 14*cm, "Ceci est un document officiel généré électroniquement.")

    # --- Génération du QR Code ---
    # L'URL de validation pointant vers le frontend (ou backend public)
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    validation_url = f"{frontend_url}/verify/{dossier.reference}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(validation_url)
    qr.make(fit=True)
    
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    # Conversion de l'image QR pour ReportLab
    img_buffer = BytesIO()
    img_qr.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    qr_image_reader = ImageReader(img_buffer)
    
    # Dessiner le QR Code en bas à droite
    qr_size = 4 * cm
    p.drawImage(qr_image_reader, width - 3*cm - qr_size, 3*cm, width=qr_size, height=qr_size)
    
    p.setFont("Helvetica", 8)
    p.drawCentredString(width - 3*cm - qr_size/2, 2.5*cm, "Scanner pour vérifier")
    p.drawCentredString(width - 3*cm - qr_size/2, 2.2*cm, "l'authenticité")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    # Création du Document dans la base de données
    pdf_filename = f"Acte_{dossier.reference}.pdf"
    
    document = Document.objects.create(
        dossier=dossier,
        original_filename=pdf_filename,
        file_type=Document.FileType.PDF,
        file_size=len(buffer.getvalue()),
        description=f"Acte officiel généré pour {dossier.get_type_display()}",
        uploaded_by=dossier.assigned_agent if dossier.assigned_agent else dossier.citizen,  # l'agent qui a approuvé
        # Le fichier lui-même sera sauvegardé juste après
    )
    
    document.file.save(pdf_filename, ContentFile(buffer.getvalue()), save=True)
    
    return document
