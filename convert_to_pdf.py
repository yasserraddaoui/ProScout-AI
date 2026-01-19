"""
Script pour convertir RAPPORT_ML_PROJECT.md en PDF
Utilise reportlab pour une conversion simple et portable
"""

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
import sys

def parse_markdown_to_elements(md_content):
    """Parse Markdown et retourne des éléments pour reportlab"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        spaceBefore=20,
        borderWidth=1,
        borderColor=colors.HexColor('#3498db'),
        borderPadding=5
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=15,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#555'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        backColor=colors.HexColor('#f4f4f4'),
        leftIndent=20,
        rightIndent=20
    )
    
    lines = md_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            elements.append(Spacer(1, 6))
            i += 1
            continue
        
        # Titre principal
        if line.startswith('# 📊') or (line.startswith('#') and 'Rapport' in line):
            text = re.sub(r'^#+\s*', '', line)
            text = re.sub(r'[📊⚽🤖]', '', text).strip()
            elements.append(Paragraph(text, title_style))
            elements.append(Spacer(1, 20))
            i += 1
            continue
        
        # H1
        if line.startswith('## '):
            text = re.sub(r'^##+\s*', '', line)
            text = clean_markdown(text)
            elements.append(Paragraph(text, h1_style))
            elements.append(Spacer(1, 12))
            i += 1
            continue
        
        # H2
        if line.startswith('### '):
            text = re.sub(r'^###+\s*', '', line)
            text = clean_markdown(text)
            elements.append(Paragraph(text, h2_style))
            elements.append(Spacer(1, 10))
            i += 1
            continue
        
        # H3
        if line.startswith('#### '):
            text = re.sub(r'^####+\s*', '', line)
            text = clean_markdown(text)
            elements.append(Paragraph(text, h3_style))
            elements.append(Spacer(1, 8))
            i += 1
            continue
        
        # Tableau
        if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
            table_data = []
            # Lire l'en-tête
            header = [cell.strip() for cell in line.split('|') if cell.strip()]
            table_data.append(header)
            i += 1
            # Lire la ligne de séparation
            if i < len(lines) and '---' in lines[i]:
                i += 1
            # Lire les lignes de données
            while i < len(lines) and '|' in lines[i] and not lines[i].strip().startswith('#'):
                row = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
                if row:
                    table_data.append(row)
                i += 1
            if len(table_data) > 1:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')])
                ]))
                elements.append(table)
                elements.append(Spacer(1, 12))
            continue
        
        # Code block
        if line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                code_text = '\n'.join(code_lines)
                elements.append(Paragraph(f'<font face="Courier" size="9">{escape_html(code_text)}</font>', code_style))
                elements.append(Spacer(1, 10))
            i += 1
            continue
        
        # Liste
        if line.startswith('- ') or line.startswith('* '):
            text = re.sub(r'^[-*]\s+', '', line)
            text = clean_markdown(text)
            elements.append(Paragraph(f'• {text}', normal_style))
            i += 1
            continue
        
        # Ligne de séparation
        if line.startswith('---'):
            elements.append(Spacer(1, 20))
            i += 1
            continue
        
        # Texte normal
        text = clean_markdown(line)
        if text:
            elements.append(Paragraph(text, normal_style))
            elements.append(Spacer(1, 6))
        i += 1
    
    return elements

def clean_markdown(text):
    """Nettoie le markdown et le convertit en HTML pour reportlab"""
    # Échapper d'abord les caractères spéciaux
    text = escape_html(text)
    
    # Code inline (avant les autres transformations)
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" size="9">\1</font>', text)
    
    # Gras (en évitant les conflits avec code)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__([^_]+)__', r'<b>\1</b>', text)
    
    # Italique (seulement si pas déjà dans code ou gras)
    def replace_italic(match):
        content = match.group(1)
        if '<font' not in content and '<b>' not in content:
            return f'<i>{content}</i>'
        return match.group(0)
    text = re.sub(r'(?<!`)\*([^*`]+)\*(?!`)', replace_italic, text)
    
    # Emojis (supprimer)
    text = re.sub(r'[📊⚽🤖👤🏠📈🔍📐🏆✅❌⚠️💡🎯🔮📉📊]', '', text)
    
    return text

def escape_html(text):
    """Échappe les caractères HTML (mais garde les balises reportlab)"""
    # Ne pas échapper si c'est déjà une balise HTML valide
    if '<' in text and '>' in text:
        # Vérifier si c'est une balise HTML valide
        if re.search(r'<[a-z]+[^>]*>', text, re.IGNORECASE):
            # C'est déjà du HTML, ne pas échapper
            return text
    
    # Sinon échapper
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def markdown_to_pdf(md_file, pdf_file):
    """Convertit un fichier Markdown en PDF"""
    try:
        # Lire le fichier Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Créer le PDF
        doc = SimpleDocTemplate(
            pdf_file,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Parser le markdown
        print(f"Parsing du fichier {md_file}...")
        elements = parse_markdown_to_elements(md_content)
        
        # Générer le PDF
        print(f"Génération du PDF {pdf_file}...")
        doc.build(elements)
        
        print(f"PDF cree avec succes : {pdf_file}")
        
    except ImportError as e:
        print("❌ Erreur : Bibliothèque manquante")
        print("\nInstallez reportlab avec :")
        print("pip install reportlab")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de la conversion : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    md_file = "RAPPORT_ML_PROJECT.md"
    pdf_file = "RAPPORT_ML_PROJECT.pdf"
    
    if not Path(md_file).exists():
        print(f"Fichier {md_file} introuvable")
        sys.exit(1)
    
    markdown_to_pdf(md_file, pdf_file)
