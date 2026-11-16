"""Genera tres figuras comparables a partir de los VCD del programa docente.

Requiere matplotlib. Los tiempos se alinean por la primera y segunda
resolución tomada del salto C1 (PC 0x7C), no por el tiempo absoluto.
"""
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
BRANCH_PC = 0x7C
TARGET_PC = 0x70


def read_vcd(path):
    scopes = []
    names_by_id = defaultdict(list)
    events = defaultdict(list)
    header = True
    time = 0
    with path.open(encoding="utf-8", errors="replace") as source:
        for raw in source:
            line = raw.strip()
            if header:
                if line.startswith("$scope "):
                    scopes.append(line.split()[2])
                elif line.startswith("$upscope "):
                    scopes.pop()
                elif line.startswith("$var "):
                    parts = line.split()
                    names_by_id[parts[3]].append(".".join([*scopes, parts[4]]))
                elif line.startswith("$enddefinitions"):
                    header = False
                continue
            if not line or line.startswith("$"):
                continue
            if line.startswith("#"):
                time = int(line[1:])  # timescale 1 ps
            elif line[0] in "bB":
                bits, identifier = line[1:].split(None, 1)
                value = None if any(c in bits.lower() for c in "xz") else int(bits, 2)
                for name in names_by_id.get(identifier, ()):
                    if name.startswith("docente_tb.wave_") or name in (
                        "docente_tb.clk", "docente_tb.checkpoint_passed",
                        "docente_tb.dut.btb_hit0", "docente_tb.dut.btb_hit1",
                        "docente_tb.dut.predict0", "docente_tb.dut.predict1",
                    ):
                        events[name].append((time, value))
            elif line[0] in "01xXzZ":
                identifier = line[1:]
                value = None if line[0].lower() in "xz" else int(line[0])
                for name in names_by_id.get(identifier, ()):
                    if name.startswith("docente_tb.wave_") or name in (
                        "docente_tb.clk", "docente_tb.checkpoint_passed",
                        "docente_tb.dut.btb_hit0", "docente_tb.dut.btb_hit1",
                        "docente_tb.dut.predict0", "docente_tb.dut.predict1",
                    ):
                        events[name].append((time, value))
    return events


def value_at(changes, time):
    times = [event[0] for event in changes]
    index = bisect_right(times, time) - 1
    return None if index < 0 else changes[index][1]


def normalized_events(changes, start, end):
    if not changes:
        return [(start, None), (end, None)]
    result = [(start, value_at(changes, start))]
    for time, value in changes:
        if start < time < end and value != result[-1][1]:
            result.append((time, value))
    result.append((end, result[-1][1]))
    return result


def find_returns(events):
    prefix = "docente_tb."
    required = ["wave_control_resolved", "wave_branch_pc", "wave_actual_next_pc"]
    for key in required:
        if prefix + key not in events:
            raise ValueError(f"Falta la señal {key}")
    # Una muestra por ciclo en el flanco negativo, después de establecer EX.
    end = max(changes[-1][0] for changes in events.values() if changes)
    hits = []
    for time in range(30_000, end, 10_000):
        if (value_at(events[prefix + "wave_control_resolved"], time) == 1
            and value_at(events[prefix + "wave_branch_pc"], time) == BRANCH_PC
            and value_at(events[prefix + "wave_actual_next_pc"], time) == TARGET_PC):
            hits.append(time)
    if len(hits) < 2:
        raise ValueError(f"Se esperaban dos retornos tomados de C1; hallados {len(hits)}")
    return hits


def draw_digital(ax, changes, y, start, end, color):
    points = normalized_events(changes, start, end)
    for (t0, value), (t1, _) in zip(points, points[1:]):
        level = y + (0.19 if value == 1 else -0.19)
        ax.hlines(level, t0 / 1000, t1 / 1000, color=color, linewidth=2.0)
    for time, _ in points[1:-1]:
        ax.vlines(time / 1000, y - 0.19, y + 0.19, color=color, linewidth=1.0)


def fmt(value, decimal=False):
    if value is None:
        return "X"
    return str(value) if decimal else f"0x{value:X}"


def draw_bus(ax, changes, y, start, end, color, decimal=False):
    points = normalized_events(changes, start, end)
    for (t0, value), (t1, _) in zip(points, points[1:]):
        x0, x1 = t0 / 1000, t1 / 1000
        ax.add_patch(Rectangle((x0, y - 0.27), x1 - x0, 0.54,
                               facecolor="#eef5fb" if value is not None else "#f8edf0",
                               edgecolor=color, linewidth=0.7))
        if x1 - x0 >= 6:
            ax.text((x0 + x1) / 2, y, fmt(value, decimal), fontsize=8.5,
                    ha="center", va="center", color=color, clip_on=True)


def render(arch, events):
    returns = find_returns(events)
    first, second = returns[:2]
    start, end = first - 30_000, second + 30_000
    top = "docente_tb."
    rows = [
        ("clk", "clk", "digital"),
        ("PC de búsqueda", "wave_fetch_pc", "bus"),
        ("PC en ID vía 0", "wave_pc_d0", "bus"),
        ("instrucción ID vía 0", "wave_instr_d0", "bus"),
    ]
    if arch != "A":
        rows.extend([
            ("PC en ID vía 1", "wave_pc_d1", "bus"),
            ("instrucción ID vía 1", "wave_instr_d1", "bus"),
            ("emite vía 0", "wave_issue0", "digital"),
            ("emite vía 1", "wave_issue1", "digital"),
        ])
    else:
        rows.append(("avanza ID a EX", "wave_issue0", "digital"))
    rows.extend([
        ("stall por carga", "wave_stall_load", "digital"),
        ("control en EX", "wave_control_resolved", "digital"),
        ("PC del salto", "wave_branch_pc", "bus"),
        ("PC previsto", "wave_predicted_next_pc", "bus"),
        ("PC real", "wave_actual_next_pc", "bus"),
        ("redirección", "wave_redirect", "digital"),
        ("x19 índice", "wave_x19", "decimal"),
    ])
    if arch == "C":
        rows.extend([
            ("BTB acierto vía 0", "dut.btb_hit0", "digital"),
            ("BTB acierto vía 1", "dut.btb_hit1", "digital"),
            ("predice vía 0", "dut.predict0", "digital"),
            ("predice vía 1", "dut.predict1", "digital"),
        ])
    height = max(7.0, 0.5 * len(rows) + 2)
    fig, ax = plt.subplots(figsize=(17, height), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    for index, (label, key, kind) in enumerate(rows):
        y = len(rows) - index
        full = top + key
        if full not in events:
            raise ValueError(f"Falta {full} en docente_{arch}.vcd")
        color = "#be3137" if key == "wave_redirect" else (
            "#2a7852" if "btb_" in key or "predict" in key and key.startswith("dut.")
            else "#24547e")
        if kind == "digital":
            draw_digital(ax, events[full], y, start, end, color)
        else:
            draw_bus(ax, events[full], y, start, end, color, decimal=kind == "decimal")
        ax.text(start / 1000 - 3, y, label, ha="right", va="center", fontsize=9.5)
        ax.hlines(y - 0.42, start / 1000, end / 1000, color="#e2e7ea", linewidth=0.5)
    for number, time in enumerate((first, second), 1):
        ax.axvline(time / 1000, color="#b97722", linestyle="--", linewidth=1.2)
        ax.text(time / 1000 + 1, len(rows) + 0.55, f"retorno {number}",
                fontsize=9, color="#825015", va="bottom")
    ax.set_xlim(start / 1000, end / 1000)
    ax.set_ylim(0.4, len(rows) + 1.3)
    ax.set_yticks([])
    ax.set_xticks(range((start // 10_000) * 10, end // 1000 + 1, 10))
    ax.grid(axis="x", color="#d9e0e5", linewidth=0.7)
    ax.set_xlabel("Tiempo de simulación (ns)")
    ax.set_title(f"Programa docente · {arch} · dos retornos de C1 (PC 0x7C → 0x70)",
                 fontsize=15, loc="left", pad=18)
    fig.text(0.55, 0.02, "Ondas trazadas desde el VCD de Icarus Verilog. Cada versión tiene su propio tiempo absoluto.",
             ha="center", fontsize=9, color="#555")
    fig.subplots_adjust(left=0.22, right=0.98, top=0.88, bottom=0.10)
    out = HERE / f"captura_docente_{arch}_C1.png"
    fig.savefig(out)
    plt.close(fig)
    def measured(time, name):
        return value_at(events[top + name], time)
    print(f"{arch}: retorno1={first/1000:.0f} ns redirect={measured(first,'wave_redirect')} "
          f"pred={fmt(measured(first,'wave_predicted_next_pc'))} "
          f"real={fmt(measured(first,'wave_actual_next_pc'))}")
    print(f"{arch}: retorno2={second/1000:.0f} ns redirect={measured(second,'wave_redirect')} "
          f"pred={fmt(measured(second,'wave_predicted_next_pc'))} "
          f"real={fmt(measured(second,'wave_actual_next_pc'))}")
    print(out)


def main():
    for arch in "ABC":
        render(arch, read_vcd(HERE / f"docente_{arch}.vcd"))


if __name__ == "__main__":
    main()
