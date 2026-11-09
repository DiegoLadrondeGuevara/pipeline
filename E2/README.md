# Proyecto 2 — Entrega 2

Esta carpeta es una copia de trabajo independiente de E1. La arquitectura A permanece en `rtl/top.v`; la arquitectura B funcional está en `rtl/dualissue.v`. El prototipo `rtl/dualissue_prelim.v` sigue incluido para reproducir la prueba E1, pero no es el procesador B.

## Reproducir

Desde PowerShell, con Python e Icarus Verilog en `PATH`:

```powershell
./run_e1.ps1
./run_e2.ps1
```

`run_e2.ps1` genera los `.mem`, ejecuta cuatro pruebas dirigidas, compara los estados finales A/B en cinco programas E1 y mide una comparación preliminar con `e1_2.mem`. Cada prueba termina con PASS o un error explícito. Las ondas E2 se guardan en `tests/e2_1.vcd` a `tests/e2_4.vcd`.

## Módulos nuevos

- `rtl/issueunit.v`: emisión 0/1/2, RAW, Load-Use y recursos compartidos.
- `rtl/forward_dual.v`: selección del productor más reciente de ambas vías y etapas.
- `rtl/dualissue.v`: IF/ID con reagrupamiento, dos ALU, EX/MEM y MEM/WB dobles, cuatro lecturas/dos escrituras, un puerto de datos y branch compartido.

El alcance exacto de la rúbrica y las pruebas está en `ANALISIS_E2.md`.

## Informe base

`informe/Informe_E2_Proyecto2_base.pdf` contiene la portada de E2, índice, arquitectura, reglas de emisión, hazards, recursos compartidos, resultados y espacios para cinco capturas reales de GTKWave. La versión editable es `informe/Informe_E2_Proyecto2_base.docx`. La comparación A/B genera también `tests/e2_compare.vcd`.

Las capturas y sus explicaciones ciclo a ciclo están pendientes. Después de insertarlas, habrá que actualizar el índice y revisar la paginación. Los scripts `tools/build_e2_report.py` y `tools/render_e2_pdf.py` reconstruyen la versión base desde cero; no deben ejecutarse sobre una copia del DOCX que ya tenga ediciones manuales que se deseen conservar.
