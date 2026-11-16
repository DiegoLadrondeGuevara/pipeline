# Comparación reproducible de A, B y C

**Fecha:** 16/11/2026. **Comando:** `./run_code_checks.ps1` desde `EF/`. Los testbenches usan el mismo `.mem`, reinicio, frecuencia de simulación y evento de cierre por programa. El bucle `fin` no se incluye. Las pruebas no generan waveforms.

| Programa | Arquitectura | Instrucciones retiradas | Ciclos | IPC | CPI | Speedup vs A | Speedup vs B |
|---|---|---:|---:|---:|---:|---:|---:|
| Docente | A | 312 | 458 | 0.6812 | 1.4679 | 1.0000 | 0.8428 |
| Docente | B | 312 | 386 | 0.8083 | 1.2372 | 1.1865 | 1.0000 |
| Docente | C | 312 | 320 | 0.9750 | 1.0256 | 1.4313 | 1.2063 |
| Propio | A | 268 | 363 | 0.7383 | 1.3545 | 1.0000 | 0.7934 |
| Propio | B | 268 | 288 | 0.9306 | 1.0746 | 1.2604 | 1.0000 |
| Propio | C | 268 | 233 | 1.1502 | 0.8694 | 1.5579 | 1.2361 |

El testbench del docente verifica registros y memoria en los cuatro cierres A–D; el propio verifica las 12 palabras generadas y 7 salidas. En ambos casos A/B/C producen los mismos valores. El detalle de BTB, contadores y límites está en `../BTB_DOCUMENTACION.md`.
