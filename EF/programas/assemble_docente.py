"""Assemble the RV32I subset used by the final teacher and own programs."""
import argparse
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "docente.S"
OUTPUT = HERE / "docente.mem"
NOP = 0x00000013


def reg(text):
    match = re.fullmatch(r"x(\d+)", text)
    if not match or int(match.group(1)) > 31:
        raise ValueError(f"Invalid register: {text}")
    return int(match.group(1))


def imm12(value):
    if not -2048 <= value <= 2047:
        raise ValueError(f"12-bit immediate out of range: {value}")
    return value & 0xFFF


def encode(op, args, pc, labels):
    if op == "addi":
        rd, rs1, value = reg(args[0]), reg(args[1]), imm12(int(args[2], 0))
        return (value << 20) | (rs1 << 15) | (rd << 7) | 0x13
    if op in ("add", "sub", "slt"):
        rd, rs1, rs2 = map(reg, args)
        funct3 = 2 if op == "slt" else 0
        funct7 = 0x20 if op == "sub" else 0
        return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | 0x33
    if op in ("lw", "sw"):
        match = re.fullmatch(r"(-?\d+)\((x\d+)\)", args[1])
        if not match:
            raise ValueError(f"Invalid memory operand: {args[1]}")
        offset, rs1 = imm12(int(match.group(1))), reg(match.group(2))
        value_reg = reg(args[0])
        if op == "lw":
            return (offset << 20) | (rs1 << 15) | (2 << 12) | (value_reg << 7) | 0x03
        return (((offset >> 5) & 0x7F) << 25) | (value_reg << 20) | (rs1 << 15) | (2 << 12) | ((offset & 31) << 7) | 0x23
    if op == "beq":
        rs1, rs2 = reg(args[0]), reg(args[1])
        offset = labels[args[2]] - pc
        if offset % 2 or not -4096 <= offset <= 4094:
            raise ValueError(f"Invalid branch offset: {offset}")
        value = offset & 0x1FFF
        return (((value >> 12) & 1) << 31) | (((value >> 5) & 63) << 25) | (rs2 << 20) | (rs1 << 15) | (((value >> 1) & 15) << 8) | (((value >> 11) & 1) << 7) | 0x63
    if op == "jal":
        rd = reg(args[0])
        offset = labels[args[1]] - pc
        if offset % 2 or not -(1 << 20) <= offset < (1 << 20):
            raise ValueError(f"Invalid jump offset: {offset}")
        value = offset & 0x1FFFFF
        return (((value >> 20) & 1) << 31) | (((value >> 1) & 1023) << 21) | (((value >> 11) & 1) << 20) | (((value >> 12) & 255) << 12) | (rd << 7) | 0x6F
    raise ValueError(f"Unsupported instruction: {op}")


def main(source=SOURCE, output=OUTPUT):
    labels = {}
    instructions = []
    pc = 0
    for raw in source.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("."):
            continue
        if line.endswith(":"):
            labels[line[:-1]] = pc
            continue
        parts = line.replace(",", " ").split()
        instructions.append((pc, parts[0], parts[1:]))
        pc += 4
    if len(instructions) > 256:
        raise ValueError("Program exceeds instruction memory")
    words = [encode(op, args, pc, labels) for pc, op, args in instructions]
    output.write_text("\n".join(f"{word:08x}" for word in words + [NOP] * (256 - len(words))) + "\n", encoding="ascii")
    print(f"{source.stem}: {len(words)} instructions; fin PC={labels['fin']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    main(args.source, args.output)
