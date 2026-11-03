# Proyecto 2 — Entrega 1

Procesador RISC-V de cinco etapas con forwarding, stall Load Use y flush, más un prototipo Dual Issue de Fetch, Decode y EX.

## Archivos de entrega

| Ruta | Contenido |
|---|---|
| `rtl/` | Código Verilog del procesador Single Issue y del prototipo Dual Issue preliminar. |
| `testbenches/` | Pruebas automáticas de P1–P4, Dual Fetch/Decode, Register File doble y cobertura ISA adicional. |
| `tests/` | Programas `.S`, memorias `.mem` y trazas `.vcd`. |
| `run_e1.ps1` | Reproduce las simulaciones en Windows. |
| `informe/Informe_E1_Proyecto2.pdf` | Informe técnico final de E1. |

## Reproducir

Desde la raíz del proyecto, con Python e Icarus Verilog instalados:

```powershell
./run_e1.ps1
```

El script regenera las memorias, compila el Verilog, ejecuta las cuatro pruebas obligatorias y las pruebas complementarias, y escribe los VCD en `tests/`. Los archivos `.vcd` pueden abrirse con GTKWave.

El prototipo Dual Issue de E1 lee y decodifica dos instrucciones y lleva ambas vías hasta EX. Aún no incorpora Issue Unit, acceso compartido a memoria ni doble writeback funcional.
