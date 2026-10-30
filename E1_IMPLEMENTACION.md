# E1 — Implementación y verificación

## Estado actual

El procesador `riscvpipelined` de `riscvsingle.v` y `datapath.v` es el **Single-Issue A**. Sus cinco etapas tienen señales de validez, controles propagados con la instrucción, forwarding desde MEM/WB, stall de Load-Use y flush de instrucciones jóvenes al resolver `beq` o `jal` en EX. `MemWrite` ahora viaja hasta MEM junto con dirección y dato. Un store puede recibir su dato mediante forwarding.

`dualissue_prelim.v` es un **prototipo de E1** de Dual Fetch/Dual Decode: lee dos palabras consecutivas, avanza PC de ocho en ocho, decodifica ambas, guarda datos/control de ambas vías en ID/EX y calcula dos resultados ALU para instrucciones independientes. `hold` conserva el par de ID e inserta una burbuja en EX; `flush` redirige PC y anula el par. Usa `regfile_dual.v` de cuatro lecturas y dos escrituras. **Aún no es el procesador B de E2:** faltan Issue Unit, reagrupamiento, forwarding entre vías, WB doble, memoria/branch compartidos y retiro ordenado.

## Mapa de A

```text
PC/IF -> IF/ID -> ID/EX -> EX/MEM -> MEM/WB -> Register File
            |        |         |         |
         Decode    ALU/BEQ   data mem    WB
            |        ^         |         |
            +--- Hazard Unit <-+---------+
                 stall / forwarding / flush
```

- `Stall_D` retiene PC e IF/ID e inserta una burbuja en ID/EX cuando un `lw` de EX alimenta una instrucción de ID.
- `ForwardAE` y `ForwardBE` eligen MEM antes que WB, excepto que un load en MEM todavía no tiene dato disponible. `ForwardedB_E` también alimenta los stores.
- `PCSrc_E` redirige a `PC_E + ImmExt_E` y anula IF/ID e ID/EX. Los bits `Valid_D/E/M/W` impiden efectos de instrucciones anuladas.
- El Register File escribe en el flanco de bajada para que Decode lea el valor de WB en la segunda mitad del ciclo.

## Cómo reproducir

Desde `pipeline/`, con Python e Icarus Verilog (`iverilog` y `vvp`) instalados:

```powershell
./run_e1.ps1
```

El script genera los `.mem` desde `tests/gen_programs.py`, compila tres testbenches y ejecuta seis verificaciones. Los archivos `tests/e1_*.S` son listados Assembly de cada programa; los `.mem` contienen las palabras que carga `imem`. Los VCD se guardan en `tests/` y se pueden abrir con GTKWave u otro visor compatible. En `imem.v` también se puede elegir cualquier programa con `+PROGRAM=ruta/al/programa.mem`. El testbench Single-Issue permite `+CASE=1..4` y `+VCD=ruta.vcd`.

Para regenerar el borrador del informe E1 con las waveforms reales, después de las pruebas ejecutar `pip install -r requirements-report.txt` y `python tools/build_e1_report.py`. El archivo resultante está en `output/pdf/Informe_E1_Proyecto2.pdf`.

## Evidencia obtenida en simulación

| Caso | Qué verifica | Resultado | Señales clave del VCD |
|---|---|---|---|
| `e1_1` | Operaciones ISA soportadas espaciadas sin hazards: R, I, `lw` y `sw`. | PASS; 0 stalls; registros y memoria correctos. | `PC_F`, `Instr_D`, `ALUResult_E`, `Result_W`, `MemWrite`. |
| `e1_2` | RAW ALU, prioridad de productores y forwarding hacia store. | PASS; 11 ciclos; 6 ciclos con forwarding; 0 stalls. | `ForwardAE/BE`, `SrcA_E`, `ForwardedB_E`, `Rd_M/W`, `WriteData_M`. |
| `e1_3` | Store inicial, `lw` seguido inmediatamente por consumidor, burbuja y uso del valor cargado. | PASS; 9 ciclos; exactamente 1 stall; memoria y registros correctos. | `Stall_D`, `PC_F`, `Instr_D`, `Valid_E`, `ReadData_W`, `ForwardAE`. |
| `e1_4` | `beq` tomado/no tomado, `jal`, link y eliminación de stores de camino incorrecto. | PASS; 13 ciclos; 2 redirecciones; sin escritura a dirección 104. | `PCSrc_E`, `PCTarget_E`, `Valid_D/E`, `MemWrite`, `Rd_W`. |
| `e1_dual` | Fetch/Decode de dos pares 0/4 y 8/12, dos resultados ALU, hold y redirect. | PASS. | `PC0_F`, `PC1_F`, `Instr0_D`, `Instr1_D`, `PC0_E`, `PC1_E`, `ALUResult0_E`, `ALUResult1_E`. |
| `regfile_dual` | Cuatro lecturas, dos escrituras, `x0` fijo y prioridad de la vía joven. | PASS. | Salida textual del testbench. |

Los ciclos de la tabla cuentan desde la liberación de reset hasta el store de éxito; **no son todavía métricas de rendimiento A/B/C**. Para E2/EF se deberá definir un punto de terminación común y contar instrucciones retiradas válidas.

## Alcance y pendientes

- El conjunto implementado es el subconjunto del código base: `lw`, `sw`, `beq`, `jal`, `addi`, operaciones R `add/sub/slt/and/or/sll/srl` y las variantes I que decodifica `aludec.v`. No afirmar cobertura de RV32I completo hasta implementar y probar instrucciones restantes.
- El programa legado `riscvtest.dat` se conserva como material recibido. El antiguo testbench esperaba un store de 25 en dirección 100; con la memoria ampliada y el pipeline corregido, ese programa escribe en 96 y 292 y no satisface esa condición. Los programas E1 nuevos tienen resultados esperados explícitos y son los usados en la regresión.
- Hay un **borrador PDF de E1** con diagrama, waveforms y resultados interpretados. Antes de entregarlo faltan nombres de los integrantes, fecha real, revisión del equipo y cualquier ajuste de alcance ISA indicado por el profesor.
- Para E2, implementar emisión dinámica y reagrupamiento antes de conectar el prototipo de doble vía a `top.v`. El top actual sigue ejecutando A, y eso es intencional para poder conservarlo como referencia funcional.
