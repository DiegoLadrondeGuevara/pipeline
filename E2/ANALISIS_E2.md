# E2 — requisitos, rúbrica y estado de implementación

Fuentes: `../../Proyecto2_Enunciado.pdf` (secciones 2–5), `../../Proyecto2_Indicaciones_Generales_Rubrica.pdf` (sección 3) y `../../GUIA_OBJETIVOS_PROYECTO2.md`. La fecha comunicada por el equipo es **9 de noviembre de 2026**. El documento oficial indica «antes de la sesión 14.1» y no fija una hora de calendario.

## Punto de partida: E1

La versión A (`rtl/datapath.v` y `rtl/top.v`) ya ejecuta las pruebas de pipeline, forwarding, Load-Use y flush. El prototipo `rtl/dualissue_prelim.v` lee y decodifica dos instrucciones, usa cuatro lecturas de `regfile_dual.v` y lleva dos vías hasta EX. Sus `we0` y `we1` están conectados a cero: **no es todavía un procesador B funcional**. Faltan Issue Unit, EX/MEM y MEM/WB de dos vías, memoria compartida, branches y writeback reales. Los archivos de E1 originales permanecen fuera de esta carpeta.

## Rúbrica E2, 4 puntos

| Criterio oficial | Puntos | Trabajo concreto de código | Evidencia exigible |
|---|---:|---|---|
| Datapath Dual-Issue e Issue Unit | 0.75 | Dos ALU y controles por vía; cuatro lecturas y dos escrituras de registro; registros IF/ID, ID/EX, EX/MEM y MEM/WB; decisión de emitir 0/1/2 en orden; conservar la joven y reagruparla con la siguiente tras emitir solo la antigua. | Dos ALU independientes emitidas juntas, PC/orden de cada vía, dos resultados y escrituras; emisión parcial sin pérdidas ni duplicados. |
| Forwarding, hazards y stalls | 1.00 | Detectar RAW dentro del par y con etapas previas, usando solo fuentes realmente leídas; detener ante Load-Use; reenviar desde MEM/WB de cualquiera de las dos vías, con prioridad al productor más joven; impedir efectos de burbujas. | Casos RAW, Load-Use, forwarding cruzado, varias escrituras al mismo `rd`, stalls y señales de selección en VCD. |
| Memoria, branches y flushing | 0.75 | Seleccionar dinámicamente una sola operación Load/Store por ciclo, incluso ALU+memoria en ambos órdenes; separar dos memorias; un recurso de branch; branch/jump en ambas posiciones, tomado o no; redirigir PC y anular solo instrucciones jóvenes. | Resultados en memoria, conflicto de dos memorias, branch tomado/no tomado en ambas posiciones y ausencia de escrituras por instrucciones anuladas. |
| Programas, waveforms y resultados | 0.50 | Programas `.S` y `.mem`, testbench con aserciones y timeout, VCD reproducible, comparación preliminar A/B con mismo programa y criterio de conteo de ciclos e instrucciones retiradas. | Salida PASS/FAIL, estados esperados y observados, ondas interpretables, ciclos e IPC. |
| Pregunta individual | 1.00 | Cada integrante debe poder explicar reglas de emisión, edad de instrucciones, forwarding, Load-Use, memoria compartida y flush ciclo a ciclo. | Preparación oral del equipo; no se obtiene solo con código. |

## Contrato microarquitectónico que se implementa

1. La vía 0 contiene siempre la instrucción más antigua; la vía 1, la siguiente. Si la antigua no puede emitirse por una carga previa, se emiten cero. Si solo la joven presenta un riesgo, se emite una y la joven pasa a ser la antigua del ciclo siguiente.
2. No se emiten juntas dos instrucciones con RAW, dos accesos de datos ni dos operaciones de control. Dos escrituras al mismo destino sin RAW sí son válidas; gana la joven. `x0` nunca cambia.
3. Una carga en EX bloquea consumidores en ID hasta que su dato pueda tomarse desde WB. Para operandos EX se prioriza MEM vía 1, MEM vía 0, WB vía 1 y WB vía 0; cargas en MEM no se reenvían como valor ALU.
4. Una operación de memoria puede ocupar cualquiera de las dos vías. Solo la operación válida seleccionada usa el puerto de datos. Un branch tomado en vía 0 anula la vía 1 y las instrucciones más jóvenes en Decode; uno tomado en vía 1 conserva la vía 0.
5. `valid` acompaña a cada instrucción; las burbujas y el camino anulado no escriben registros ni memoria ni cuentan como retiradas. El PC se desplaza 0, 4 u 8 bytes según la emisión y el reagrupamiento; una redirección tiene prioridad.

## Matriz de pruebas y entregables

- Dos ALU independientes; RAW dentro del par; forwarding desde ambas vías en MEM/WB; Load-Use y emisión cero.
- Dos operaciones de memoria; ALU+memoria y memoria+ALU; store con dato reenviado.
- Dos escrituras simultáneas, mismo `rd` sin RAW y protección de `x0`.
- Branch/jump en primera y segunda posición, tomado y no tomado; flush sin efectos laterales.
- Emisión parcial y reagrupamiento consecutivo, sin perder ni duplicar PC.
- Regresión E1 para A y comparación funcional A/B; ciclos, retiradas e IPC del mismo programa.

## Estado verificado del código E2

| Requisito | Archivo / prueba | Resultado |
|---|---|---|
| Dos vías completas, cuatro lecturas y dos escrituras | `rtl/dualissue.v`, `rtl/regfile_dual.v`, `testbenches/e2_tb.v` caso 1 | Dos ALU y escrituras simultáneas; el `rd` repetido conserva el valor de la vía joven; `x0` permanece en cero. |
| Emisión, RAW, conservación y reagrupamiento | `rtl/issueunit.v`, casos 1 y 4 | La secuencia exacta de PC retirados se compara con la esperada; se observa emisión 0/1/2 y no hay pérdidas ni duplicados. |
| Forwarding y Load-Use | `rtl/forward_dual.v`, casos 1 y 4 | Se observan selecciones desde MEM0, MEM1, WB0 y WB1; una carga en EX provoca stall de cero emisiones en su consumidor. |
| Memoria y control compartidos | `rtl/dualissue.v`, casos 2 y 3 | Un único `dmem`; selección de memoria en ambas vías, separación de dos accesos, branches tomados/no tomados en ambas posiciones y stores anulados. |
| Equivalencia y medición | `testbenches/e2_equiv_tb.v`, `testbenches/e2_compare_tb.v` | Estado final de registros y memoria idéntico a A en los cinco programas E1. En `e1_2.mem`, 8 instrucciones hasta el store terminal: A 11 ciclos, B 10 ciclos; IPC 0.727 y 0.800; speedup 1.10 con el mismo período supuesto. |

`./run_e1.ps1` y `./run_e2.ps1` pasan desde esta carpeta. Las cuatro ondas E2 están en `tests/e2_1.vcd` a `tests/e2_4.vcd`. La comparación termina al **escribir el store terminal** en ambos núcleos; así evita incluir los NOP de relleno que siguen al programa en la memoria. Los contadores libres del módulo continúan contando esos NOP si la simulación sigue después del fin del programa.

El código conserva el subconjunto RV32I implementado en A: operaciones ALU enteras, cargas/almacenamientos de byte, media palabra y palabra, branches, JAL/JALR, LUI y AUIPC. FENCE y SYSTEM siguen fuera del entorno de pruebas de este proyecto. El programa aún no proporcionado por el profesor se verificará cuando esté disponible.

Este `.md` documenta alcance, implementación y evidencia de código. El **informe PDF de E2**, con diagrama y waveforms explicadas, queda para la fase posterior indicada por el equipo. La propuesta de optimización para EF requiere aprobación del docente en la sesión 14.1 y es independiente de B.
