"""Build an editable Word/Google Docs version of the final report.

The PDF remains the visual reference. This DOCX keeps body text, tables and
waveform spaces editable so the team can add its own captures in Docs.
"""
from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOGO = ROOT / "E2" / "informe" / "assets" / "logo_utec_e1.png"
DATAPATH = HERE / "datapath_e2_refinado.png"
WAVE_RAW = ROOT / "EF" / "resultados" / "waveforms" / "captura_01_raw_load_use.png"
WAVE_MEM = ROOT / "EF" / "resultados" / "waveforms" / "captura_02_memoria_emision.png"
WAVE_BTB = ROOT / "EF" / "resultados" / "waveforms" / "captura_03_btb.png"
WAVE_STAGE_A = ROOT / "EF" / "resultados" / "waveforms" / "captura_04_docente_etapa_A.png"
WAVE_STAGE_B = ROOT / "EF" / "resultados" / "waveforms" / "captura_05_docente_etapa_B.png"
WAVE_STAGE_C = ROOT / "EF" / "resultados" / "waveforms" / "captura_06_docente_etapa_C.png"
WAVE_STAGE_D = [
    ROOT / "EF" / "resultados" / "waveforms" / f"captura_07{part}_docente_etapa_D.png"
    for part in "abc"
]
OUTPUT = ROOT / "tmp" / "informe_final_raw.docx"

NAVY = RGBColor(23, 50, 77)
BLUE = RGBColor(21, 153, 199)
PALE = "EDF5F8"
GREY = "D9D9D9"


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_borders(cell, color=GREY, size="5"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = tcPr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tcPr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        el = borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), size)
        el.set(qn("w:color"), color)


def text_in_cell(cell, value, bold=False, color=None, size=8):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    r = p.add_run(str(value))
    r.bold = bold
    r.font.name = "Arial"
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for j, h in enumerate(headers):
        cell = t.rows[0].cells[j]
        text_in_cell(cell, h, bold=True, color=RGBColor(255, 255, 255), size=8)
        shade(cell, "17324D")
        set_borders(cell)
        if widths:
            cell.width = Inches(widths[j])
    for i, row in enumerate(rows):
        cells = t.add_row().cells
        for j, value in enumerate(row):
            text_in_cell(cells[j], value, size=8)
            if widths:
                cells[j].width = Inches(widths[j])
            shade(cells[j], "F4F7F9" if i % 2 else "FFFFFF")
            set_borders(cells[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def add_p(doc, text, style=None):
    p = doc.add_paragraph(style=style)
    p.add_run(text)
    return p


def add_h(doc, text, level=1):
    return doc.add_paragraph(text, style=f"Heading {level}")


def page_break(doc):
    doc.add_page_break()


def add_wave_page(doc, title, signals):
    page_break(doc)
    add_h(doc, title, 1)
    add_p(doc, "Insertar aquí una waveform propia de la simulación final. La captura debe mostrar ciclos, PC, instrucciones y las señales indicadas.")
    t = doc.add_table(rows=1, cols=1)
    t.autofit = False
    t.columns[0].width = Inches(6.75)
    t.rows[0].height = Inches(4.25)
    t.rows[0].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
    cell = t.cell(0, 0)
    cell.width = Inches(6.75)
    set_borders(cell, color="9AAEBA", size="7")
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ESPACIO PARA INSERTAR WAVEFORM")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(95, 111, 122)
    add_p(doc, f"Señales y comprobación: {signals}")
    add_p(doc, "Ciclo, PC e instrucciones: ______________________________________________")
    add_p(doc, "Valor esperado y observado: __________________________________________")
    add_p(doc, "Interpretación ciclo a ciclo: __________________________________________")


def add_raw_wave_page(doc):
    page_break(doc)
    add_h(doc, "8.5 Caso clave RAW y Load Use", 1)
    add_p(doc, "En la primera iteración de llenar (aproximadamente 85–140 ns), la vía 0 contiene lw x9, 0(x1) en PC 0x28 y la vía 1 contiene add x4, x4, x9 en PC 0x2C. split_raw=1 impide emitir ambas juntas: issue0=1 e issue1=0. En el ciclo siguiente stall_load=1 detiene temporalmente la suma hasta que el dato cargado está disponible. La ejecución continúa y se observan x9=3 y luego x4=3, tal como exige la primera palabra del arreglo. La captura acredita la separación RAW, la espera Load-Use y el resultado; no muestra directamente los selectores de forwarding.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(WAVE_RAW), width=Inches(6.75))
    add_p(doc, "Figura 3. Captura proporcionada por el equipo: primera iteración del programa propio en C, 0–155 ns. El caso clave se concentra en 85–140 ns.")
    rows = [
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
    add_table(doc, ("Señal", "Qué representa", "Lectura en la captura"), rows,
              widths=(1.15, 2.45, 3.15))
    add_p(doc, "Los PC de EX y WB son registros de etapa y pueden conservar valores durante burbujas; para demostrar validez en esos ciclos debe añadirse valid_e/valid_w en una captura complementaria. El forwarding tampoco se identifica directamente sin sus selectores.")


def add_memory_wave_page(doc):
    page_break(doc)
    add_h(doc, "8.6 Conflicto de memoria y doble emisión", 1)
    add_p(doc, "En la primera iteración de llenar, alrededor de 75 ns, ID contiene sw x8, 0(x1) en PC 0x24 y lw x9, 0(x1) en PC 0x28. Ambas instrucciones solicitan el único puerto de memoria de datos; split_resource=1 e issue1=0 obligan a emitir primero la más antigua. Cerca de 95 ns, mem_write=1 escribe el valor 3 en 0x400; la lectura posterior devuelve 3 cerca de 105 ns. En ese momento, add x4, x4, x9 (PC 0x2C) y slt x11, x9, x10 (PC 0x30) pueden emitirse juntas: issue0=issue1=1 y double_issue_count avanza de 4 a 5. La captura muestra serialización del conflicto y recuperación de la doble emisión sin perder el dato.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(WAVE_MEM), width=Inches(6.75))
    add_p(doc, "Figura 4. Captura proporcionada por el equipo: puerto de memoria compartido y doble emisión posterior en C. Ventana 70–205 ns; evento principal 75–115 ns.")
    rows = [
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
    add_table(doc, ("Señal", "Qué representa", "Lectura en la captura"), rows,
              widths=(1.25, 2.35, 3.15))
    add_p(doc, "El valor X de mem_read fuera de un ciclo de lectura válida no es un resultado del programa. Las señales valid_m distinguen operaciones activas de datos residuales en las etapas.")


def add_btb_wave_page(doc):
    page_break(doc)
    add_h(doc, "8.7 BTB predicción y corrección", 1)
    add_p(doc, "La captura reúne dos resoluciones del branch de retorno del bucle llenar (PC 0x50). Cerca de 190 ns, el BTB todavía no anticipa el destino: predicted_next_pc=0x54, pero EX calcula actual_next_pc=0x20; redirect=1 corrige el PC y el contador de errores aumenta. En la siguiente vuelta, cuando fetch_pc=0x4C, la segunda consulta del BTB corresponde a PC 0x50: btb_hit1=1, predict1=1 y btb_target1=0x20. Al resolver de nuevo ese branch cerca de 310 ns, predicted_next_pc y actual_next_pc coinciden en 0x20; redirect=0. Se ve cómo el predictor aprende el retorno y evita una corrección posterior. Las señales de consulta en IF y las de resolución en EX pertenecen a instrucciones de etapas distintas cuando aparecen en el mismo instante.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(WAVE_BTB), width=Inches(6.75))
    add_p(doc, "Figura 5. Captura proporcionada por el equipo: fallo inicial y acierto posterior del BTB en el programa propio de C, aproximadamente 170–315 ns.")
    rows = [
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
    add_table(doc, ("Señal", "Qué representa", "Lectura en la captura"), rows,
              widths=(1.45, 2.3, 3.0))
    add_p(doc, "Los contadores son acumulados. La predicción tomada intermedia del JAL en PC 0x3C también contribuye a btb_prediction_count; para evaluar el branch de retorno se comparan sus PC predicho y real cuando control_resolved=1.")


def add_stage_a_wave_page(doc):
    page_break(doc)
    add_h(doc, "8.1 Cierre de etapa A del docente", 1)
    add_p(doc, "La etapa A del programa docente termina con tres stores consecutivos en 1536, 1540 y 1544. En la ventana aproximada de 95–126 ns, el puerto de datos presenta las direcciones 0x600, 0x604 y 0x608 con los valores 11, 5 y 12. El último store corresponde a sw x10, 8(x1), en PC 0x34. Al completarse, x5=11, x6=5 y x10=12; las tres palabras de memoria muestran esos mismos resultados. Cerca de 126 ns, el bit 0 de checkpoint_passed pasa a 1 después de que el testbench compara el estado de todos los registros y posiciones de memoria conocidos para A. Así queda documentado el cierre funcional de la primera etapa.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(WAVE_STAGE_A), width=Inches(6.75))
    add_p(doc, "Figura 3. Captura proporcionada por el equipo: cierre de la etapa A del programa docente en C, aproximadamente 75–220 ns; comprobación principal 95–126 ns.")
    rows = [
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
    add_table(doc, ("Señal", "Qué representa", "Lectura en la captura"), rows,
              widths=(1.55, 2.3, 2.9))
    add_p(doc, "Las celdas de memoria aparecen como X antes de su primera escritura; el testbench confirma sus valores al activar checkpoint_passed.")


def add_stage_b_wave_page(doc):
    page_break(doc)
    add_h(doc, "8.2 Cierre de etapa B del docente", 1)
    add_p(doc, "La etapa B lee los resultados almacenados por A y los combina con cargas, sumas y una resta. Al cierre se observan x11=11, x12=16, x13=5, x14=12, x15=7, x16=7, x17=16 y x18=23. Los stores escriben 7, 16 y 23 en 1548, 1552 y 1556 (0x60C, 0x610 y 0x614); el último es sw x18, 20(x1) en PC 0x60. Cerca de 255 ns la última palabra pasa a 23 y, un nanosegundo después, checkpoint_passed cambia de 1 a 3. Ese cambio ocurre tras la comprobación del testbench de todos los registros y posiciones de memoria esperados para B, conservando aprobada también A.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(WAVE_STAGE_B), width=Inches(6.75))
    add_p(doc, "Figura 4. Captura proporcionada por el equipo: cierre de etapa B del programa docente en C, aproximadamente 160–280 ns; comprobación cerca de 256 ns.")
    rows = [
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
    add_table(doc, ("Señal", "Qué representa", "Lectura en la captura"), rows,
              widths=(1.55, 2.25, 2.95))
    add_p(doc, "Los valores X de memoria antes de cada store indican posiciones aún no escritas en esta simulación. El marcador de aprobación se activa después de verificar el estado final de la etapa.")


def add_stage_c_wave_page(doc):
    page_break(doc)
    add_h(doc, "8.3 Cierre de etapa C del docente", 1)
    add_p(doc, "La etapa C ejecuta tres bucles y deja sus resultados 24, 18 y 24 en las direcciones 1560, 1564 y 1568. En el cierre, x19=12, x20=12, x21=24, x22=18, x24=24 y x26=6. El último store es sw x24, 32(x1) en PC 0xE0: cerca de 2445 ns presenta la dirección 0x620 y el dato 24; la palabra de memoria se actualiza en 2455 ns. Luego, cerca de 2456 ns, checkpoint_passed cambia de 3 a 7 tras la comprobación de registros y memoria por el testbench. En los ciclos siguientes comienza D y reinicia x19 a 0 y x20 a 6; esos cambios posteriores no alteran el estado verificado al cierre de C.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(WAVE_STAGE_C), width=Inches(6.75))
    add_p(doc, "Figura 5. Captura proporcionada por el equipo: cierre de etapa C del programa docente en C, aproximadamente 2380–2530 ns; comprobación cerca de 2456 ns.")
    rows = [
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
    add_table(doc, ("Señal", "Qué representa", "Lectura en la captura"), rows,
              widths=(1.55, 2.25, 2.95))
    add_p(doc, "La línea roja X de wave_mem_8 corresponde al tiempo anterior al último store. El valor del cursor, tomado después del inicio de D, no representa el valor de x19 en el cierre de C.")


def add_stage_d_wave_page(doc):
    page_break(doc)
    add_h(doc, "8.4 Cierre de etapa D del docente", 1)
    add_p(doc, "La etapa D recorre seis datos, acumula x28=74 y cuenta x29=4. Los primeros stores del cierre escriben 74 en 1572 y 4 en 1576, visibles entre 3045 y 3065 ns. La ruta de control evita D3: la posición 1580 permanece en 0, mientras x31 pasa a 1 y se escribe en 1584 cerca de 3135 ns. El store terminal sw x31, 52(x1), en PC 0x160, escribe 1 en 1588 cerca de 3215 ns. Un nanosegundo después checkpoint_passed cambia de 7 a 15, señal de que el testbench comprobó el estado final de todas las etapas A–D. Las tres capturas son tramos consecutivos de una misma simulación.")
    captions = (
        "Figura 6a. 3020–3100 ns: stores de x28 y x29; memoria 1572=74 y 1576=4.",
        "Figura 6b. 3100–3175 ns: x31 pasa a 1 y memoria 1584=1; 1580 sigue en 0.",
        "Figura 6c. 3145–3220 ns: store final en 1588 y aprobación de las cuatro etapas.",
    )
    for path, caption in zip(WAVE_STAGE_D, captions):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path), width=Inches(6.75))
        add_p(doc, caption)
    page_break(doc)
    add_h(doc, "8.4 Cierre de etapa D: señales y comprobación", 1)
    rows = [
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
    add_table(doc, ("Señal", "Qué representa", "Lectura en las tres capturas"),
              rows, widths=(1.55, 2.25, 2.95))
    add_p(doc, "La memoria 1580 fue inicializada a 0 al comenzar D y permanece así. La aprobación final del testbench ocurre después del store terminal; los valores hexadecimales 0x4A y 0x04 equivalen a 74 y 4 en decimal.")


def main():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(0.65)
    sec.bottom_margin = Inches(0.62)
    sec.left_margin = Inches(0.72)
    sec.right_margin = Inches(0.72)
    sec.different_first_page_header_footer = True
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    title_style = doc.styles["Title"]
    title_style.font.name = "Arial"
    title_style.font.size = Pt(17)
    title_style.font.bold = True
    title_style.font.color.rgb = RGBColor(0, 0, 0)
    title_style.paragraph_format.space_after = Pt(4)
    for name, size, before, after in (("Heading 1", 12, 12, 5), ("Heading 2", 10, 9, 4)):
        st = doc.styles[name]
        st.font.name = "Arial"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True

    # Cover follows the E2 layout while applying the team's later instruction:
    # final-delivery title and no obsolete E2 date.
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    p.add_run().add_picture(str(LOGO), width=Inches(2.5))
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.add_run("INFORME TÉCNICO DE LA ENTREGA FINAL")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Procesador RISC-V segmentado y arquitectura Dual Issue funcional")
    r.bold = True
    r.font.size = Pt(10)
    p.paragraph_format.space_after = Pt(20)
    for lead, value in (("ASIGNATURA", "Arquitectura de Computadoras (CS3051)-Teo. 1-Lab. 11-2026-2"),
                        ("DOCENTE", "Williams Valencia, Carlos Eduardo")):
        p = doc.add_paragraph()
        r = p.add_run(f"{lead}: "); r.bold = True
        p.add_run(value)
        p.paragraph_format.space_after = Pt(10)
    p = doc.add_paragraph()
    r = p.add_run("INTEGRANTES:"); r.bold = True
    add_table(doc, ["INTEGRANTES", "CÓDIGO"], [
        ["Ladron de Guevara Aguirre, Diego Abraham", "202410083"],
        ["Burgos Ochoa, Jeseph Imanol", "202510395"],
        ["Morales Portella Santiago Cesar", "202510403"],
        ["Heredia Cadenas, Guillermo Arturo", "202410219"],
    ], [4.3, 2.2])
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(65)
    p.add_run("Lima, Perú\n2026")

    page_break(doc)
    doc.add_paragraph("Informe técnico de la entrega final", style="Title")
    add_p(doc, "Procesadores A, B y C con optimización Branch Target Buffer")
    add_h(doc, "1. Resumen y alcance")
    add_p(doc, "Se comparan tres procesadores RV32I de cinco etapas: A, pipeline Single-Issue; B, Dual-Issue In-Order con dos vías y recursos de memoria y branch compartidos; y C, copia de B con Branch Target Buffer (BTB). Los dos programas de evaluación —uno del docente y uno propio— se ejecutan sin cambiar el Assembly entre versiones. En las seis corridas se verificó el estado funcional y se midieron instrucciones retiradas, ciclos, IPC, CPI y speedup.")
    add_p(doc, "El BTB se incorporó a la ruta de búsqueda y control de B. Las ALU, la Issue Unit, el forwarding y los recursos compartidos de E2 permanecen. La memoria de datos se amplió de 256 a 512 palabras en A/B/C por igual para admitir la base 1536 del programa docente; este ajuste no se atribuye a la optimización.")
    add_table(doc, ["Configuración", "Arquitectura"], [
        ["A", "Pipeline Single-Issue de cinco etapas."],
        ["B", "Dual-Issue In-Order con recursos de memoria y branch compartidos."],
        ["C", "B con BTB aprobado verbalmente por el docente en clase."],
    ], [1.0, 5.5])
    add_p(doc, "Fuentes: enunciado y rúbrica del Proyecto 2; programa de prueba del docente. Las cifras se reproducen con el código y testbenches incluidos en EF/.")

    page_break(doc)
    add_h(doc, "2. Arquitectura y cambio de C")
    add_p(doc, "B obtiene hasta dos instrucciones en IF, las mantiene en una pareja ordenada en ID y emite cero, una o dos según dependencias y conflictos. Conserva dos ALU y un solo puerto de datos y recurso de branch. C conserva este datapath y añade una consulta anticipada del destino al lado de IF.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(DATAPATH), width=Inches(6.65))
    add_p(doc, "Figura 1. Datapath B de E2 reutilizado como base de C.")
    add_table(doc, ["IF", "BTB", "MUX de PC", "ID y EX"], [[
        "Consulta PC y PC+4", "16 entradas, dos lecturas", "Elige destino o secuencia", "Comprueba PC real y actualiza BTB"
    ]], [1.35, 1.45, 1.55, 2.15])
    add_p(doc, "Figura 2. Adición funcional al frente de B: consulta en IF y actualización desde la unidad de branch en EX; el metadato de PC predicho viaja por IF/ID e ID/EX.")
    add_h(doc, "2.1 Tabla y política", 2)
    add_p(doc, "El BTB tiene 16 entradas de mapeo directo. Usa PC[5:2] como índice y compara una etiqueta de PC completa; cada entrada guarda valid, destino de 32 bits y contador saturante de dos bits. Dos lecturas combinacionales atienden PC y PC+4. Un salto tomado instala o refuerza la predicción; uno no tomado debilita su contador. JAL y JALR se instalan como fuertemente tomados. El almacenamiento lógico es 1072 bits, sin contar multiplexores y comparadores.")

    page_break(doc)
    add_h(doc, "3. Predicción, resolución y corrección")
    add_table(doc, ["Momento", "Acción en C"], [
        ["IF", "Consulta dos PC. Si la primera instrucción predice salto tomado, guarda solo la antigua y usa el destino en el siguiente fetch. Si predice la segunda, guarda el par y cambia el siguiente fetch."],
        ["ID", "Guarda el PC siguiente predicho con cada instrucción. Conserva ese metadato al reagrupar. No empareja un control predicho tomado con su destino antes de resolverlo."],
        ["EX", "Compara el PC real con el predicho. Si difieren, redirige y anula solo instrucciones jóvenes. Si coinciden, no hace flush. Actualiza el BTB."],
    ], [0.9, 5.6])
    add_h(doc, "3.1 Corrección y prioridades", 2)
    add_p(doc, "La predicción solo modifica el camino especulativo. El resultado arquitectónico depende del branch resuelto en EX. Un control en vía 0 puede anular su compañera joven cuando se corrige la predicción; un control en vía 1 conserva la vía 0. Los bits valid impiden que instrucciones anuladas escriban memoria o registros. Se mantiene una actualización de BTB por instrucción de control válida.")
    add_h(doc, "3.2 Validación específica", 2)
    add_p(doc, "La prueba unitaria cubre miss frío, instalación de destino, decremento y recuperación del contador, lectura de ambas posiciones y colisión de índice con etiqueta diferente. La regresión de C pasa cuatro casos E2 y cinco comparaciones E1. Los testbenches de ambos programas finales comprueban resultados y terminan por éxito o error explícito.")
    add_h(doc, "4. Programas de evaluación")
    add_h(doc, "4.1 Programa del docente", 2)
    add_p(doc, "Se transcribieron las 90 instrucciones del PDF y se contrastó su secuencia. Utiliza x1=1536 y las etapas A–D; sus estados se comprueban en los stores de cierre. El testbench verifica los 32 registros y las posiciones de memoria esperadas. A/B/C retiran 312 instrucciones dinámicas antes de fin y producen el mismo estado final.")
    add_h(doc, "4.2 Programa propio", 2)
    add_p(doc, "Genera 12 palabras con valores 3…14 desde la dirección 1024 y las recorre dos veces. Combina store seguido de load, Load-Use, suma, conteo por umbral, hash recurrente, branches condicionales y bucles de retorno. Tiene 45 instrucciones estáticas y 268 retiradas dinámicas antes de fin.")
    add_table(doc, ["Dirección", "Resultado", "Valor"], [
        ["1200", "Suma durante generación", "102"], ["1204", "Suma durante lectura", "102"],
        ["1208 / 1212", "Conteos menores / mayores o iguales a 9", "6 / 6"],
        ["1216", "Hash h = 2h + dato", "16368"], ["1220 / 1224", "Suma de índices / marcador", "66 / 1"],
    ], [1.15, 4.45, 0.9])

    page_break(doc)
    add_h(doc, "5. Método y comparación cuantitativa")
    add_p(doc, "Para cada programa se usa el mismo .mem, registros iniciales en cero, reloj y criterio de cierre en A/B/C. Los ciclos se cuentan al liberar reset y se cierran con el store terminal. Las retiradas se cuentan solo para PC anteriores a fin; su bucle infinito no entra en las cifras. IPC = retiradas/ciclos; CPI = ciclos/retiradas; speedup = ciclos de referencia/ciclos de configuración, suponiendo igual período de reloj.")
    add_table(doc, ["Prog.", "Conf.", "Ret.", "Ciclos", "IPC", "CPI", "vs A", "vs B"], [
        ["Docente", "A", 312, 458, "0.6812", "1.4679", "1.0000", "0.8428"],
        ["Docente", "B", 312, 386, "0.8083", "1.2372", "1.1865", "1.0000"],
        ["Docente", "C", 312, 320, "0.9750", "1.0256", "1.4313", "1.2063"],
        ["Propio", "A", 268, 363, "0.7383", "1.3545", "1.0000", "0.7934"],
        ["Propio", "B", 268, 288, "0.9306", "1.0746", "1.2604", "1.0000"],
        ["Propio", "C", 268, 233, "1.1502", "0.8694", "1.5579", "1.2361"],
    ], [0.9, 0.55, 0.55, 0.78, 0.75, 0.75, 1.1, 1.1])
    add_p(doc, "Tabla 1. Seis corridas con igualdad funcional. La columna vs B para A expresa ciclos_B/ciclos_A.")
    add_h(doc, "5.1 Señales de actividad y BTB", 2)
    add_table(doc, ["Prog.", "Conf.", "Doble", "Stalls", "Parcial", "BTB tomado", "Correctas / correcciones"], [
        ["Docente", "B", 140, 11, 99, "—", "—"],
        ["Docente", "C", 85, 11, 152, 63, "57 / 32"],
        ["Propio", "B", 110, 24, 83, "—", "—"],
        ["Propio", "C", 79, 24, 105, 32, "36 / 6"],
    ], [0.85, 0.55, 0.62, 0.62, 0.72, 0.88, 2.26])
    add_p(doc, "Tabla 2. Las decisiones correctas incluyen continuaciones secuenciales; las métricas de control filtran PC < fin. Los contadores de doble emisión y emisión parcial se observan al cierre del store terminal.")

    page_break(doc)
    add_h(doc, "6. Interpretación de resultados")
    add_p(doc, "B reduce ciclos frente a A en el programa docente (458 a 386) y en el propio (363 a 288), porque puede emitir dos instrucciones independientes. No llega al IPC ideal de 2: RAW dentro de la pareja, Load-Use, un único puerto de memoria, branches y emisiones parciales limitan la ocupación. El propio exhibe 24 stalls Load-Use en B y C; el docente, 11.")
    add_p(doc, "C baja de 386 a 320 ciclos en el docente (speedup 1.2063 frente a B) y de 288 a 233 en el propio (1.2361). En los bucles repetidos, el BTB anticipa destinos tomados y evita parte del vaciado tardío del camino secuencial. Excluyendo fin, el docente registra 63 predicciones de tomado, 57 decisiones correctas y 32 correcciones; el propio, 32, 36 y 6.")
    add_p(doc, "C muestra menos ciclos de doble emisión que B (85 frente a 140 en el docente; 79 frente a 110 en el propio) y más emisiones parciales. La regla que evita emparejar un control predicho tomado con su destino consume oportunidades de issue. Aun así, el menor costo de los cambios de flujo predomina en estos dos programas. Los stalls Load-Use no cambian, coherente con una optimización de control.")
    add_h(doc, "7. Límites y reproducción")
    add_p(doc, "El BTB es de mapeo directo: dos PC con igual índice compiten por una entrada. Un branch alternante o un destino JALR cambiante pueden degradar la predicción. No se ha sintetizado ni medido frecuencia máxima; por tanto, los speedups reportados son de ciclos y presuponen el mismo período de reloj. El docente aprobó verbalmente la elección de BTB durante la clase, según comunicación del equipo.")
    add_p(doc, "Para reproducir desde EF/ en PowerShell con Python e Icarus Verilog: ./run_code_checks.ps1. El script ensambla ambos programas y ejecuta A, B y C, la prueba unitaria del BTB y la regresión E2/E1 de C. Fuentes: programas/propio.S, programas/docente.S, testbenches/, resultados/comparacion_codigo.md y BTB_DOCUMENTACION.md.")

    add_stage_a_wave_page(doc)
    add_stage_b_wave_page(doc)
    add_stage_c_wave_page(doc)
    add_stage_d_wave_page(doc)
    add_raw_wave_page(doc)
    add_memory_wave_page(doc)
    add_btb_wave_page(doc)

    doc.core_properties.title = "Informe técnico de la entrega final"
    doc.core_properties.subject = "Comparación de tres procesadores RV32I con BTB"
    doc.core_properties.author = "Equipo Proyecto 2 Arquitectura de Computadoras"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
