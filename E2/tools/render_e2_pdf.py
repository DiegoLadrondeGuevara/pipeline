"""Render the editable E2 DOCX to a reviewable PDF without LibreOffice."""
from html import escape
from io import BytesIO
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

E2=Path(__file__).resolve().parents[1]
docx_path=E2/'informe'/'Informe_E2_Proyecto2_base.docx'
pdf_path=E2/'informe'/'Informe_E2_Proyecto2_base.pdf'
doc=Document(docx_path)
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold')

styles={
 'Normal':ParagraphStyle('Normal',fontName='Arial',fontSize=10.2,leading=13.1,
                         spaceAfter=5,textColor=colors.black),
 'Heading 1':ParagraphStyle('Heading 1',fontName='Arial-Bold',fontSize=14,leading=18,
                             spaceAfter=9,keepWithNext=1,textColor=colors.black),
 'Heading 2':ParagraphStyle('Heading 2',fontName='Arial-Bold',fontSize=11.5,leading=14,
                             spaceBefore=8,spaceAfter=5,keepWithNext=1,textColor=colors.black),
 'Title':ParagraphStyle('Title',fontName='Arial-Bold',fontSize=17,leading=21,
                        alignment=TA_CENTER,spaceAfter=6,textColor=colors.black),
 'Caption':ParagraphStyle('Caption',fontName='Arial',fontSize=9,leading=11,
                          alignment=TA_CENTER,spaceAfter=7,textColor=colors.black),
 'Cover':ParagraphStyle('Cover',fontName='Arial',fontSize=10.5,leading=14,
                        spaceAfter=12,textColor=colors.black),
 'Index':ParagraphStyle('Index',fontName='Arial',fontSize=9.6,leading=12,
                        spaceAfter=0,textColor=colors.black),
}

def markup(par):
    parts=[]
    for run in par.runs:
        txt=escape(run.text).replace('\n','<br/>')
        if not txt: continue
        if run.bold: txt='<b>'+txt+'</b>'
        if run.italic: txt='<i>'+txt+'</i>'
        parts.append(txt)
    return ''.join(parts) or ' '

def picture(par):
    blips=par._p.xpath('.//a:blip')
    if not blips: return None
    rid=blips[0].get(qn('r:embed'))
    blob=par.part.related_parts[rid].blob
    im=Image(BytesIO(blob))
    inline=par._p.xpath('.//wp:inline')
    if inline:
        extent=inline[0].xpath('./wp:extent')
        if extent:
            width=float(extent[0].get('cx'))/914400*72
            height=float(extent[0].get('cy'))/914400*72
            im.drawWidth=width; im.drawHeight=height
    im.hAlign='CENTER'
    return im

def is_pagebreak(par):
    return bool(par._p.xpath('.//w:br[@w:type="page"]'))

def convert_table(t, cover=False):
    rows=[]
    for row in t.rows:
        cells=[]
        for c in row.cells:
            cells.append(Paragraph(escape(c.text).replace('\n','<br/>'),
                                   styles['Cover'] if cover else styles['Normal']))
        rows.append(cells)
    widths=[]
    for c in t.rows[0].cells:
        widths.append(c.width.cm*cm if c.width else 17.2*cm/len(t.columns))
    total=sum(widths)
    widths=[w*17.2*cm/total for w in widths]
    rt=Table(rows,colWidths=widths,repeatRows=1,hAlign='CENTER')
    rt.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.8 if cover else 0.35,
         colors.black if cover else colors.HexColor('#D9D9D9')),
        ('BACKGROUND',(0,0),(-1,0),colors.white if cover else colors.HexColor('#E8E8E8')),
        ('FONTNAME',(0,0),(-1,0),'Arial-Bold'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),7 if cover else 5),
        ('BOTTOMPADDING',(0,0),(-1,-1),7 if cover else 5),
    ]))
    return rt

story=[]
page=1
for child in doc.element.body.iterchildren():
    if child.tag==qn('w:p'):
        p=DocxParagraph(child,doc)
        if is_pagebreak(p):
            story.append(PageBreak()); page+=1; continue
        if p.text.count('\n')>=8 and not p.text.strip():
            story.append(Spacer(1,7.3*cm)); continue
        pic=picture(p)
        if pic:
            story.append(pic)
            story.append(Spacer(1,5 if page==1 else 7))
            continue
        txt=markup(p)
        if txt.strip() in ('',' '):
            story.append(Spacer(1,4)); continue
        # Waveform placeholders carry eight line breaks as an editable slot.
        if 'Figura pendiente.' in p.text:
            story.append(Paragraph(txt,styles['Normal']))
            continue
        if p.text.strip()=='':
            story.append(Spacer(1,4)); continue
        if page==1 and p.text.startswith('Lima, Perú'):
            story.append(Spacer(1,2.5*cm))
        style=styles.get(p.style.name,styles['Normal'])
        if page==1 and p.style.name=='Normal': style=styles['Cover']
        if p.alignment==1 and p.style.name=='Normal':
            style=ParagraphStyle('center'+str(len(story)),parent=style,alignment=TA_CENTER)
        if 'Figura ' in p.text and p.text.startswith('Figura '):
            style=styles['Caption']
        story.append(Paragraph(txt,style))
        # Cover uses the generous vertical rhythm of the E1 reference.
        if page==1 and p.text.startswith('2026'):
            pass
    elif child.tag==qn('w:tbl'):
        t=DocxTable(child,doc)
        story.append(convert_table(t,cover=page==1))
        story.append(Spacer(1,7))

def footer(canvas,pdfdoc):
    if pdfdoc.page==1: return
    canvas.saveState()
    canvas.setFont('Arial',9)
    canvas.drawRightString(A4[0]-1.8*cm,0.88*cm,f'Página {pdfdoc.page}')
    canvas.restoreState()

pdf=SimpleDocTemplate(str(pdf_path),pagesize=A4,
                      topMargin=1.7*cm,bottomMargin=1.8*cm,
                      leftMargin=1.8*cm,rightMargin=1.8*cm,
                      title='Informe técnico de la segunda entrega',
                      author='Equipo Proyecto 2')
story.insert(0,Spacer(1,-0.7*cm))
pdf.build(story,onFirstPage=footer,onLaterPages=footer)
print(pdf_path)
