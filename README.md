# Proyecto 2 - Arquitectura de Computadoras

Implementación de E1 de un procesador RISC-V segmentado y comienzo de la arquitectura Dual-Issue In-Order.

## Estado

- `top.v` ejecuta el procesador Single-Issue A de cinco etapas con forwarding, stall Load-Use y flush de control.
- `dualissue_prelim.v` demuestra Dual Fetch, Dual Decode y dos vías EX preliminares. Todavía no implementa la Issue Unit ni el procesador B funcional de E2.
- Las cuatro pruebas funcionales E1 y dos pruebas del prototipo doble terminan en PASS.

## Ejecutar pruebas

Desde esta carpeta, con Python e Icarus Verilog instalados:

```powershell
./run_e1.ps1
```

El script regenera los programas `.mem`, ejecuta los testbenches y guarda waveforms `.vcd` en `tests/`. Véase [implementación y resultados de E1](E1_IMPLEMENTACION.md).

## Documentación

- [Guía de objetivos, entregables y plazos](docs/GUIA_OBJETIVOS_PROYECTO2.md)
- [Enunciado](docs/Proyecto2_Enunciado.pdf) y [rúbrica](docs/Proyecto2_Indicaciones_Generales_Rubrica.pdf)
- [Borrador del informe E1](output/pdf/Informe_E1_Proyecto2.pdf)

El informe es preliminar: faltan nombres del equipo, fecha de entrega y revisión final del alcance ISA con el profesor.
