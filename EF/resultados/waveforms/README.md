# Waveforms del programa propio

`propio_C.vcd` se generó el 16/11/2026 con `../run_propio_wave.ps1`. Ejecuta `propio.S` en la arquitectura C con BTB. La simulación pasó: 233 ciclos, 268 instrucciones retiradas, 79 ciclos de doble emisión y 24 stalls Load-Use.

Para regenerar y abrir el visor desde `EF/`:

```powershell
./run_propio_wave.ps1 -Open
```

`propio_C_01_load_use.gtkw` contiene las señales de la primera captura. La captura recibida del equipo se guardó sin alteraciones como `captura_01_raw_load_use.png` y se incorporó en la sección 8.5 del informe con interpretación y tabla. Muestra `lw x9,0(x1)` en PC 40 (0x28) y `add x4,x4,x9` en PC 44 (0x2c). El par se separa por RAW, aparece el stall Load-Use y después se observan `x9=3` y `x4=3`.

`propio_C_02_memoria_emision.gtkw` selecciona las señales para el siguiente caso: conflicto entre `sw` (PC 36) y `lw` (PC 40) en las vías de ID, seguido de una pareja independiente emitida en paralelo. La ventana útil es aproximadamente **70–120 ns**. Las capturas e interpretaciones restantes se incorporarán una por una.

La segunda captura recibida del equipo se guardó sin alteraciones como `captura_02_memoria_emision.png` y se incorporó en la sección 8.6 del informe. La captura 8.7 del BTB sigue pendiente.

`propio_C_03_btb.gtkw` selecciona las señales del BTB. La captura recibida del equipo se guardó sin alteraciones como `captura_03_btb.png` y se incorporó en 8.7 con interpretación y tabla. La ventana muestra una corrección de PC del branch de retorno cerca de 190 ns y una predicción correcta de ese mismo branch cerca de 310 ns.

`docente_C.vcd` se generó con `../run_docente_wave.ps1`: el programa docente en C pasó los cuatro cierres y terminó en 320 ciclos. `docente_C_01_etapa_A.gtkw` prepara el primer cierre. Mostrar aproximadamente **95–135 ns**: el store de PC 0x34 a dirección 1544, `stage=1`, `checkpoint_passed=1`, registros x5=11, x6=5, x10=12 y memoria 1536/1540/1544 = 11/5/12. El marcador `checkpoint_passed` solo cambia después de que el testbench ha comprobado todos los registros y posiciones de memoria de la etapa.

La captura de etapa A recibida del equipo se guardó sin alteraciones como `captura_04_docente_etapa_A.png` y se incorporó en 8.1. `docente_C_02_etapa_B.gtkw` prepara el siguiente cierre; mostrar aproximadamente **175–265 ns** para incluir los stores en 1548/1552/1556, los registros x11–x18 y el bit 1 de `checkpoint_passed`, que sube cerca de 256 ns.

La captura de etapa B recibida del equipo se guardó sin alteraciones como `captura_05_docente_etapa_B.png` y se incorporó en 8.2. `docente_C_03_etapa_C.gtkw` prepara el siguiente cierre. Mostrar aproximadamente **2400–2460 ns**: el último store escribe 24 en 1568 en el ciclo 244 y `checkpoint_passed` pasa de 3 a 7 cerca de 2456 ns. `x19` se reinicia al entrar en D después de ese cierre, por lo que conviene encuadrar antes de 2460 ns.

La captura de etapa C recibida del equipo se guardó sin alteraciones como `captura_06_docente_etapa_C.png` y se incorporó en 8.3. `docente_C_04_etapa_D.gtkw` prepara el cierre final. Mostrar aproximadamente **3030–3220 ns**: los stores finales escriben 74 en 1572, 4 en 1576 y 1 en 1584/1588; la posición 1580 permanece en 0. `checkpoint_passed` pasa de 7 a 15 cerca de 3216 ns.

El cierre D fue aportado por el equipo en tres capturas consecutivas, guardadas sin alteraciones como `captura_07a_docente_etapa_D.png`, `captura_07b_docente_etapa_D.png` y `captura_07c_docente_etapa_D.png`. El informe las incorpora en 8.4 con interpretación y tabla. Las siete evidencias del informe están completas.
