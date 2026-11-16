"""Build the EF report with the E2 cover design and final-delivery wording.

The body deliberately reserves labelled spaces for waveforms; it never invents
or renders waveform evidence. Run from any working directory.
"""
from pathlib import Path
import io
import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, Flowable, KeepTogether,
)

HERE = Path(__file__).resolve().parent
EF = HERE.parent
ROOT = EF.parent
SOURCE_COVER = ROOT / "E2_LadronDeGuevara_Burgos_Morales_Heredia" / "informe" / "Informe_E2_Proyecto2.pdf"
DATAPATH = HERE / "datapath_e2_refinado.png"
WAVE_RAW = EF / "resultados" / "waveforms" / "captura_01_raw_load_use.png"
WAVE_MEM = EF / "resultados" / "waveforms" / "captura_02_memoria_emision.png"
WAVE_BTB = EF / "resultados" / "waveforms" / "captura_03_btb.png"
WAVE_STAGE_A = EF / "resultados" / "waveforms" / "captura_04_docente_etapa_A.png"
WAVE_STAGE_B = EF / "resultados" / "waveforms" / "captura_05_docente_etapa_B.png"
WAVE_STAGE_C = EF / "resultados" / "waveforms" / "captura_06_docente_etapa_C.png"
WAVE_STAGE_D = [
    EF / "resultados" / "waveforms" / f"captura_07{part}_docente_etapa_D.png"
    for part in "abc"
]
OUTPUT = HERE / "Informe_Final_Proyecto2_BTB.pdf"
BLUE = colors.HexColor("#1599c7")
NAVY = colors.HexColor("#17324d")
PALE = colors.HexColor("#eaf4f8")
LIGHT = colors.HexColor("#f3f6f8")
GREY = colors.HexColor("#5d6973")

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="EFTitle", fontName="Arial-Bold", fontSize=17, leading=21,
                          textColor=NAVY, spaceAfter=8))
styles.add(ParagraphStyle(name="EFSubtitle", fontName="Arial", fontSize=10.5, leading=15,
                          textColor=GREY, spaceAfter=15))
styles.add(ParagraphStyle(name="EFH1", fontName="Arial-Bold", fontSize=12.5, leading=16,
                          textColor=NAVY, spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle(name="EFH2", fontName="Arial-Bold", fontSize=10, leading=13,
                          textColor=NAVY, spaceBefore=10, spaceAfter=4))
styles.add(ParagraphStyle(name="EFBody", fontName="Arial", fontSize=9, leading=13,
                          spaceAfter=6))
styles.add(ParagraphStyle(name="EFSmall", fontName="Arial", fontSize=7.7, leading=11,
                          spaceAfter=4))
styles.add(ParagraphStyle(name="EFCaption", fontName="Arial", fontSize=8, leading=11,
                          textColor=GREY, spaceBefore=4, spaceAfter=10))
styles.add(ParagraphStyle(name="EFTableHead", fontName="Arial-Bold", fontSize=7.5,
                          leading=9, textColor=colors.white))
styles.add(ParagraphStyle(name="EFTable", fontName="Arial", fontSize=7.6, leading=10))
styles.add(ParagraphStyle(name="EFNote", fontName="Arial", fontSize=8.5, leading=12,
                          textColor=NAVY, backColor=PALE, borderPadding=8, spaceAfter=10))


def P(text, style="EFBody"):
    return Paragraph(text, styles[style])


def heading(text):
    return P(text, "EFH1")


def subheading(text):
    return P(text, "EFH2")


def table(headers, rows, widths, row_background=True):
    data = [[P(str(v), "EFTableHead") for v in headers]]
    data += [[P(str(v), "EFTable") for v in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, BLUE),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#c9d3da")),
    ]
    if row_background:
        cmds.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]))
    t.setStyle(TableStyle(cmds))
    return t


class BtbAddition(Flowable):
    def __init__(self, width=506, height=112):
        super().__init__()
        self.width, self.height = width, height

    def draw(self):
        c = self.canv
        boxes = [
            (7, 46, 105, 48, "IF: PC / PC+4"),
            (146, 46, 105, 48, "BTB: 16 entradas"),
            (285, 46, 105, 48, "MUX próximo PC"),
            (424, 46, 75, 48, "ID / EX"),
        ]
        for x, y, w, h, label in boxes:
            c.setFillColor(PALE if "BTB" in label else LIGHT)
            c.setStrokeColor(BLUE if "BTB" in label else NAVY)
            c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
            c.setFont("Arial-Bold", 8)
            c.setFillColor(NAVY)
            c.drawCentredString(x+w/2, y+25, label)
        c.setStrokeColor(NAVY)
        c.setFillColor(NAVY)
        for x1, x2 in ((112, 146), (251, 285), (390, 424)):
            c.line(x1, 70, x2-5, 70)
            p=c.beginPath(); p.moveTo(x2-5,67); p.lineTo(x2,70); p.lineTo(x2-5,73); p.close()
            c.drawPath(p, fill=1, stroke=0)
        c.setFont("Arial", 7.3)
        c.setFillColor(GREY)
        c.drawString(151, 30, "Consulta de 2 PC; predicción y destino hacia el MUX")
        c.drawString(125, 8, "EX resuelve control y devuelve PC real / actualización al BTB")
        c.setStrokeColor(BLUE)
        c.line(461, 42, 461, 20); c.line(461, 20, 35, 20); c.line(35, 20, 35, 42)


class WaveSpace(Flowable):
    def __init__(self, label):
        super().__init__()
        self.width, self.height = 506, 405
        self.label = label

    def draw(self):
        c = self.canv
        c.setStrokeColor(colors.HexColor("#93a8b5"))
        c.setDash(5, 4)
        c.roundRect(0, 0, self.width, self.height, 8, fill=0, stroke=1)
        c.setDash()
        c.setFillColor(GREY)
        c.setFont("Arial-Bold", 11)
        c.drawCentredString(self.width/2, self.height/2+10, "ESPACIO RESERVADO PARA WAVEFORM")
        c.setFont("Arial", 8.5)
        c.drawCentredString(self.width/2, self.height/2-8, self.label)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(0.6)
    canvas.line(45, 40, 551, 40)
    canvas.setFillColor(GREY)
    canvas.setFont("Arial", 7.5)
    canvas.drawString(45, 28, "Proyecto 2 · Entrega final · BTB")
    canvas.drawRightString(551, 28, f"Página {doc.page+1}")
    canvas.restoreState()


def body_pdf():
    out = io.BytesIO()
    doc = SimpleDocTemplate(out, pagesize=(596, 842), leftMargin=45,
                            rightMargin=45, topMargin=48, bottomMargin=55,
                            title="Informe final Proyecto 2 - BTB")
    s = []
    s += [P("INFORME TÉCNICO DE LA ENTREGA FINAL", "EFTitle"),
          P("Procesadores A/B/C y optimización Branch Target Buffer", "EFSubtitle")]
    s += [heading("1. Resumen y alcance"),
          P("Se comparan tres procesadores RV32I de cinco etapas: A, pipeline Single-Issue; B, Dual-Issue In-Order con dos vías y recursos de memoria y branch compartidos; y C, copia de B con Branch Target Buffer (BTB). Los dos programas de evaluación —uno del docente y uno propio— se ejecutan sin cambiar el Assembly entre versiones. En las seis corridas se verificó el estado funcional y se midieron instrucciones retiradas, ciclos, IPC, CPI y speedup."),
          P("El BTB se incorporó a la ruta de búsqueda y control de B. Las ALU, la Issue Unit, el forwarding y los recursos compartidos de E2 permanecen. La memoria de datos se amplió de 256 a 512 palabras en A/B/C por igual para admitir la base 1536 del programa docente; este ajuste de capacidad no se atribuye a la optimización."),
          subheading("Configuraciones comparadas"),
          table(["Configuración", "Arquitectura"], [
              ["A", "Pipeline Single-Issue de cinco etapas."],
              ["B", "Dual-Issue In-Order con recursos de memoria y branch compartidos."],
              ["C", "B con Branch Target Buffer aprobado verbalmente por el docente en clase."],
          ], [100,406]),
          Spacer(1,10),
          P("Fuente de requisitos: Proyecto2_Enunciado.pdf; Proyecto2_Indicaciones_Generales_Rubrica.pdf; Programa-proyecto-del-docente.pdf. La reproducibilidad y los límites de esta versión se detallan en la sección 7.", "EFSmall"),
          PageBreak()]

    s += [heading("2. Arquitectura y cambio de C"),
          P("B obtiene hasta dos instrucciones en IF, las mantiene en una pareja ordenada en ID y emite cero, una o dos según dependencias y conflictos. Conserva dos ALU y un solo puerto de datos y recurso de branch. C conserva este datapath y añade una consulta anticipada del destino al lado de IF."),
          Image(str(DATAPATH), width=506, height=191),
          P("Figura 1. Datapath B de E2 que se reutiliza como base de C; la adición al frente se muestra debajo.", "EFCaption"),
          BtbAddition(),
          P("Figura 2. Adición funcional del BTB: lectura en IF, selección del PC y actualización desde EX. El metadato de PC predicho acompaña la instrucción por IF/ID e ID/EX.", "EFCaption"),
          subheading("2.1 Tabla y política"),
          P("El BTB tiene 16 entradas de mapeo directo. Usa PC[5:2] como índice y compara una etiqueta de PC completa; cada entrada guarda valid, destino de 32 bits y contador saturante de dos bits. Dos lecturas combinacionales atienden PC y PC+4. Un salto tomado instala o refuerza la predicción; uno no tomado debilita su contador. JAL y JALR se instalan como fuertemente tomados."),
          P("El almacenamiento lógico es 16 × (1 + 32 + 32 + 2) = 1072 bits, sin contar multiplexores y comparadores. La implementación se encuentra en rtl/btb.v y la conexión al pipeline en rtl/dualissue.v de C.", "EFSmall"),
          PageBreak()]

    s += [heading("3. Predicción, resolución y corrección"),
          table(["Momento", "Acción en C"], [
              ["IF", "Consulta los dos PC. Una predicción tomada en la primera posición guarda solo la instrucción antigua y usa el destino en el siguiente fetch. Si predice la segunda, guarda el par y cambia el siguiente fetch al destino."],
              ["ID", "Guarda el PC siguiente predicho junto con la instrucción. En emisión parcial, reagrupa la joven y conserva ese metadato. No empareja una instrucción de control predicha tomada con su destino antes de resolverla."],
              ["EX", "El recurso compartido obtiene condición y destino reales. Compara PC real con PC predicho. Si difieren, redirige y anula solo instrucciones jóvenes; si coinciden, no hace flush. Actualiza el BTB."],
          ], [72,434]),
          subheading("3.1 Corrección y prioridades"),
          P("La predicción solo modifica el camino especulativo. El resultado arquitectónico depende del branch resuelto en EX. Un control en vía 0 puede anular su compañera joven cuando se corrige la predicción; un control en vía 1 conserva la vía 0. Los bits valid impiden que instrucciones anuladas escriban memoria o registros. Se mantiene una sola actualización de BTB por ciclo, conforme al recurso de branch compartido de B."),
          subheading("3.2 Validación específica"),
          P("La prueba unitaria cubre miss frío, instalación de destino, decremento y recuperación del contador, lectura de ambas posiciones y colisión de índice con etiqueta diferente. La regresión de C pasa cuatro casos E2 y cinco comparaciones E1. Los testbenches de ambos programas finales comprueban resultados y terminan por éxito o error explícito."),
          heading("4. Programas de evaluación"),
          subheading("4.1 Programa del docente"),
          P("Se transcribieron las 90 instrucciones del PDF y se contrastó su secuencia. Utiliza x1=1536 y las etapas A–D; sus estados se comprueban en los stores de cierre de cada etapa. El testbench verifica los 32 registros y las posiciones de memoria esperadas en esos instantes. A/B/C retiran 312 instrucciones dinámicas antes de fin y producen el mismo estado final."),
          subheading("4.2 Programa propio"),
          P("Genera 12 palabras con valores 3…14 desde la dirección 1024 y las recorre dos veces. Combina store seguido de load, dependencia Load-Use, suma, conteo por umbral, hash recurrente, branches condicionales y bucles de retorno. El código tiene 45 instrucciones estáticas; A/B/C retiran 268 instrucciones dinámicas antes de fin."),
          table(["Salida en memoria", "Significado", "Valor"], [
              ["1200", "Suma durante generación", "102"], ["1204", "Suma durante lectura", "102"],
              ["1208 / 1212", "Valores menores que 9 / mayores o iguales", "6 / 6"],
              ["1216", "Hash h ← 2h + dato", "16368"], ["1220 / 1224", "Suma de índices / marcador terminal", "66 / 1"],
          ], [100,336,70]),
          PageBreak()]

    s += [heading("5. Método y comparación cuantitativa"),
          P("Para cada programa se usa el mismo .mem, registros iniciales en cero, reloj y criterio de cierre en A/B/C. Los ciclos se cuentan al liberar reset y se cierran con el store terminal. Las retiradas se cuentan solo para PC anteriores a la etiqueta fin; su bucle infinito no entra en las cifras. IPC = retiradas/ciclos; CPI = ciclos/retiradas; speedup frente a una referencia = ciclos de referencia/ciclos de la configuración, suponiendo igual período de reloj."),
          table(["Programa", "Conf.", "Ret.", "Ciclos", "IPC", "CPI", "vs A", "vs B"], [
              ["Docente", "A", "312", "458", "0.6812", "1.4679", "1.0000", "0.8428"],
              ["Docente", "B", "312", "386", "0.8083", "1.2372", "1.1865", "1.0000"],
              ["Docente", "C", "312", "320", "0.9750", "1.0256", "1.4313", "1.2063"],
              ["Propio", "A", "268", "363", "0.7383", "1.3545", "1.0000", "0.7934"],
              ["Propio", "B", "268", "288", "0.9306", "1.0746", "1.2604", "1.0000"],
              ["Propio", "C", "268", "233", "1.1502", "0.8694", "1.5579", "1.2361"],
          ], [75,44,43,48,56,56,92,92]),
          P("Tabla 1. Seis corridas con igualdad funcional. La columna vs B para A expresa ciclos_B/ciclos_A; se conserva por simetría de la tabla.", "EFCaption"),
          subheading("5.1 Señales de actividad y BTB"),
          table(["Programa", "Conf.", "Doble emisión", "Stalls Load-Use", "Emisión parcial", "BTB tomado", "Correctas / correcciones"], [
              ["Docente", "B", "140", "11", "99", "—", "—"],
              ["Docente", "C", "85", "11", "152", "63", "57 / 32"],
              ["Propio", "B", "110", "24", "83", "—", "—"],
              ["Propio", "C", "79", "24", "105", "32", "36 / 6"],
          ], [72,38,83,80,78,69,86]),
          P("Tabla 2. 'Correctas' cuenta todas las decisiones de siguiente PC, incluidas continuaciones secuenciales; no debe dividirse por la columna BTB tomado. Las métricas de control filtran PC &lt; fin para excluir incluso la primera resolución del bucle terminal. Los contadores de doble emisión y emisión parcial se observan al cierre del store terminal.", "EFCaption"),
          PageBreak()]

    s += [heading("6. Interpretación de resultados"),
          P("B reduce ciclos frente a A en el programa docente (458→386) y en el propio (363→288), porque puede emitir dos instrucciones independientes. No llega al IPC ideal de 2: RAW dentro de la pareja, Load-Use, un único puerto de memoria, branches y emisiones parciales limitan la ocupación. El programa propio exhibe 24 stalls Load-Use en B y C; el docente, 11."),
          P("C baja de 386 a 320 ciclos en el docente (speedup 1.2063 frente a B) y de 288 a 233 en el propio (1.2361). En los bucles repetidos, el BTB anticipa destinos tomados y evita parte del vaciado tardío del camino secuencial. El resultado no se debe a modificar el Assembly ni a duplicar recursos. Excluyendo fin, en el docente hay 63 predicciones de tomado, 57 decisiones de PC correctas y 32 correcciones; en el propio, 32, 36 y 6, respectivamente."),
          P("C muestra menos ciclos de doble emisión que B (85 frente a 140 en el docente; 79 frente a 110 en el propio) y más emisiones parciales. La regla que evita emparejar una instrucción de control predicha tomada con su destino consume oportunidades de issue. Aun así, el menor costo de los cambios de flujo predomina en estos dos programas. Los stalls Load-Use no cambian, coherente con una optimización de control y no de forwarding."),
          heading("7. Límites, reproducción y siguientes evidencias"),
          P("El BTB es de mapeo directo: dos PC con igual índice compiten por una entrada. Un branch alternante o un destino JALR cambiante pueden degradar la predicción. No se ha sintetizado ni medido frecuencia máxima; por tanto, los speedups reportados son de ciclos y presuponen el mismo período de reloj. El docente aprobó verbalmente la elección de BTB durante la clase, según comunicación del equipo."),
          P("Para reproducir desde EF/ en PowerShell con Python e Icarus Verilog: <b>./run_code_checks.ps1</b>. El script ensambla ambos programas y ejecuta A, B y C, la prueba unitaria del BTB y la regresión E2/E1 de C. Fuentes y resultados legibles: programas/propio.S, programas/docente.S, testbenches/, resultados/comparacion_codigo.md y BTB_DOCUMENTACION.md."),
          PageBreak()]

    placeholders = [
        ("8.1 Cierre de etapa A del docente", "Store en x1+8; comprobar x5=11, x6=5, x10=12 y memoria."),
        ("8.2 Cierre de etapa B del docente", "Store en x1+20; comprobar x11…x18 y memoria x1+12…20."),
        ("8.3 Cierre de etapa C del docente", "Store en x1+32; comprobar x19=12, x21=24, x22=18, x24=24."),
        ("8.4 Cierre de etapa D del docente", "Store en x1+52; comprobar x28=74, x29=4, x31=1 y memoria."),
        ("8.5 Caso clave: RAW y Load-Use", "PC e instrucciones dependientes; issue0/issue1, stall, forwarding y WB."),
        ("8.6 Caso clave: conflicto de memoria y doble emisión", "Par de instrucciones, split_resource, mem_lane1, issue y retiro."),
        ("8.7 BTB: predicción y corrección", "fetch_pc, hit, predict, target, PC predicho/real, redirect y valid."),
    ]
    raw_rows = [
        ("clk", "Reloj de simulación.", "Cada período corresponde a un ciclo de 10 ns."),
        ("wave_pc_d0", "PC de la instrucción más antigua en ID.", "0x28 para lw; después 0x2C para add."),
        ("wave_pc_d1", "PC de la instrucción joven en ID.", "0x2C cuando add acompaña a lw."),
        ("wave_instr_d0", "Instrucción codificada de vía 0.", "0x0000A483 = lw x9, 0(x1)."),
        ("wave_instr_d1", "Instrucción codificada de vía 1.", "0x00920233 = add x4, x4, x9."),
        ("issue0", "Autoriza emitir vía 0.", "1 al emitir lw; 0 durante el stall."),
        ("issue1", "Autoriza emitir vía 1.", "0 cuando la pareja tiene dependencia RAW."),
        ("split_raw", "Detecta dependencia dentro de la pareja.", "1 con lw y add en ID."),
        ("stall_load", "Detiene emisión por Load-Use.", "1 aproximadamente entre 95 y 105 ns."),
        ("wave_pc_e0", "PC almacenado en EX, vía 0.", "Permite seguir la carga; requiere valid_e para afirmar ejecución."),
        ("wave_pc_w0", "PC almacenado en WB, vía 0.", "Permite seguir la carga hasta WB; requiere valid_w."),
        ("wave_x9", "Registro destino de la carga.", "Pasa de 0 a 3 cerca de 120 ns."),
        ("wave_x4", "Acumulador de la generación.", "Pasa de 0 a 3 cerca de 140 ns."),
    ]
    memory_rows = [
        ("clk", "Reloj de simulación.", "Un ciclo cada 10 ns."),
        ("wave_pc_d0", "PC de la vía antigua en ID.", "0x24 para sw; luego 0x28 para lw y 0x2C para add."),
        ("wave_pc_d1", "PC de la vía joven en ID.", "0x28 para lw; después 0x30 para slt."),
        ("wave_instr_d0", "Código de la instrucción antigua.", "0x0080A023 = sw x8, 0(x1)."),
        ("wave_instr_d1", "Código de la instrucción joven.", "0x0000A483 = lw x9, 0(x1)."),
        ("issue0", "Emisión de la vía antigua.", "1 al aceptar sw; 0 en la espera posterior."),
        ("issue1", "Emisión de la vía joven.", "0 para sw/lw; 1 para add/slt."),
        ("split_resource", "Conflicto por recurso compartido.", "1 cerca de 75–85 ns para dos accesos a memoria."),
        ("double_issue_count", "Cuenta parejas emitidas.", "Sube de 4 a 5 cerca de 115 ns."),
        ("mem_lane1", "Selecciona vía 1 en el puerto de datos.", "Permanece 0: el acceso válido usa vía 0."),
        ("mem_write", "Habilita escritura de datos.", "1 cerca de 95 ns para sw."),
        ("mem_address", "Dirección del puerto de datos.", "0x400 (1024) en sw y lw."),
        ("mem_store_data", "Dato escrito por sw.", "3 en la escritura de 0x400."),
        ("mem_read", "Dato devuelto a lw.", "3 cerca de 105 ns; X fuera de la lectura válida."),
        ("wave_valid_m0", "Validez de vía 0 en MEM.", "Permite interpretar el acceso de la vía antigua."),
        ("wave_valid_m1", "Validez de vía 1 en MEM.", "0 para la instrucción joven separada."),
    ]
    btb_rows = [
        ("clk", "Reloj de simulación.", "Un ciclo cada 10 ns."),
        ("fetch_pc", "PC base consultado en IF.", "0x4C cerca de 280 ns; la segunda consulta es 0x50."),
        ("btb_hit0", "Coincidencia BTB para fetch_pc.", "0 en la consulta destacada."),
        ("btb_hit1", "Coincidencia BTB para fetch_pc+4.", "1 cerca de 280 ns para PC 0x50."),
        ("predict0", "Predicción de tomado para vía 0.", "0 en la consulta destacada."),
        ("predict1", "Predicción de tomado para vía 1.", "1 para el branch de retorno."),
        ("btb_target0", "Destino asociado a vía 0.", "0 cuando no hay acierto de tabla."),
        ("btb_target1", "Destino asociado a vía 1.", "0x20 cuando hit1=1."),
        ("control_resolved", "Control válido que se resuelve en EX.", "1 cerca de 190 y 310 ns para el branch en 0x50."),
        ("branch_pc", "PC del control resuelto en EX.", "0x50 para el retorno; 0x3C para JAL intermedio."),
        ("predicted_next_pc", "Siguiente PC anticipado.", "0x54 en el primer retorno; 0x20 en el siguiente."),
        ("actual_next_pc", "Siguiente PC calculado en EX.", "0x20 en ambos retornos."),
        ("redirect", "Corrección y vaciado del camino joven.", "1 en 190 ns; 0 en 310 ns."),
        ("btb_prediction_count", "Conteo acumulado de predicciones tomadas.", "Sube de 0 a 1 en la ventana; no es un hit instantáneo."),
        ("btb_mispredict_count", "Conteo acumulado de correcciones.", "Sube de 1 a 2 tras la corrección de 190 ns."),
    ]
    stage_a_rows = [
        ("clk", "Reloj de simulación.", "Cada ciclo dura 10 ns."),
        ("wave_pc_mem", "PC del acceso elegido en MEM.", "0x2C, 0x30 y 0x34 para los tres stores."),
        ("mem_write", "Habilita escritura en memoria.", "1 durante los stores de cierre."),
        ("mem_address", "Dirección de memoria de datos.", "0x600, 0x604 y 0x608 (1536, 1540, 1544)."),
        ("wave_store_data", "Dato presentado al puerto de escritura.", "11, 5 y 12, respectivamente."),
        ("checkpoint_passed", "Bits de etapas comprobadas por testbench.", "Bit 0 pasa a 1 cerca de 126 ns, tras verificar A."),
        ("wave_x5", "Resultado de add x5, x3, x4.", "11 al cierre."),
        ("wave_x6", "Resultado de sub x6, x3, x4.", "5 al cierre."),
        ("wave_x10", "Valor del último store de A.", "12 al cierre."),
        ("wave_mem_0", "Memoria en 1536.", "Pasa a 11."),
        ("wave_mem_1", "Memoria en 1540.", "Pasa a 5."),
        ("wave_mem_2", "Memoria en 1544.", "Pasa a 12."),
    ]
    stage_b_rows = [
        ("clk", "Reloj de simulación.", "Un ciclo cada 10 ns."),
        ("wave_pc_mem", "PC del acceso elegido en MEM.", "0x4C, 0x54 y 0x60 en los stores de B."),
        ("mem_write", "Habilita escritura de datos.", "1 durante cada store."),
        ("mem_address", "Dirección del puerto de datos.", "0x60C, 0x610 y 0x614."),
        ("wave_store_data", "Dato que escribe cada store.", "7, 16 y 23, respectivamente."),
        ("checkpoint_passed", "Bits de etapas aprobadas.", "Pasa de 1 a 3 cerca de 256 ns: A y B verificadas."),
        ("wave_x11", "Carga desde 1536.", "11."),
        ("wave_x12", "Suma x11+x6.", "16."),
        ("wave_x13", "Carga desde 1540.", "5."),
        ("wave_x14", "Carga desde 1544.", "12."),
        ("wave_x15", "Diferencia x14−x13.", "7."),
        ("wave_x16", "Carga del resultado en 1548.", "7."),
        ("wave_x17", "Carga del resultado en 1552.", "16."),
        ("wave_x18", "Suma x16+x17.", "23."),
        ("wave_mem_3", "Memoria en 1548.", "7."),
        ("wave_mem_4", "Memoria en 1552.", "16."),
        ("wave_mem_5", "Memoria en 1556.", "23."),
    ]
    stage_c_rows = [
        ("clk", "Reloj de simulación.", "Un ciclo cada 10 ns."),
        ("wave_pc_mem", "PC del acceso elegido en MEM.", "0xE0 para el store final de C."),
        ("mem_write", "Habilita escritura de datos.", "1 antes del cierre en 2455 ns."),
        ("mem_address", "Dirección del puerto de datos.", "0x620 (1568) en el último store."),
        ("wave_store_data", "Dato escrito por el store final.", "24."),
        ("checkpoint_passed", "Bits de etapas aprobadas.", "Pasa de 3 a 7 cerca de 2456 ns."),
        ("wave_x19", "Índice de los bucles de C.", "12 al cierre; D lo reinicia a 0 después."),
        ("wave_x20", "Límite de los bucles de C.", "12 al cierre; D lo cambia a 6 después."),
        ("wave_x21", "Resultado del primer bucle.", "24 (0x18)."),
        ("wave_x22", "Resultado del segundo bucle.", "18 (0x12)."),
        ("wave_x24", "Resultado del tercer bucle.", "24 (0x18)."),
        ("wave_x26", "Umbral del tercer bucle.", "6."),
        ("wave_mem_6", "Memoria en 1560.", "24 (0x18)."),
        ("wave_mem_7", "Memoria en 1564.", "18 (0x12)."),
        ("wave_mem_8", "Memoria en 1568.", "Pasa de X a 24 en 2455 ns."),
    ]
    stage_d_rows = [
        ("clk", "Reloj de simulación.", "Un ciclo cada 10 ns."),
        ("wave_pc_mem", "PC del acceso elegido en MEM.", "0x120, 0x124, 0x144 y 0x160 en los stores mostrados."),
        ("mem_write", "Habilita la escritura de datos.", "1 en cada store válido."),
        ("mem_address", "Dirección del puerto de datos.", "0x624, 0x628, 0x630 y 0x634 en los stores visibles."),
        ("wave_store_data", "Dato presentado para escritura.", "74, 4, 1 y 1, respectivamente."),
        ("checkpoint_passed", "Bits de etapas comprobadas.", "Pasa de 7 a 15 cerca de 3216 ns: A–D aprobadas."),
        ("wave_x28", "Suma de los seis datos recorridos.", "74 (0x4A)."),
        ("wave_x29", "Cantidad que supera el criterio.", "4."),
        ("wave_x31", "Bandera del camino correcto.", "Pasa a 1 cerca de 3130 ns y permanece 1."),
        ("wave_mem_9", "Memoria en 1572.", "74."),
        ("wave_mem_10", "Memoria en 1576.", "4."),
        ("wave_mem_11", "Memoria en 1580.", "Permanece en 0; el camino D3 no la cambia."),
        ("wave_mem_12", "Memoria en 1584.", "Pasa a 1 cerca de 3135 ns."),
        ("wave_mem_13", "Memoria en 1588.", "Pasa a 1 cerca de 3215 ns."),
    ]
    for j, (title, hint) in enumerate(placeholders):
        if j == 0:
            s += [heading(title),
                  P("La etapa A del programa docente termina con tres stores consecutivos en 1536, 1540 y 1544. En la ventana aproximada de 95–126 ns, el puerto de datos presenta las direcciones 0x600, 0x604 y 0x608 con los valores 11, 5 y 12. El último store corresponde a sw x10, 8(x1), en PC 0x34. Al completarse, x5=11, x6=5 y x10=12; las tres palabras de memoria muestran esos mismos resultados. Cerca de 126 ns, el bit 0 de checkpoint_passed pasa a 1 después de que el testbench compara el estado de todos los registros y posiciones de memoria conocidos para A. Así queda documentado el cierre funcional de la primera etapa.", "EFBody"),
                  Image(str(WAVE_STAGE_A), width=506, height=506*396/1615),
                  P("Figura 3. Captura proporcionada por el equipo: cierre de la etapa A del programa docente en C, aproximadamente 75–220 ns; comprobación principal 95–126 ns.", "EFCaption"),
                  table(("Señal", "Qué representa", "Lectura en la captura"), stage_a_rows,
                        (118, 178, 210)),
                  P("Las celdas de memoria aparecen como X antes de su primera escritura; el testbench confirma sus valores al activar checkpoint_passed.", "EFSmall"),
                  PageBreak()]
            continue
        if j == 1:
            s += [heading(title),
                  P("La etapa B lee los resultados almacenados por A y los combina con cargas, sumas y una resta. Al cierre se observan x11=11, x12=16, x13=5, x14=12, x15=7, x16=7, x17=16 y x18=23. Los stores escriben 7, 16 y 23 en 1548, 1552 y 1556 (0x60C, 0x610 y 0x614); el último es sw x18, 20(x1) en PC 0x60. Cerca de 255 ns la última palabra pasa a 23 y, un nanosegundo después, checkpoint_passed cambia de 1 a 3. Ese cambio ocurre tras la comprobación del testbench de todos los registros y posiciones de memoria esperados para B, conservando aprobada también A.", "EFBody"),
                  Image(str(WAVE_STAGE_B), width=506, height=506*517/1606),
                  P("Figura 4. Captura proporcionada por el equipo: cierre de etapa B del programa docente en C, aproximadamente 160–280 ns; comprobación cerca de 256 ns.", "EFCaption"),
                  table(("Señal", "Qué representa", "Lectura en la captura"), stage_b_rows,
                        (116, 178, 212)),
                  P("Los valores X de memoria antes de cada store indican posiciones aún no escritas en esta simulación. El marcador de aprobación se activa después de verificar el estado final de la etapa.", "EFSmall"),
                  PageBreak()]
            continue
        if j == 2:
            s += [heading(title),
                  P("La etapa C ejecuta tres bucles y deja sus resultados 24, 18 y 24 en las direcciones 1560, 1564 y 1568. En el cierre, x19=12, x20=12, x21=24, x22=18, x24=24 y x26=6. El último store es sw x24, 32(x1) en PC 0xE0: cerca de 2445 ns presenta la dirección 0x620 y el dato 24; la palabra de memoria se actualiza en 2455 ns. Luego, cerca de 2456 ns, checkpoint_passed cambia de 3 a 7 tras la comprobación de registros y memoria por el testbench. En los ciclos siguientes comienza D y reinicia x19 a 0 y x20 a 6; esos cambios posteriores no alteran el estado verificado al cierre de C.", "EFBody"),
                  Image(str(WAVE_STAGE_C), width=506, height=506*469/1611),
                  P("Figura 5. Captura proporcionada por el equipo: cierre de etapa C del programa docente en C, aproximadamente 2380–2530 ns; comprobación cerca de 2456 ns.", "EFCaption"),
                  table(("Señal", "Qué representa", "Lectura en la captura"), stage_c_rows,
                        (118, 178, 210)),
                  P("La línea roja X de wave_mem_8 corresponde al tiempo anterior al último store. El valor del cursor, tomado después del inicio de D, no representa el valor de x19 en el cierre de C.", "EFSmall"),
                  PageBreak()]
            continue
        if j == 3:
            s += [heading(title),
                  P("La etapa D recorre seis datos, acumula x28=74 y cuenta x29=4. Los primeros stores del cierre escriben 74 en 1572 y 4 en 1576, visibles entre 3045 y 3065 ns. La ruta de control evita D3: la posición 1580 permanece en 0, mientras x31 pasa a 1 y se escribe en 1584 cerca de 3135 ns. El store terminal sw x31, 52(x1), en PC 0x160, escribe 1 en 1588 cerca de 3215 ns. Un nanosegundo después checkpoint_passed cambia de 7 a 15, señal de que el testbench comprobó el estado final de todas las etapas A–D. Las tres capturas son tramos consecutivos de una misma simulación.", "EFBody")]
            for path, caption, (image_width, image_height) in zip(WAVE_STAGE_D, (
                "Figura 6a. 3020–3100 ns: stores de x28 y x29; memoria 1572=74 y 1576=4.",
                "Figura 6b. 3100–3175 ns: x31 pasa a 1 y memoria 1584=1; 1580 sigue en 0.",
                "Figura 6c. 3145–3220 ns: store final en 1588 y aprobación de las cuatro etapas.",
            ), ((1596, 433), (1612, 433), (1606, 435))):
                s += [Image(str(path), width=506, height=506*image_height/image_width),
                      P(caption, "EFCaption")]
            s += [PageBreak(), heading("8.4 Cierre de etapa D: señales y comprobación"),
                  table(("Señal", "Qué representa", "Lectura en las tres capturas"),
                        stage_d_rows, (118, 178, 210)),
                  Spacer(1, 11),
                  P("La memoria 1580 fue inicializada a 0 al comenzar D y permanece así. La aprobación final del testbench ocurre después del store terminal; los valores hexadecimales 0x4A y 0x04 equivalen a 74 y 4 en decimal.", "EFSmall"),
                  PageBreak()]
            continue
        if j == 4:
            s += [heading(title),
                  P("En la primera iteración de llenar (aproximadamente 85–140 ns), la vía 0 contiene lw x9, 0(x1) en PC 0x28 y la vía 1 contiene add x4, x4, x9 en PC 0x2C. split_raw=1 impide emitir ambas juntas: issue0=1 e issue1=0. En el ciclo siguiente stall_load=1 detiene temporalmente la suma hasta que el dato cargado está disponible. La ejecución continúa y se observan x9=3 y luego x4=3, tal como exige la primera palabra del arreglo. La captura acredita la separación RAW, la espera Load-Use y el resultado; no muestra directamente los selectores de forwarding.", "EFBody"),
                  Image(str(WAVE_RAW), width=506, height=506*415/1609),
                  P("Figura 7. Captura proporcionada por el equipo: primera iteración del programa propio en C, 0–155 ns. El caso clave se concentra en 85–140 ns.", "EFCaption"),
                  table(("Señal", "Qué representa", "Lectura en la captura"), raw_rows,
                        (92, 185, 229)),
                  P("Los PC de EX y WB son registros de etapa y pueden conservar valores durante burbujas; para demostrar validez en esos ciclos debe añadirse valid_e/valid_w en una captura complementaria. El forwarding tampoco se identifica directamente sin sus selectores.", "EFSmall")]
            if j < len(placeholders)-1:
                s.append(PageBreak())
            continue
        if j == 5:
            s += [heading(title),
                  P("En la primera iteración de llenar, alrededor de 75 ns, ID contiene sw x8, 0(x1) en PC 0x24 y lw x9, 0(x1) en PC 0x28. Ambas instrucciones solicitan el único puerto de memoria de datos; split_resource=1 e issue1=0 obligan a emitir primero la más antigua. Cerca de 95 ns, mem_write=1 escribe el valor 3 en 0x400; la lectura posterior devuelve 3 cerca de 105 ns. En ese momento, add x4, x4, x9 (PC 0x2C) y slt x11, x9, x10 (PC 0x30) pueden emitirse juntas: issue0=issue1=1 y double_issue_count avanza de 4 a 5. La captura muestra serialización del conflicto y recuperación de la doble emisión sin perder el dato.", "EFBody"),
                  Image(str(WAVE_MEM), width=506, height=506*490/1612),
                  P("Figura 8. Captura proporcionada por el equipo: puerto de memoria compartido y doble emisión posterior en C. Ventana 70–205 ns; evento principal 75–115 ns.", "EFCaption"),
                  table(("Señal", "Qué representa", "Lectura en la captura"), memory_rows,
                        (104, 180, 222)),
                  P("El valor X de mem_read fuera de un ciclo de lectura válida no es un resultado del programa. Las señales valid_m distinguen operaciones activas de datos residuales en las etapas.", "EFSmall")]
            if j < len(placeholders)-1:
                s.append(PageBreak())
            continue
        if j == 6:
            s += [heading(title),
                  P("La captura reúne dos resoluciones del branch de retorno del bucle llenar (PC 0x50). Cerca de 190 ns, el BTB todavía no anticipa el destino: predicted_next_pc=0x54, pero EX calcula actual_next_pc=0x20; redirect=1 corrige el PC y el contador de errores aumenta. En la siguiente vuelta, cuando fetch_pc=0x4C, la segunda consulta del BTB corresponde a PC 0x50: btb_hit1=1, predict1=1 y btb_target1=0x20. Al resolver de nuevo ese branch cerca de 310 ns, predicted_next_pc y actual_next_pc coinciden en 0x20; redirect=0. Se ve cómo el predictor aprende el retorno y evita una corrección posterior. Las señales de consulta en IF y las de resolución en EX pertenecen a instrucciones de etapas distintas cuando aparecen en el mismo instante.", "EFBody"),
                  Image(str(WAVE_BTB), width=506, height=506*471/1606),
                  P("Figura 9. Captura proporcionada por el equipo: fallo inicial y acierto posterior del BTB en el programa propio de C, aproximadamente 170–315 ns.", "EFCaption"),
                  table(("Señal", "Qué representa", "Lectura en la captura"), btb_rows,
                        (116, 178, 212)),
                  P("Los contadores son acumulados. La predicción tomada intermedia del JAL en PC 0x3C también contribuye a btb_prediction_count; para evaluar el branch de retorno se comparan sus PC predicho y real cuando control_resolved=1.", "EFSmall")]
            continue
        s += [heading(title),
              P("Evidencia pendiente. Insertar aquí una captura propia legible de la simulación final; el recuadro preserva el espacio y no representa una medición realizada.", "EFNote"),
              WaveSpace(title), Spacer(1,13),
              P(f"<b>Señales y comprobación esperadas:</b> {hint}", "EFSmall"),
              P("<b>Ciclo / PC / instrucciones:</b> _________________________________________________", "EFSmall"),
              P("<b>Valor esperado y observado:</b> _______________________________________________", "EFSmall"),
              P("<b>Interpretación ciclo a ciclo:</b> ______________________________________________", "EFSmall")]
        if j < len(placeholders)-1:
            s.append(PageBreak())

    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    out.seek(0)
    return out.read()


def main():
    body = fitz.open(stream=body_pdf(), filetype="pdf")
    cover = fitz.open(str(SOURCE_COVER))
    final = fitz.open()
    final.insert_pdf(cover, from_page=0, to_page=0)
    first = final[0]
    # Retain the E2 cover's logo, team table, spacing and typography. The team
    # asked to update only the title and remove the obsolete E2 date line.
    old_title = first.search_for("INFORME TÉCNICO DE LA SEGUNDA ENTREGA")
    old_date = first.search_for("FECHA DE ENTREGA:")
    old_value = first.search_for("09/11/2026")
    if len(old_title) != 1 or len(old_date) != 1 or len(old_value) != 1:
        raise ValueError("The source cover changed; cannot safely edit it")
    first.add_redact_annot(fitz.Rect(95, 347, 502, 370), fill=(1, 1, 1))
    first.add_redact_annot(fitz.Rect(49, 468, 224, 484), fill=(1, 1, 1))
    first.apply_redactions(images=0, graphics=0)
    first.insert_font(fontname="arialbold", fontfile=r"C:\Windows\Fonts\arialbd.ttf")
    title = "INFORME TÉCNICO DE LA ENTREGA FINAL"
    title_font = fitz.Font(fontfile=r"C:\Windows\Fonts\arialbd.ttf")
    title_x = (first.rect.width - title_font.text_length(title, fontsize=17)) / 2
    first.insert_text((title_x, 365.0814), title, fontsize=17,
                      fontname="arialbold", color=(0, 0, 0))
    final.insert_pdf(body)
    final.set_metadata({"title": "Informe técnico de entrega final - BTB",
                        "author": "Equipo Proyecto 2 Arquitectura de Computadoras",
                        "subject": "Tres arquitecturas RV32I, programas docente y propio, optimización BTB"})
    final.save(str(OUTPUT), garbage=4, deflate=True)
    print(f"Wrote {OUTPUT} ({len(final)} pages)")


if __name__ == "__main__":
    main()
