"""Rebuild the E2 datapath diagram with readable resource labels for EF."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "datapath_e2_refinado.png"
W, H = 1800, 680
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
regular = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
bold = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
bottom_bold = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26)
small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 25)
blue, pale, gray = "#17324D", "#EAF2F6", "#555555"


def box(x, y, w, h, lines, fill=pale, heading_font=bold):
    d.rounded_rectangle((x, y, x+w, y+h), radius=13,
                        fill=fill, outline=blue, width=3)
    line_y = y + 20
    for j, line in enumerate(lines):
        f = heading_font if j == 0 else small
        bounds = d.textbbox((0, 0), line, font=f)
        width = bounds[2] - bounds[0]
        if width > w - 12:
            raise ValueError(f"Diagram label does not fit: {line}")
        d.text((x + (w-width)/2, line_y), line, font=f, fill=blue)
        line_y += 39


for x, label in ((28,"IF"),(365,"ID"),(702,"EX"),(1039,"MEM"),(1376,"WB")):
    d.text((x+122,10), label, font=bold, fill=blue)
for lane, y in enumerate((70,240)):
    box(28,y,290,130,[f"Vía {lane}","PC + instrucción"])
    box(365,y,290,130,[f"Decode {lane}","lecturas + control"])
    box(702,y,290,130,[f"ALU {lane}","operandos reenviados"])
    box(1039,y,290,130,[f"Registro {lane}","EX / MEM"])
    box(1376,y,290,130,[f"Writeback {lane}","resultado + rd"])
    for x in (325,662,999,1336):
        d.line((x,y+65,x+31,y+65), fill=gray, width=4)
        d.polygon([(x+31,y+65),(x+20,y+57),(x+20,y+73)], fill=gray)

box(365,425,290,135,["Issue Unit","emite 0, 1 o 2"],"#F2F2F2",bottom_bold)
box(702,425,290,135,["Branch compartido","comparador + destino"],"#F2F2F2",bottom_bold)
box(1039,425,290,135,["Memoria de datos","un único puerto"],"#F2F2F2",bottom_bold)
box(1376,425,290,135,["Register File","4 lecturas / 2 escrituras"],"#F2F2F2",bottom_bold)
d.text((35,605), "Los bits valid acompañan ambas vías; la vía 0 contiene la instrucción más antigua.",
       font=regular, fill=blue)
im.save(OUT)
print(OUT)
