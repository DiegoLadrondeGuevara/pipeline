"""Generate directed RV32I programs for the functional dual-issue core."""
from pathlib import Path
from gen_programs import addi, alu, beq, jal, lw, sw, nop

root = Path(__file__).resolve().parent
cases = {
    1: [
        addi(1, 0, 10), addi(2, 0, 15),
        alu("add", 3, 1, 2, 0), addi(4, 0, 7),
        addi(5, 3, 1), addi(5, 4, 2),
        addi(0, 0, 99), addi(6, 5, 1),
        addi(7, 6, 1), addi(8, 7, 1),
        sw(8, 96, 0),
    ],
    2: [
        addi(1, 0, 25), addi(2, 0, 4),
        sw(1, 96, 0), addi(3, 2, 3),
        addi(4, 3, 1), lw(5, 96, 0),
        sw(4, 100, 0), sw(5, 104, 0),
    ],
    3: [
        addi(1, 0, 1), addi(2, 0, 2),
        beq(1, 1, 12), sw(1, 108, 0),
        addi(3, 0, 99), addi(3, 0, 3),
        beq(1, 2, 8), beq(1, 2, 8),
        addi(4, 0, 4), addi(5, 0, 5),
        beq(1, 1, 12), sw(1, 112, 0),
        addi(6, 0, 99), addi(6, 0, 6),
        jal(7, 8), sw(1, 116, 0),
        sw(6, 100, 0),
    ],
    4: [
        addi(1, 0, 25), addi(2, 0, 1),
        sw(1, 96, 0), lw(3, 96, 0),
        alu("add", 4, 3, 2, 0), sw(4, 100, 0),
    ],
}
for num, program in cases.items():
    stem = f"e2_{num}"
    words = [w for _, w in program]
    (root / f"{stem}.mem").write_text("\n".join(f"{w:08x}" for w in words + [nop()[1]] * (256-len(words))) + "\n")
    (root / f"{stem}.S").write_text("\n".join(f"{asm:<32} # PC={i*4:03d}" for i,(asm,_) in enumerate(program)) + "\n")
    print(stem, len(program), "instructions")
