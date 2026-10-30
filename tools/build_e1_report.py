"""Create a draft E1 PDF from the VCDs produced by run_e1.ps1."""
from bisect import bisect_right
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from vcdvcd import VCDVCD
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
)

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "pdfs"
OUT = ROOT / "output" / "pdf"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2C6589")
PALE = colors.HexColor("#EAF2F6")
GREY = colors.HexColor("#53636F")


def value_at(vcd, signal, tick):
    tv = vcd[signal].tv
    times = [t for t, _ in tv]
    pos = bisect_right(times, tick) - 1
    if pos < 0:
        return 0
    bits = tv[pos][1]
    if any(c in bits.lower() for c in "xz"):
        return 0
    return int(bits, 2)


def waveform(vcd_file, filename, rows, first, last):
    vcd = VCDVCD(str(ROOT / "tests" / vcd_file))
    cycles = list(range(first, last + 1))
    ticks = [26000 + (n - 1) * 10000 for n in cycles]
    fig, axes = plt.subplots(len(rows), 1, figsize=(9.5, 3.0), sharex=True,
                             constrained_layout=True)
    if len(rows) == 1:
        axes = [axes]
    palette = ["#24658A", "#B66036", "#438A65", "#8055A0"]
    for ax, (label, signals) in zip(axes, rows):
        for j, signal in enumerate(signals):
            values = [value_at(vcd, signal, tick) for tick in ticks]
            ax.step(cycles, values, where="mid", linewidth=1.9,
                    color=palette[j % len(palette)], label=f"vía {j}" if len(signals) > 1 else None)
            ax.plot(cycles, values, ".", color=palette[j % len(palette)], markersize=3)
        ax.set_ylabel(label, rotation=0, ha="right", va="center", fontsize=8, labelpad=16)
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(axis="x", alpha=0.22)
        if len(signals) > 1:
            ax.legend(loc="upper left", fontsize=6, ncol=2, frameon=False)
    axes[-1].set_xlabel("Ciclo desde reset", fontsize=8)
    axes[-1].set_xticks(cycles)
    axes[-1].tick_params(axis="x", labelsize=7)
    fig.patch.set_facecolor("white")
    path = TMP / filename
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


DP = "testbench.dut.rvpipelined.dp."
P1 = waveform("e1_1.vcd", "p1.png", [
    ("PC", [DP + "PC_F[31:0]"]),
    ("Valid M", [DP + "Valid_M"]),
    ("Write", ["testbench.MemWrite"]),
], 60, 72)
P2 = waveform("e1_2.vcd", "p2.png", [
    ("PC", [DP + "PC_F[31:0]"]),
    ("Fwd A", [DP + "ForwardAE[1:0]"]),
    ("Fwd B", [DP + "ForwardBE[1:0]"]),
    ("Write", ["testbench.MemWrite"]),
], 1, 11)
P3 = waveform("e1_3.vcd", "p3.png", [
    ("PC", [DP + "PC_F[31:0]"]),
    ("Stall", [DP + "Stall_D"]),
    ("Valid EX", [DP + "Valid_E"]),
    ("Fwd A", [DP + "ForwardAE[1:0]"]),
], 1, 9)
P4 = waveform("e1_4.vcd", "p4.png", [
    ("PC", [DP + "PC_F[31:0]"]),
    ("Redirect", [DP + "PCSrc_E"]),
    ("Valid ID", [DP + "Valid_D"]),
    ("Write", ["testbench.MemWrite"]),
], 1, 13)
DUAL = waveform("e1_dual.vcd", "dual.png", [
    ("PC fetch", ["dual_prelim_tb.pc0f[31:0]", "dual_prelim_tb.pc1f[31:0]"]),
    ("ALU EX", ["dual_prelim_tb.result0[31:0]", "dual_prelim_tb.result1[31:0]"]),
    ("Valid EX", ["dual_prelim_tb.valid0", "dual_prelim_tb.valid1"]),
], 1, 5)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"],
    fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=NAVY, spaceAfter=13))
styles.add(ParagraphStyle(name="ReportHeading", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=NAVY,
    spaceBefore=13, spaceAfter=7))
styles.add(ParagraphStyle(name="ReportBody", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=9.4, leading=14, spaceAfter=8))
styles.add(ParagraphStyle(name="ReportSmall", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=8.1, leading=11, spaceAfter=5))
styles.add(ParagraphStyle(name="ReportCaption", parent=styles["BodyText"],
    fontName="Helvetica-Oblique", fontSize=8, leading=11,
    textColor=GREY, spaceAfter=10))
styles.add(ParagraphStyle(name="ReportCentered", parent=styles["BodyText"],
    alignment=TA_CENTER, fontSize=8.5, leading=12))


def p(text, style="ReportBody"):
    return Paragraph(text, styles[style])


def heading(text):
    return p(text, "ReportHeading")


def img(path, width=177 * mm):
    from PIL import Image as PILImage
    with PILImage.open(path) as pic:
        w, h = pic.size
    return Image(str(path), width=width, height=width * h / w)


def table(data, widths, header=True):
    converted = [[p(str(cell), "ReportSmall") for cell in row] for row in data]
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0,
              hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, colors.HexColor("#CAD7DF")),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), PALE),
            ("LINEBELOW", (0, 0), (-1, 0), 1, BLUE),
        ])
    t.setStyle(TableStyle(commands))
    return t


story = []
story += [p("Proyecto 2 | Entrega 1", "ReportTitle"),
          p("Pipeline RV32I Single-Issue y comienzo Dual-Issue", "ReportHeading"),
          p("Informe técnico preliminar generado a partir del código y de las simulaciones de E1. "
            "Los integrantes, curso y fecha de entrega deben completarse antes de presentar."),
          table([
              ["Versión", "Estado verificado"],
              ["A - Single-Issue", "Cinco etapas, forwarding MEM/WB, stall Load-Use y flush de branch/jump. Cuatro programas dirigidos pasan."],
              ["B - preliminar E1", "Dual Fetch, Dual Decode, dos registros de vía en ID/EX y dos ALU con pares independientes. No es B funcional de E2."],
          ], [41 * mm, 136 * mm]),
          heading("Arquitectura implementada en A"),
          table([["IF", "ID", "EX", "MEM", "WB"],
                 ["PC + 4; fetch", "Decode; RF; hazard", "ALU; branch; forwarding", "Memoria de datos", "Resultado; escritura RF"]],
                [35.4 * mm] * 5),
          Spacer(1, 6 * mm),
          p("<b>Ruta de hazards.</b> La unidad compara fuentes de ID y EX con destinos de EX/MEM/WB. "
            "MEM tiene prioridad sobre WB cuando hay dos productores del mismo registro. Un load en EX "
            "que alimenta ID retiene PC e IF/ID e inserta una burbuja en ID/EX. Los branches se resuelven "
            "en EX; si se toman, el PC se redirige y se anulan las instrucciones jóvenes de IF e ID."),
          p("<b>Corrección de efectos.</b> `MemWrite` se propaga a MEM con la dirección y el dato del store. "
            "Los bits Valid de cada etapa impiden que una burbuja o una instrucción anulada escriban "
            "registro o memoria. El dato de un store también puede llegar por forwarding."),
          PageBreak()]

story += [heading("Programas de verificación funcional"),
          table([
              ["Caso", "Estímulo y observación decisiva", "Resultado"],
              ["P1 - ISA sin hazards", "R/I, lw y sw separados por NOP; verifica valores de x3-x16 y memoria.", "PASS; 72 ciclos; 0 stalls"],
              ["P2 - Forwarding", "RAW seguidas, mismo destino y dato reenviado a store.", "PASS; 11 ciclos; 6 ciclos con forwarding"],
              ["P3 - Stalling", "lw seguido inmediatamente por add consumidor.", "PASS; 9 ciclos; 1 stall"],
              ["P4 - Flushing", "beq tomado y no tomado; jal; stores erróneos a 104.", "PASS; 13 ciclos; 2 redirecciones; 0 stores erróneos"],
          ], [35 * mm, 92 * mm, 50 * mm]),
          heading("P1 - ISA sin dependencias que requieran Hazard Unit"),
          p("El programa separa productores y consumidores con tres NOP. Se comprueban addi, add, sub, "
            "slt, and, or, sll, srl, slti, andi, ori, slli, srli, lw y sw. Los valores finales clave "
            "son x3=25, x4=5, x8=1024, x9=512, x10=10, x11=25 y memoria[100]=25."),
          img(P1),
          p("Últimos ciclos de P1. PC avanza sin retención, las instrucciones válidas llegan a MEM y "
            "el store final se activa una sola vez. No se observó Stall_D.", "ReportCaption"),
          p("Las mediciones de ciclos de esta página terminan en el store de éxito. Todavía no son "
            "la comparación de rendimiento A/B/C exigida para EF.", "ReportSmall"),
          PageBreak()]

story += [heading("P2 - Forwarding entre etapas"), img(P2),
          p("ForwardAE/BE toman 2 cuando el productor está en MEM y 1 cuando está en WB. "
            "La cadena de x4 da 1, luego 3; el consumidor obtiene el valor más reciente. "
            "x5 termina en 25 y el store final escribe 25 en dirección 100. No hubo stalls.",
            "ReportCaption"),
          heading("P3 - Load-Use y burbuja"), img(P3),
          p("Stall_D se activa un ciclo cuando el lw está en EX y el add consumidor en ID. "
            "PC se conserva, Valid_E cae para marcar la burbuja y el consumidor recibe el dato "
            "desde WB en el siguiente ciclo. Memoria[96] y x2 valen 25; memoria[100] termina en 25.",
            "ReportCaption"), PageBreak()]

story += [heading("P4 - Flushing por cambio de control"), img(P4),
          p("El beq tomado y el jal provocan dos redirecciones. IF/ID e ID/EX quedan inválidos "
            "en cada una; las dos instrucciones sw del camino incorrecto nunca escriben en dirección "
            "104. El beq no tomado conserva el flujo secuencial. El enlace de jal en x3 es 24 y "
            "el store final escribe 25 en dirección 100.", "ReportCaption"),
          heading("Dual Fetch, Dual Decode y datapath preliminar"), img(DUAL),
          p("La vía 0 y la vía 1 obtienen PC 0/4 y después 8/12. En EX, dos operaciones "
            "independientes generan 10/15 y 4/5. Un hold invalida EX sin perder ID; luego el "
            "redirect fija los PC a 64/68. Esta prueba verifica estructura preliminar, no emisión "
            "dinámica ni ejecución superescalar completa.", "ReportCaption"), PageBreak()]

story += [heading("Módulos y reproducción"),
          table([
              ["Bloque", "Archivo / responsabilidad"],
              ["A", "datapath.v, hazardunit.v, riscvsingle.v, controller.v, regfile.v, imem.v, dmem.v"],
              ["B preliminar", "dualissue_prelim.v, regfile_dual.v, dual_prelim_tb.v"],
              ["Pruebas", "tests/gen_programs.py, tests/e1_*.S, tests/e1_*.mem, testbench.v, regfile_dual_tb.v"],
          ], [40 * mm, 137 * mm]),
          Spacer(1, 3 * mm),
          p("Ejecutar <b>./run_e1.ps1</b> dentro de pipeline/. El script requiere Python e Icarus "
            "Verilog, regenera los .mem, compila las pruebas y escribe los VCD en tests/. Las seis "
            "verificaciones terminan en PASS o con error explícito; ninguna depende de una captura manual."),
          heading("Límites y siguiente paso"),
          p("El ISA cubierto sigue siendo un subconjunto de RV32I. El prototipo de doble vía no "
            "incluye Issue Unit, reagrupamiento, forwarding entre vías, arbitraje de memoria/branch "
            "ni doble writeback; esas funciones corresponden a E2. El programa legado riscvtest.dat "
            "no cumple la condición de éxito del antiguo testbench y se conserva sin usarlo como "
            "prueba E1. Antes de presentar este PDF, completar nombres, revisar las capturas con el "
            "profesor o equipo e incorporar cualquier instrucción ISA adicional que exija el curso."),
          p("Fuentes de requisitos: Proyecto2_Enunciado.pdf (secciones 1-4) y "
            "Proyecto2_Indicaciones_Generales_Rubrica.pdf (sección 2). "
            "Resultados: simulación Icarus Verilog de run_e1.ps1.", "ReportSmall")]


def decorate(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#C9D8E1"))
    canvas.line(16 * mm, 16 * mm, width - 16 * mm, 16 * mm)
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(17 * mm, 10 * mm, "Arquitectura de Computadoras - Proyecto 2 - E1")
    canvas.drawRightString(width - 17 * mm, 10 * mm, f"Página {doc.page}")
    canvas.restoreState()


pdf = OUT / "Informe_E1_Proyecto2.pdf"
doc = SimpleDocTemplate(str(pdf), pagesize=A4,
    leftMargin=16 * mm, rightMargin=16 * mm,
    topMargin=17 * mm, bottomMargin=22 * mm,
    title="Proyecto 2 - Informe preliminar E1",
    author="Equipo de Arquitectura de Computadoras")
doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
print(pdf)
