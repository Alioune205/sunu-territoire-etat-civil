"""
Script pour générer un PDF de test simulant une CNI sénégalaise.
Lance : python generate_test_pdf.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

doc = SimpleDocTemplate("test_cni.pdf", pagesize=A4)
styles = getSampleStyleSheet()
elements = []

# Titre
title_style = ParagraphStyle('title', fontSize=18, fontName='Helvetica-Bold', alignment=1, spaceAfter=10)
elements.append(Paragraph("REPUBLIQUE DU SENEGAL", title_style))
elements.append(Paragraph("CARTE NATIONALE D'IDENTITE CEDEAO", title_style))
elements.append(Spacer(1, 0.5*cm))

# Données CNI
label_style = ParagraphStyle('label', fontSize=11, fontName='Helvetica-Bold')
value_style = ParagraphStyle('value', fontSize=12, fontName='Helvetica')

fields = [
    ("Prénoms", "MOUSSA"),
    ("Nom", "DIALLO"),
    ("Date de naissance", "15/03/1990"),
    ("Lieu de naissance", "DAKAR"),
    ("Sexe", "M"),
    ("Numéro CNI", "2 04 19900315 00042"),
    ("Date d'expiration", "15/03/2030"),
    ("Adresse", "15 RUE DE THIONG, DAKAR"),
    ("Numéro d'électeur", "103456789"),
    ("NIN", "1 234 1990 00456"),
]

table_data = [[Paragraph(label, label_style), Paragraph(value, value_style)] for label, value in fields]

table = Table(table_data, colWidths=[6*cm, 10*cm])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 8),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))
elements.append(table)

doc.build(elements)
print("✅ PDF généré : test_cni.pdf")
