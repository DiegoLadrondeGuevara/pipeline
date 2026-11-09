"""Build the editable E2 base report using the E1 cover as reference."""
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
E2 = ROOT / "E2"
OUT = E2 / "informe"
ASSETS = OUT / "assets"
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)
DOCX = OUT / "Informe_E2_Proyecto2_base.docx"

logo = ASSETS / "logo_utec_e1.png"
# The committed asset makes E2 self-contained. Extract from E1 only if absent.
if not logo.exists():
    e1 = pymupdf.open(ROOT / "informe" / "Informe_E1_Proyecto2.pdf")
    xref = e1[0].get_images(full=True)[0][0]
    logo.write_bytes(e1.extract_image(xref)["image"])

# Editable conceptual diagram, intentionally separate from the future waveforms.
diagram = ASSETS / "datapath_e2.png"
W, H = 1800, 680
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
font_path = "C:/Windows/Fonts/arial.ttf"
bold_path = "C:/Windows/Fonts/arialbd.ttf"
font = ImageFont.truetype(font_path, 30)
bold = ImageFont.truetype(bold_path, 34)
small = ImageFont.truetype(font_path, 25)
blue, pale, gray = "#17324D", "#EAF2F6", "#555555"

def box(x, y, w, h, lines, fill=pale):
    d.rounded_rectangle((x,y,x+w,y+h), radius=13, fill=fill, outline=blue, width=3)
    line_y = y + 20
    for j, line in enumerate(lines):
        f = bold if j == 0 else small
        bb = d.textbbox((0,0), line, font=f)
        d.text((x + (w-(bb[2]-bb[0]))/2, line_y), line, font=f, fill=blue)
        line_y += 39

columns = [(28, "IF"), (365, "ID"), (702, "EX"), (1039, "MEM"), (1376, "WB")]
for x, label in columns:
    d.text((x+122, 10), label, font=bold, fill=blue)
for lane, y in enumerate((70, 240)):
    box(28,y,290,130,[f"Vía {lane}","PC + instrucción"])
    box(365,y,290,130,[f"Decode {lane}","lecturas + control"])
    box(702,y,290,130,[f"ALU {lane}","operandos reenviados"])
    box(1039,y,290,130,[f"Registro {lane}","EX / MEM"])
    box(1376,y,290,130,[f"Writeback {lane}","resultado + rd"])
    for x in (325,662,999,1336):
        d.line((x,y+65,x+31,y+65), fill=gray, width=4)
        d.polygon([(x+31,y+65),(x+20,y+57),(x+20,y+73)], fill=gray)
box(365,425,290,135,["Issue Unit","emite 0, 1 o 2"],"#F2F2F2")
box(702,425,290,135,["Branch compartido","comparador + destino"],"#F2F2F2")
box(1039,425,290,135,["Memoria de datos","un único puerto"],"#F2F2F2")
box(1376,425,290,135,["Register File","4 lecturas / 2 escrituras"],"#F2F2F2")
d.text((35,605), "Los bits valid acompañan ambas vías; la vía 0 contiene la instrucción más antigua.",
       font=font, fill=blue)
im.save(diagram)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin, sec.bottom_margin = Cm(1.7), Cm(1.8)
sec.left_margin = sec.right_margin = Cm(1.8)
sec.footer_distance = Cm(0.8)
sec.different_first_page_header_footer = True

normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(10.5)
normal.font.color.rgb = RGBColor(0,0,0)
normal.paragraph_format.line_spacing = 1.14
normal.paragraph_format.space_after = Pt(5)
for name, size, before, after in (("Title",17,0,6),("Heading 1",14,0,9),
                                  ("Heading 2",11.5,9,5)):
    style = doc.styles[name]
    style.font.name = "Arial"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor(0,0,0)
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)
    style.paragraph_format.keep_with_next = True

def para(text="", bold_lead=None, align=None, after=None):
    p = doc.add_paragraph()
    if align is not None: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if bold_lead and text.startswith(bold_lead):
        p.add_run(bold_lead).bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p

def heading(text, level=1):
    return doc.add_heading(text, level=level)

def cell_shade(cell, fill):
    tcpr=cell._tc.get_or_add_tcPr()
    shd=OxmlElement("w:shd"); shd.set(qn("w:fill"),fill); tcpr.append(shd)

def table(headers, rows, widths, cover=False):
    t=doc.add_table(rows=1,cols=len(headers))
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.autofit=False
    for i,h in enumerate(headers): t.rows[0].cells[i].text=str(h)
    for row in rows:
        cells=t.add_row().cells
        for i,v in enumerate(row): cells[i].text=str(v)
    for ri,row in enumerate(t.rows):
        for ci,cell in enumerate(row.cells):
            cell.width=Cm(widths[ci])
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell_shade(cell,"FFFFFF" if cover else ("E8E8E8" if ri==0 else "FFFFFF"))
            tcpr=cell._tc.get_or_add_tcPr()
            borders=OxmlElement("w:tcBorders")
            for side in ("top","left","bottom","right"):
                edge=OxmlElement("w:"+side)
                edge.set(qn("w:val"),"single")
                edge.set(qn("w:sz"),"8" if cover else "5")
                edge.set(qn("w:color"),"000000" if cover else "D9D9D9")
                borders.append(edge)
            tcpr.append(borders)
            mar=OxmlElement("w:tcMar")
            for side in ("top","left","bottom","right"):
                m=OxmlElement("w:"+side)
                m.set(qn("w:w"),("120" if cover else "85") if side in ("top","bottom") else "100")
                m.set(qn("w:type"),"dxa")
                mar.append(m)
            tcpr.append(mar)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(0)
                p.paragraph_format.line_spacing=1.05
                for run in p.runs:
                    run.font.name="Arial"; run.font.size=Pt(10 if cover else 9)
                    if ri==0: run.bold=True
        trpr=row._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

def figure(path, caption, width=16.6):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(path),width=Cm(width))
    c=para(caption,align=WD_ALIGN_PARAGRAPH.CENTER,after=8)
    for run in c.runs: run.italic=True; run.font.size=Pt(9)

def waveform_placeholder(case, signals, explanation):
    p=para(f"Figura pendiente. Captura real de GTKWave del caso {case}.",after=3)
    p.paragraph_format.keep_with_next=True
    for r in p.runs: r.bold=True
    para("Señales que debe mostrar: "+signals,after=4)
    space=doc.add_paragraph(" ")
    space.paragraph_format.space_after=Pt(0)
    space.paragraph_format.line_spacing=1
    space.add_run("\n"*18)
    cap=para(f"Figura {case+1}. Espacio reservado para la waveform real de tests/e2_{case}.vcd.",
             align=WD_ALIGN_PARAGRAPH.CENTER,after=6)
    for r in cap.runs: r.italic=True; r.font.size=Pt(9)
    para("Lectura prevista: "+explanation)

def new_page(title):
    doc.add_page_break()
    heading(title)

footer=sec.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run("Página ")
field=OxmlElement("w:fldSimple")
field.set(qn("w:instr"),"PAGE")
footer._p.append(field)
for run in footer.runs: run.font.name="Arial"; run.font.size=Pt(9)

# Cover mirrors the final E1 PDF: centered logo/title, course metadata and team table.
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after=Pt(6)
p.add_run().add_picture(str(logo),width=Cm(9.0))
p=doc.add_paragraph(style="Title"); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.add_run("INFORME TÉCNICO DE LA SEGUNDA ENTREGA")
p=para("Procesador RISC-V segmentado y arquitectura Dual Issue funcional",
       align=WD_ALIGN_PARAGRAPH.CENTER,after=37)
for r in p.runs: r.bold=True
for label,value in (
    ("ASIGNATURA: ","Arquitectura de Computadoras (CS3051)-Teo. 1-Lab. 11-2026-2"),
    ("DOCENTE: ","Williams Valencia, Carlos Eduardo"),
    ("FECHA DE ENTREGA: ","09/11/2026"),
):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(13)
    p.add_run(label).bold=True; p.add_run(value)
para("INTEGRANTES:",bold_lead="INTEGRANTES:",after=5)
table(["INTEGRANTES","CÓDIGO"],[
    ("Ladron de Guevara Aguirre, Diego Abraham","202410083"),
    ("Burgos Ochoa, Jeseph Imanol","202510395"),
    ("Morales Portella Santiago Cesar","202510403"),
    ("Heredia Cadenas, Guillermo Arturo","202410219"),
],[11.8,5.4],cover=True)
p=para("Lima, Perú",align=WD_ALIGN_PARAGRAPH.CENTER,after=4)
p.paragraph_format.space_before=Pt(70)
para("2026",align=WD_ALIGN_PARAGRAPH.CENTER)

# Manual index. Explicit page starts below keep these references stable.
new_page("Índice")
para("Contenido del informe y correspondencia con los criterios de la segunda entrega.",after=13)
table(["Sección","Página"],[
    ("1 Introducción y alcance",3),
    ("2 Arquitectura Dual Issue completa",4),
    ("3 Controller e Issue Unit",5),
    ("4 Forwarding, hazards y stalls",6),
    ("5 Memoria, branches y flushing",7),
    ("6 Verificación funcional y waveforms",8),
    ("6.1 Dos ALU, RAW y doble escritura",8),
    ("6.2 Memoria compartida en ambas vías",9),
    ("6.3 Branches en ambas posiciones",10),
    ("6.4 Load Use y emisión cero",11),
    ("7 Equivalencia y comparación preliminar A frente a B",12),
    ("8 Conclusiones, reproducción y pendientes",13),
],[15.0,2.2])

new_page("1 Introducción y alcance")
para("Este informe presenta la segunda entrega del Proyecto 2 de Arquitectura de Computadoras. El objetivo de E2 es convertir el prototipo Dual Issue de E1 en un procesador B funcional, capaz de emitir hasta dos instrucciones consecutivas por ciclo sin alterar el orden del programa. Se documentan el datapath, el control de emisión, los riesgos, los recursos compartidos y los resultados de simulación.")
heading("1.1 Punto de partida y cambio realizado",2)
para("La arquitectura A de E1 es un pipeline Single Issue de cinco etapas con forwarding, stall Load Use y flush. El prototipo Dual Issue de E1 leía y decodificaba dos instrucciones y calculaba dos resultados en EX, pero sus puertos de writeback estaban deshabilitados. E2 incorpora la Issue Unit, la propagación completa por EX/MEM y MEM/WB, dos escrituras reales, memoria de datos única, branch compartido y control de validez por vía.")
heading("1.2 Alcance de instrucciones y criterio de corrección",2)
para("B conserva las instrucciones enteras soportadas por A: operaciones ALU de registro e inmediato, cargas y stores de byte, media palabra y palabra, branches, JAL, JALR, LUI y AUIPC. FENCE y SYSTEM quedan fuera del entorno implementado; no se afirma cobertura integral de todas las excepciones RV32I. La condición funcional es que B produzca el mismo estado de registros y memoria que A con el mismo programa y datos iniciales.")
heading("1.3 Organización de la evidencia",2)
para("Las secciones 2 a 5 describen el hardware y sus reglas. La sección 6 vincula cuatro programas dirigidos con resultados esperados y espacios para capturas reales de GTKWave. La sección 7 compara A y B. Las capturas se incorporarán y comentarán en una revisión posterior de este informe base; los archivos VCD ya son generados por los testbenches.")
heading("1.4 Criterios de aceptación de E2",2)
table(["Criterio","Evidencia en este informe"],[
    ("Datapath e Issue Unit (0,75)","Secciones 2 y 3; caso 1"),
    ("Forwarding, hazards y stalls (1,00)","Sección 4; casos 1 y 4"),
    ("Memoria, branches y flushing (0,75)","Sección 5; casos 2 y 3"),
    ("Programas, waveforms y resultados (0,50)","Secciones 6 y 7; capturas por incorporar"),
    ("Pregunta individual (1,00)","Defensa oral de decisiones y trazas"),
],[8.2,9.0])
heading("1.5 Módulos usados en B",2)
table(["Archivo RTL","Función en B"],[
    ("dualissue.v","Registros de pipeline, dos vías y selección de recursos"),
    ("issueunit.v","Decisión de emitir cero, una o dos instrucciones"),
    ("forward_dual.v","Selección del productor válido más reciente"),
    ("regfile_dual.v","Cuatro lecturas y dos escrituras reales"),
    ("controller.v, imem.v, dmem.v","Decodificación por vía, dos lecturas IF y puerto de datos único"),
],[6.0,11.2])

new_page("2 Arquitectura Dual Issue completa")
para("El procesador conserva IF, ID, EX, MEM y WB. IF obtiene dos instrucciones en direcciones PC y PC+4. ID mantiene un par ordenado: la vía 0 contiene la instrucción antigua y la vía 1 la joven. Dos Controllers y cuatro lecturas del Register File preparan operandos y controles. La Issue Unit decide cuántas instrucciones entran en EX. Dos ALU ejecutan operaciones independientes; un multiplexor selecciona la única operación de memoria y otro selecciona la operación de control. EX/MEM y MEM/WB llevan datos, destinos y bits de validez para cada vía.")
figure(diagram,"Figura 1. Datapath lógico de B con dos vías y recursos compartidos.")
para("Los registros de pipeline guardan PC, operandos, inmediatos, destino, tipo de resultado y controles de cada instrucción. La señal valid acompaña a cada vía. Una burbuja puede conservar valores en los buses, pero no produce escrituras ni se considera instrucción retirada.")
table(["Recurso","Capacidad por ciclo","Implementación"],[
    ("Fetch y Decode","Hasta 2 instrucciones","Dos lecturas de imem y dos decodificadores"),
    ("EX","Hasta 2 operaciones ALU","Una ALU por vía"),
    ("Register File","4 lecturas y 2 escrituras","regfile_dual"),
    ("Memoria de datos","1 Load o Store","Un dmem con selector de vía"),
    ("Branch","1 resolución","Comparador y destino compartidos"),
],[4.2,4.6,8.4])
heading("2.1 Flujo de una pareja válida",2)
para("Si no hay dependencias ni conflicto, los dos PC consecutivos permanecen identificados durante EX, MEM y WB. La ALU de cada vía calcula su propio resultado. Si una de las instrucciones requiere memoria, solo ella alimenta dmem; la otra puede completar su resultado ALU. En WB se habilitan hasta dos escrituras, cada una condicionada por valid y RegWrite. La edad de las instrucciones no se intercambia aunque una vía use un recurso compartido.")

new_page("3 Controller e Issue Unit")
para("Cada vía usa el mismo Controller para decodificar opcode, funct3 y funct7 y generar operación ALU, tipo de inmediato, lectura o escritura de memoria, branch, jump y selección de writeback. La Issue Unit usa esos atributos, los registros fuente realmente leídos, el destino y valid para decidir la emisión. La vía 1 nunca se emite sin la vía 0: esto preserva el orden del programa.")
table(["Situación en ID","Emisión","Acción sobre el par pendiente"],[
    ("La antigua depende de un Load en EX","0","Retener ambas instrucciones y PC de fetch"),
    ("La joven depende de un Load en EX","1","Emitir antigua; conservar y desplazar joven"),
    ("RAW entre antigua y joven","1","Emitir antigua; reagrupar joven con la siguiente"),
    ("Dos memorias o dos controles","1","Separar operaciones por el recurso único"),
    ("Independientes y sin conflicto","2","Emitir ambas; traer el siguiente par"),
],[6.8,2.0,8.4])
heading("3.1 Conservación y reagrupamiento",2)
para("Si se emite una sola instrucción, la joven se copia a la posición antigua de IF/ID y se completa el par con la siguiente instrucción de imem. fetch_pc avanza cuatro bytes. Si se emiten dos, entra un par nuevo y fetch_pc avanza ocho bytes. Si no se emite ninguna, IF/ID y fetch_pc se conservan. Un redirect de branch tiene prioridad y descarta el par joven del camino incorrecto.")
heading("3.2 Dos escrituras al mismo registro",2)
para("Cuando ambas instrucciones escriben el mismo rd sin dependencia RAW, la escritura de la vía 1 prevalece por ser la más joven. Los puertos ignoran rd=x0. Esta regla se implementa en regfile_dual y se comprueba en el caso 1.")
heading("3.3 Ejemplo de emisión parcial",2)
para("En el caso 2, los stores de PC=24 y PC=28 compiten por el mismo puerto. En el primer ciclo se emite el store antiguo de PC=24 y se retiene PC=28. En el ciclo siguiente, PC=28 ocupa la vía antigua y se agrupa con la instrucción siguiente. El testbench compara los PC retirados con la secuencia esperada para comprobar que ninguna operación se perdió ni se repitió.")
table(["Par en ID","Issue","Par de ID después del flanco"],[
    ("PC=24, PC=28; ambos SW","Solo PC=24","PC=28, PC=32"),
    ("PC=28, PC=32; sin conflicto","Según dependencias","Siguiente par consecutivo"),
],[6.3,3.0,7.9])

new_page("4 Forwarding, hazards y stalls")
para("Los operandos leídos en ID pueden quedar obsoletos antes de llegar a EX. Por eso cada operando de cada vía pasa por un selector de forwarding. El selector compara su rs con los rd válidos de MEM y WB, y elige el productor más reciente. Una carga en MEM no se reenvía como resultado ALU, porque ese bus contiene la dirección de memoria, no el dato cargado.")
table(["Prioridad","Fuente","Motivo"],[
    ("1","MEM vía 1","Resultado más reciente de un par anterior"),
    ("2","MEM vía 0","Más reciente que cualquier resultado en WB"),
    ("3","WB vía 1","Resultado joven del par que está en WB"),
    ("4","WB vía 0","Último productor disponible"),
    ("5","Register File","No existe coincidencia válida"),
],[2.5,4.0,10.7])
heading("4.1 RAW dentro del par",2)
para("Si la instrucción joven lee un registro que la antigua escribe, la Issue Unit las separa. B no promete forwarding dentro del mismo ciclo de EX; la joven espera un ciclo y puede recibir el resultado por las rutas entre etapas. Esta política es conservadora, respeta el orden y evita usar un dato aún no calculado.")
heading("4.2 Load Use",2)
para("Si una carga en EX produce un registro que necesita la instrucción antigua en ID, se emiten cero instrucciones: IF/ID y fetch_pc quedan retenidos, EX recibe una burbuja y el consumidor avanza cuando el valor puede llegar desde WB. Si solo depende la joven, puede emitirse la antigua y conservarse la joven.")
heading("4.3 Burbujas y prioridad",2)
para("Las comparaciones ignoran rd=x0 y productores sin valid o sin RegWrite. En MEM la vía 1 tiene prioridad sobre la vía 0 si ambas producen el mismo registro; MEM precede a WB. Así se conserva la semántica de la escritura más reciente.")
heading("4.4 Qué prueban los programas",2)
table(["Situación","Decisión que debe verse"],[
    ("Caso 1: productor ALU y consumidor próximo","Forwarding desde MEM o WB de la vía correcta"),
    ("Caso 1: x5 escrito por dos instrucciones","Resultado joven en x5 y en su consumidor"),
    ("Caso 4: LW seguido de ADD dependiente","Un ciclo sin emisión y valor cargado desde WB"),
],[7.7,9.5])

new_page("5 Memoria, branches y flushing")
heading("5.1 Un puerto de memoria de datos",2)
para("Solo existe una instancia de dmem. El selector toma dirección, dato y funct3 de la vía que contiene el Load o Store válido. No se fija la memoria a una posición del par: puede coexistir con una ALU en vía 0 o vía 1. Dos accesos de memoria se emiten en ciclos distintos. El dato de un store también puede proceder del forwarding.")
heading("5.2 Un recurso de branch",2)
para("La Issue Unit separa dos instrucciones de control del mismo par. En EX, un multiplexor elige los operandos y PC de la vía que contiene el branch o jump. Un solo comparador y un solo cálculo de destino resuelven la redirección. Se soportan BEQ, BNE, BLT, BGE, BLTU, BGEU, JAL y JALR dentro del alcance heredado de A.")
table(["Posición del control tomado","Qué se conserva","Qué se anula"],[
    ("Vía 0, la antigua","La instrucción de control y las más antiguas en MEM/WB","Vía 1 del mismo par e instrucciones jóvenes en ID"),
    ("Vía 1, la joven","Vía 0 del mismo par y las más antiguas","Instrucciones jóvenes en ID"),
    ("Control no tomado","Ambas instrucciones válidas","Nada por control"),
],[5.0,6.1,6.1])
heading("5.3 Efectos laterales",2)
para("La redirección actualiza fetch_pc. Los bits valid de las instrucciones anuladas se ponen a cero antes de MEM/WB. MemWrite y RegWrite se activan solo si la instrucción correspondiente sigue válida. El caso 3 comprueba que los stores de las rutas equivocadas no modifican memoria.")
heading("5.4 Escenarios de control verificados",2)
para("El programa del caso 3 distingue las dos posiciones: el BEQ de PC=8, en la vía antigua, salta a PC=20 y debe anular el store de PC=12. El BEQ de PC=40, en la vía joven, salta a PC=52 y conserva la instrucción antigua de PC=36. Los branches de PC=24 y PC=28 no se toman. El JAL de PC=56 deja el enlace PC+4=60 en x7. Estas situaciones se comprueban con el estado final, la secuencia de PC retirados y los bits de redirección.")

new_page("6 Verificación funcional y waveforms")
para("La suite usa programas Assembly propios de E2, sus memorias .mem y testbenches con aserciones. Cada caso tiene un store terminal; el testbench termina tras comprobarlo o falla por timeout. Además del estado final, se compara la secuencia exacta de PC retirados. Los VCD se generan directamente con Icarus Verilog y quedan listos para abrir en GTKWave.")
table(["Caso","Riesgo principal","Estado esperado"],[
    ("1","Dos ALU, RAW, doble escritura y forwarding","x5=9; x8=12; memoria[96]=12"),
    ("2","Memoria en ambas vías y conflicto","memoria[96]=25; [100]=8; [104]=25"),
    ("3","Branch en ambas posiciones y flush","x7=60; memoria[100]=6; stores anulados"),
    ("4","Load Use y emisión cero","x3=25; x4=26; memoria[100]=26"),
],[2.0,7.1,8.1])
heading("6.1 Dos ALU, RAW y doble escritura",2)
para("El caso 1 inicia con dos ADDI independientes (PC=0 y PC=4) y ejecuta después ADD y otra ADDI en paralelo. Dos instrucciones escriben x5 sin RAW; el valor joven esperado es 9. La dependencia entre x7 y x8 obliga a separar el par y reagrupar la joven. El resultado final es x8=12 y memoria[96]=12. El testbench exige emisión doble, separación RAW, forwarding en ambas vías, doble escritura al mismo rd y retiro de PC 0, 4, ..., 40 sin huecos ni repeticiones.")
waveform_placeholder(1,"clk, PC e instrucción en ID por vía, issue0/issue1, split_raw, valid E/M/W, forward_a/forward_b, rd_w, wb_value y memoria[96].","Identificar el primer par de dos ALU, la separación RAW, la escritura simultánea a x5 y el store final de 12.")

new_page("6.2 Memoria compartida en ambas vías")
para("El caso 2 combina SW en vía 0 con una operación ALU en vía 1; más adelante combina ALU en vía 0 con LW en vía 1. Dos SW consecutivos deben separarse porque comparten el puerto de datos. Los resultados esperados son x3=7, x4=8 y x5=25; memoria[96]=25, memoria[100]=8 y memoria[104]=25. El testbench observa la selección real de ambas vías para memoria y el conflicto estructural.")
table(["Par de instrucciones","Decisión esperada","Recurso"],[
    ("SW + ADDI","Emitir ambas si no hay RAW","Memoria desde vía 0"),
    ("ADDI + LW","Emitir ambas si no hay RAW","Memoria desde vía 1"),
    ("SW + SW","Emitir antigua; reagrupar joven","Un acceso por ciclo"),
],[6.3,6.1,4.8])
waveform_placeholder(2,"PC e instrucción en ID por vía, issue0/issue1, split_resource, valid M, mem_lane1, mem_address, mem_write, mem_store_data, rd_w y wb_value.","Mostrar el cambio de selección del único puerto entre vía 0 y vía 1 y la separación de los dos stores.")

new_page("6.3 Branches en ambas posiciones")
para("El caso 3 incluye un BEQ tomado en vía 0 en PC=8 que anula el store joven de PC=12; branches no tomados en ambas posiciones; un BEQ tomado en vía 1 en PC=40; y un JAL en PC=56. Al final x3=3, x4=4, x5=5, x6=6, x7=60 y memoria[100]=6. Las direcciones 108, 112 y 116 no deben recibir los stores de rutas anuladas.")
table(["PC de control","Situación","Efecto esperado"],[
    ("8","BEQ tomado en vía 0","Anular compañera joven y redirigir a PC=20"),
    ("24 y 28","BEQ no tomados en ambas vías","Continuar secuencia"),
    ("40","BEQ tomado en vía 1","Conservar vía 0 y redirigir a PC=52"),
    ("56","JAL","Guardar enlace 60 en x7; anular store de PC=60"),
],[2.5,6.0,8.7])
waveform_placeholder(3,"PC y valid de ambas vías en EX/MEM, select_control1, shared_branch_taken, shared_target, taken0/taken1, redirect, mem_write y direcciones 100/108/112/116.","Explicar en qué ciclo se toma cada salto, qué vía se conserva y por qué los stores anulados no escriben.")

new_page("6.4 Load Use y emisión cero")
para("El caso 4 escribe 25 en memoria[96], carga ese valor en x3 y lo usa inmediatamente en ADD para producir x4=26. El consumidor no puede entrar en EX mientras la carga está en EX. La Issue Unit emite cero, mantiene el par en ID e inserta una burbuja. Cuando el dato cargado llega a WB, el ADD continúa y el store final escribe 26 en memoria[100].")
table(["Comprobación","Esperado","Observado por el testbench"],[
    ("Load Use","Un stall de cero emisiones","seen_stall=1"),
    ("Dos memorias en el flujo","Separación de recurso","seen_resource=1"),
    ("Estado final","x3=25; x4=26; memoria[100]=26","Aserciones PASS"),
    ("Orden de retiro","PC 0, 4, 8, 12, 16, 20","Secuencia exacta comprobada"),
],[5.4,5.8,6.0])
waveform_placeholder(4,"PC e instrucción en ID, issue0/issue1, stall_load, valid E/M/W, result_src E/M/W, forward_a/forward_b, wb_value y memoria[96]/[100].","Señalar el ciclo en que issue0=issue1=0, la burbuja en EX y la llegada de 25 desde WB al ADD.")

new_page("7 Equivalencia y comparación preliminar A frente a B")
heading("7.1 Equivalencia funcional",2)
para("Un testbench ejecuta simultáneamente A y B con el mismo archivo .mem y los mismos registros inicializados. Tras 130 ciclos compara los 32 registros y las 256 palabras de memoria de datos. Pasan e1_1, e1_2, e1_3, e1_4 y e1_isa_ext. Esta prueba contrasta el estado arquitectónico final; los cuatro casos dirigidos de E2 comprueban además decisiones internas de emisión y control.")
heading("7.2 Criterio de medición",2)
para("La comparación preliminar usa e1_2.mem sin cambios: ocho instrucciones reales. Ambos procesadores comienzan tras el mismo reset y la corrida termina al escribir el store terminal en dirección de byte 100. Así no se incluyen los NOP de relleno posteriores al programa. IPC se calcula como ocho instrucciones completadas divididas entre ciclos hasta ese evento. Se supone el mismo período de reloj; esta comparación no mide frecuencia máxima de síntesis.")
table(["Configuración","Instrucciones","Ciclos","IPC","Speedup frente a A"],[
    ("A Single Issue","8","11","0,727","1,00"),
    ("B Dual Issue","8","10","0,800","1,10"),
],[4.2,3.1,2.6,2.7,4.6])
para("B reduce un ciclo en este programa, pero no alcanza IPC=2. Las dependencias RAW, la necesidad de respetar el orden y los accesos compartidos limitan la doble emisión. Es una comparación preliminar de E2, no la evaluación final de dos programas y tres arquitecturas exigida para EF.")
heading("7.3 Evidencia visual pendiente",2)
para("El testbench de comparación genera tests/e2_compare.vcd. La captura de GTKWave debe alinear el inicio, la escritura terminal, issue0/issue1 y valid W de A y B.")
p=para("Figura pendiente. Captura real de GTKWave para la comparación A frente a B.")
for r in p.runs: r.bold=True
para("Señales que debe mostrar: clk, reset, PC de A, PC y valid de ambas vías de B, issue0/issue1, MemWrite, DataAdr y mem_address.")
space=doc.add_paragraph(" "); space.add_run("\n"*18)
cap=para("Figura 6. Espacio reservado para la waveform real de tests/e2_compare.vcd.",
         align=WD_ALIGN_PARAGRAPH.CENTER,after=6)
for r in cap.runs: r.italic=True; r.font.size=Pt(9)
para("Lectura prevista: explicar los ciclos que producen la diferencia de 11 frente a 10 y comprobar el mismo store terminal.")

new_page("8 Conclusiones, reproducción y pendientes")
para("El procesador B ya ejecuta hasta dos instrucciones independientes por ciclo, conserva el orden cuando una sola puede avanzar y usa forwarding, stalls y flushes para proteger el estado arquitectónico. La memoria y el branch son recursos compartidos y pueden asignarse desde cualquiera de las dos vías. Las pruebas dirigidas y la equivalencia con A respaldan la funcionalidad del subconjunto de instrucciones implementado.")
heading("8.1 Cómo reproducir",2)
para("Desde la carpeta E2, con Python e Icarus Verilog instalados, ejecutar ./run_e1.ps1 y después ./run_e2.ps1 en PowerShell. El segundo script genera las memorias, compila testbenches, ejecuta los cuatro casos E2, compara A/B en cinco programas y calcula la medición preliminar. Las waveforms de simulación se guardan en tests/e2_1.vcd a tests/e2_4.vcd.")
heading("8.2 Pendientes para la versión de entrega",2)
para("Sustituir los espacios reservados por capturas reales de GTKWave, legibles y con las señales señaladas en cada caso. Debajo de cada captura explicar el ciclo decisivo, los valores intermedios y el resultado. Revisar que los números de página del índice correspondan a la versión final. Preparar la defensa individual de Issue Unit, forwarding, memoria y control.")
table(["Apartado pendiente","Acción antes de subir"],[
    ("Figuras 2 a 5","Capturar cada caso E2 en GTKWave y explicar el ciclo decisivo"),
    ("Figura 6","Capturar A y B con el mismo criterio de inicio y store terminal"),
    ("Índice y paginación","Actualizar después de insertar las capturas"),
    ("Defensa individual","Ensayar RAW, Load Use, branch en ambas posiciones y recursos"),
],[5.8,11.4])
heading("Fuentes",2)
para("Arquitectura de Computadoras. Proyecto 2, Diseño e implementación de un procesador RISC-V superescalar Dual-Issue con optimización microarquitectónica, secciones 2 a 5. Indicaciones generales y rúbrica del Proyecto 2, sección 3. Código y testbenches en la carpeta E2 de este repositorio.")

doc.save(DOCX)
print(DOCX)
