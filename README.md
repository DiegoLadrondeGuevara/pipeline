# Proyecto 2 - Arquitectura de Computadoras

Implementación de E1 de un procesador RISC-V segmentado y comienzo de la arquitectura Dual-Issue In-Order.

## Carpetas de entrega

| Carpeta | Contenido |
|---|---|
| `rtl/` | Diseño Verilog de los procesadores A y B preliminar. |
| `testbenches/` | Bancos de prueba de E1. |
| `tests/` | Programas Assembly, memorias `.mem` y trazas de simulación `.vcd`. |
| `informe/` | Informe editable `.docx` y copia `.pdf`. |
| `docs/` | Enunciado, rúbrica y notas técnicas. |

## Estado

- `rtl/top.v` ejecuta el procesador Single-Issue A de cinco etapas con forwarding, stall Load-Use y flush de control.
- `rtl/dualissue_prelim.v` demuestra Dual Fetch, Dual Decode y dos vías EX preliminares. Todavía no implementa la Issue Unit ni el procesador B funcional de E2.
- Las cuatro pruebas funcionales obligatorias E1, el prototipo doble, el Register File doble y una prueba adicional de ISA terminan en PASS.
- El núcleo A soporta 37 instrucciones enteras RV32I de cálculo, memoria y control. ECALL/EBREAK y excepciones no forman parte del entorno de ejecución; FENCE actúa como NOP.

## Ejecutar pruebas

Desde esta carpeta, con Python e Icarus Verilog instalados:

```powershell
./run_e1.ps1
```

El script regenera los programas `.mem`, ejecuta siete verificaciones y guarda waveforms `.vcd` en `tests/`. Véase [implementación y resultados de E1](docs/E1_IMPLEMENTACION.md).

## Documentación

- [Guía de objetivos, entregables y plazos](docs/GUIA_OBJETIVOS_PROYECTO2.md)
- [Enunciado](docs/Proyecto2_Enunciado.pdf) y [rúbrica](docs/Proyecto2_Indicaciones_Generales_Rubrica.pdf)
- [Informe técnico E1 editable](informe/Informe_E1_Proyecto2.docx) y [copia PDF](informe/Informe_E1_Proyecto2.pdf)

Las gráficas del informe se generaron a partir de los VCD escritos por los testbenches durante la simulación con `vvp`. `tmp/`, `tools/` y los binarios `.out` son archivos locales y no forman parte del repositorio de entrega.

Antes de subir el informe a Canvas, completar nombres, curso, fecha, dos diagramas encargados a los compañeros y cualquier requisito adicional indicado por el docente.
