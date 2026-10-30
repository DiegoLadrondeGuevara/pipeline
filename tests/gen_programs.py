"""Build four small RV32I-subset programs and readable assembly listings."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOP = 0x00000013


def i_type(imm, rs1, funct3, rd, opcode):
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def r_type(funct7, rs2, rs1, funct3, rd):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | 0x33


def s_type(imm, rs2, rs1):
    return (((imm >> 5) & 0x7F) << 25) | (rs2 << 20) | (rs1 << 15) | (2 << 12) | ((imm & 31) << 7) | 0x23


def b_type(imm, rs2, rs1):
    assert imm % 2 == 0
    return (((imm >> 12) & 1) << 31) | (((imm >> 5) & 63) << 25) | (rs2 << 20) | (rs1 << 15) | (((imm >> 1) & 15) << 8) | (((imm >> 11) & 1) << 7) | 0x63


def j_type(imm, rd):
    assert imm % 2 == 0
    return (((imm >> 20) & 1) << 31) | (((imm >> 1) & 1023) << 21) | (((imm >> 11) & 1) << 20) | (((imm >> 12) & 255) << 12) | (rd << 7) | 0x6F


def addi(rd, rs1, imm): return (f"addi x{rd}, x{rs1}, {imm}", i_type(imm, rs1, 0, rd, 0x13))
def alu_imm(name, rd, rs1, imm, funct3): return (f"{name} x{rd}, x{rs1}, {imm}", i_type(imm, rs1, funct3, rd, 0x13))
def lw(rd, imm, rs1): return (f"lw x{rd}, {imm}(x{rs1})", i_type(imm, rs1, 2, rd, 0x03))
def sw(rs2, imm, rs1): return (f"sw x{rs2}, {imm}(x{rs1})", s_type(imm, rs2, rs1))
def alu(name, rd, rs1, rs2, funct3, funct7=0): return (f"{name} x{rd}, x{rs1}, x{rs2}", r_type(funct7, rs2, rs1, funct3, rd))
def beq(rs1, rs2, imm): return (f"beq x{rs1}, x{rs2}, {imm}", b_type(imm, rs2, rs1))
def jal(rd, imm): return (f"jal x{rd}, {imm}", j_type(imm, rd))
def nop(): return ("nop", NOP)


def spaced(seq):
    out = []
    for item in seq:
        out.extend((item, nop(), nop(), nop()))
    return out


programs = {
    1: spaced([
        addi(1, 0, 10), addi(2, 0, 15),
        alu("add", 3, 1, 2, 0),
        alu("sub", 4, 2, 1, 0, 0x20),
        alu("slt", 5, 1, 2, 2),
        alu("and", 6, 1, 2, 7),
        alu("or", 7, 1, 2, 6),
        alu("sll", 8, 5, 1, 1),
        alu("srl", 9, 8, 5, 5),
        alu_imm("slti", 12, 1, 11, 2),
        alu_imm("andi", 13, 2, 7, 7),
        alu_imm("ori", 14, 1, 1, 6),
        alu_imm("slli", 15, 12, 2, 1),
        alu_imm("srli", 16, 15, 1, 5),
        sw(1, 96, 0), lw(10, 96, 0),
        alu("add", 11, 10, 2, 0), sw(11, 100, 0),
    ]),
    2: [
        addi(1, 0, 10), addi(2, 1, 5), alu("add", 3, 2, 1, 0),
        sw(3, 96, 0), addi(4, 0, 1), addi(4, 4, 2),
        addi(5, 4, 22), sw(5, 100, 0),
    ],
    3: [
        addi(1, 0, 25), sw(1, 96, 0), lw(2, 96, 0),
        alu("add", 3, 2, 0, 0), sw(3, 100, 0),
    ],
    4: [
        addi(1, 0, 1), beq(1, 1, 12), sw(1, 104, 0),
        addi(2, 0, 99), addi(2, 0, 25), jal(3, 12),
        sw(1, 104, 0), addi(2, 0, 99),
        beq(1, 0, 8), sw(2, 100, 0),
    ],
}

for number, program in programs.items():
    stem = f"e1_{number}"
    words = [word for _, word in program]
    (ROOT / f"{stem}.mem").write_text("\n".join(f"{word:08x}" for word in words + [NOP] * (256 - len(words))) + "\n")
    (ROOT / f"{stem}.S").write_text("\n".join(f"{text:<32} # PC={index*4:03d}" for index, (text, _) in enumerate(program)) + "\n")
    print(stem, len(program), "instructions")

dual_pair = [addi(1, 0, 10), addi(2, 0, 15), addi(3, 0, 4), addi(4, 0, 5)]
(ROOT / "e1_dual.mem").write_text("\n".join(f"{word:08x}" for word in [word for _, word in dual_pair] + [NOP] * (256 - len(dual_pair))) + "\n")
(ROOT / "e1_dual.S").write_text("\n".join(f"{asm:<32} # PC={i*4:03d}" for i, (asm, _) in enumerate(dual_pair)) + "\n")
