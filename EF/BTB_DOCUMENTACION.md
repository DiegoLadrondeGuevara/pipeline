# Optimización C: Branch Target Buffer

**Base:** `B_dual_issue/` de E2. **Estado del código:** implementado y probado el 16/11/2026. **Aprobación docente:** el equipo confirma que el profesor aprobó verbalmente el BTB en clase; no se indicó fecha exacta. **Waveforms:** aplazadas por indicación del equipo.

## Problema y objetivo

B resuelve los branches y jumps en EX. Cuando el destino se conoce en esa etapa, el fetch secuencial ya ha traído instrucciones jóvenes; si el salto es tomado, se anulan y se reinicia la búsqueda en el destino. Los bucles de los programas finales repiten este costo. C añade un Branch Target Buffer (BTB) para recordar destino y tendencia de salto y elegir el próximo PC desde IF, antes de resolver el control en EX. La corrección sigue dependiendo del resultado real en EX.

## Estructura

- Tabla de 16 entradas de mapeo directo. Índice `PC[5:2]`; etiqueta completa de 32 bits para evitar falsos aciertos entre PC que comparten índice.
- Por entrada: `valid` (1 bit), etiqueta (32), destino (32) y contador saturante de dos bits (2). Almacenamiento lógico: 16 × 67 = 1072 bits, sin contar lógica de lectura/control.
- Dos consultas combinacionales, para `fetch_pc` y `fetch_pc+4`. Un único puerto de actualización desde el recurso de branch compartido en EX.
- Una rama condicional tomada que no estaba en la tabla se instala con contador `10`; un JAL/JALR tomado se instala con `11`. Un acierto tomado incrementa el contador hasta `11`; uno no tomado lo decrementa hasta `00`. Una rama no tomada que no estaba en la tabla no se instala.
- Se predice salto tomado cuando coinciden `valid` y etiqueta y el bit alto del contador vale 1. La etiqueta completa evita usar el destino de otra instrucción con el mismo índice.

## Integración con el pipeline E2

1. IF consulta los dos PC candidatos. Si la primera instrucción tiene predicción tomada, se guarda solo esa instrucción y el siguiente fetch usa su destino. Si no, se guardan ambas; cuando la segunda predice salto tomado, el siguiente fetch usa su destino. En ausencia de predicción tomada se avanza secuencialmente.
2. La pareja deslizante IF/ID conserva `pred_next_d` y `pred_taken_d` junto al PC/instrucción. Si se emite solo la antigua, la joven y su metadato pasan a la posición 0. Si la posición 0 quedó sola por una predicción, se rellena con un par nuevo. La posición 1 no se emite en el mismo ciclo que una instrucción de control predicha tomada en posición 0; así el destino se emite posteriormente y se evita especulación dentro del par.
3. ID/EX transporta el PC siguiente predicho. EX usa el comparador y sumador de branch ya compartidos en B, obtiene el PC real y lo compara con el predicho. Si coinciden, no hay redirección. Si difieren, se redirige al PC real y se anulan solo las instrucciones más jóvenes; la vía 0 del mismo par se conserva cuando el control está en vía 1.
4. EX actualiza la tabla una vez por instrucción de control válida. La memoria, las dos ALU, el Register File, la Issue Unit y el forwarding básicos de E2 no se duplican ni reemplazan.

**Cambios RTL frente a B:** `C_dual_issue_optimizado/rtl/btb.v` (nuevo) y `C_dual_issue_optimizado/rtl/dualissue.v` (fetch, metadatos, validación y contadores). `dmem.v` se amplió de 256 a 512 palabras en **A, B y C por igual** para la dirección de datos 1536 del programa docente; no es parte de la optimización.

**Cambio mínimo al diagrama E2:** añadir una caja BTB al lado de IF con dos entradas de PC, salidas `predict/target`, una flecha de actualización desde la unidad de branch de EX y el metadato de PC predicho en IF/ID e ID/EX. El resto de las dos vías y recursos compartidos permanece como en el diagrama de E2.

## Programas y comprobación

- Programa docente: 90 instrucciones estáticas, cuatro etapas A–D y bucle `fin`. Se verifican los 32 registros y las posiciones de memoria indicadas al cierre de cada etapa. Las tres versiones retiran 312 instrucciones dinámicas antes de `fin` y obtienen el mismo estado final.
- Programa propio: 45 instrucciones estáticas; genera en memoria los valores 3…14, los recorre dos veces y combina sumas, conteos por umbral, un hash acumulativo, Load-Use, conflictos del puerto de memoria, branches hacia adelante y bucles hacia atrás. Resultados: suma=102 en generación y lectura, 6 valores menores que 9, 6 mayores o iguales, hash=16368, suma de índices=66. Los tres procesadores retiran 268 instrucciones dinámicas y producen los mismos 12 datos y 7 resultados en memoria.
- `run_code_checks.ps1` ensambla ambos programas y ejecuta sus testbenches en A/B/C sin VCD. También pasa la prueba unitaria BTB (miss frío, destino, contador, dos puertos y colisión de índice), los cuatro casos dirigidos de E2 en C y cinco equivalencias E1.

## Comparación medida

Los ciclos se cuentan desde que baja reset hasta el store terminal, con el mismo `.mem` y estado inicial en A/B/C. Se cuentan instrucciones válidas retiradas con PC anterior al bucle `fin`; el bucle de terminación queda fuera. Se supone el mismo período de reloj; no se ha medido frecuencia máxima de síntesis.

| Programa | Versión | Retiradas | Ciclos | IPC | CPI | Speedup vs A | Speedup vs B |
|---|---|---:|---:|---:|---:|---:|---:|
| Docente | A | 312 | 458 | 0.6812 | 1.4679 | 1.0000 | 0.8428 |
| Docente | B | 312 | 386 | 0.8083 | 1.2372 | 1.1865 | 1.0000 |
| Docente | C | 312 | 320 | 0.9750 | 1.0256 | 1.4313 | 1.2063 |
| Propio | A | 268 | 363 | 0.7383 | 1.3545 | 1.0000 | 0.7934 |
| Propio | B | 268 | 288 | 0.9306 | 1.0746 | 1.2604 | 1.0000 |
| Propio | C | 268 | 233 | 1.1502 | 0.8694 | 1.5579 | 1.2361 |

| Programa | Versión | Ciclos de doble emisión | Stalls Load-Use | Emisiones parciales | Predicciones BTB de tomado | Decisiones correctas | Correcciones |
|---|---|---:|---:|---:|---:|---:|---:|
| Docente | B | 140 | 11 | 99 | — | — | — |
| Docente | C | 85 | 11 | 152 | 63 | 57 | 32 |
| Propio | B | 110 | 24 | 83 | — | — | — |
| Propio | C | 79 | 24 | 105 | 32 | 36 | 6 |

`Decisiones correctas` incluye tanto destino tomado predicho como continuación secuencial correcta. `Correcciones` cuenta discrepancias entre PC predicho y real en EX; para el docente se resolvieron 89 controles (57+32), y para el propio 42 (36+6). Los testbenches filtran `PC < fin` para excluir incluso la primera resolución del bucle terminal de estas métricas. Los contadores internos del RTL son generales y pueden seguir contando si la simulación continúa. La suma de `predicciones BTB de tomado` no es el denominador de `decisiones correctas`.

C reduce los ciclos frente a B en ambos programas: 386/320=1.2063 en el docente y 288/233=1.2361 en el propio. La reducción se observa en los recorridos iterativos, donde los destinos tomados se repiten. C registra menos ciclos de doble emisión y más emisiones parciales, porque no empareja una instrucción de control predicha tomada con su destino antes de resolverla; aun así termina antes al evitar parte de las redirecciones tardías de B. Load-Use se mantiene igual en B y C para cada programa, como corresponde a un cambio de control y no de forwarding.

## Límites y pendientes

- Un BTB de mapeo directo puede reemplazar entradas por colisiones de índice. Los cambios de dirección de un JALR y los patrones de branch poco estables pueden producir correcciones.
- La comparación de ciclos supone igual período de reloj; falta medir el costo de área y frecuencia del BTB si se quiere afirmar speedup en tiempo real.
- El equipo comunicó la aprobación verbal del BTB por el profesor en clase; no hay acta o fecha exacta en el repositorio.
- Faltan waveforms del cierre de las etapas A–D del docente, al menos dos casos clave y una captura de predicción/acierto/corrección del BTB. No se han generado en esta fase.
