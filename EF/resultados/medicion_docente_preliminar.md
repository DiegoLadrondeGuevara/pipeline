# Medición preliminar del programa del docente

**Fecha:** 16 de noviembre de 2026. **Comando:** `./run_code_checks.ps1` desde `EF/`. La prueba no genera waveforms.

Se inicia el conteo al liberar el reset y se cierra cuando se escribe el resultado final en `M[x1+52]`. Se cuentan como retiradas las instrucciones válidas con PC anterior a `fin` (PC 356); el bucle `fin: jal x0, fin` queda excluido. El mismo `.mem` y los mismos valores iniciales se usan en A/B/C. Las cuatro comprobaciones A–D y los estados finales coinciden con el PDF del docente.

| Arquitectura | Retiradas | Ciclos | IPC | CPI | Speedup vs A | Speedup vs B |
|---|---:|---:|---:|---:|---:|---:|
| A — Single-Issue | 312 | 458 | 0.681223 | 1.467949 | 1.000000 | 0.842795 |
| B — Dual-Issue | 312 | 386 | 0.808290 | 1.237179 | 1.186528 | 1.000000 |
| C — Dual-Issue + BTB | 312 | 320 | 0.975000 | 1.025641 | 1.431250 | 1.206250 |

El BTB de C registró 63 predicciones de salto tomado. De los 89 controles resueltos antes de `fin`, 57 tuvieron siguiente PC correcto y 32 requirieron corrección. Estas cifras excluyen la primera resolución de `fin`; los contadores internos del RTL pueden incluirla. El análisis visual sigue pendiente; el programa propio ya figura en `comparacion_codigo.md`. La mejora medida de C frente a B en este programa es `386/320 = 1.20625` bajo el supuesto de igual período de reloj.
