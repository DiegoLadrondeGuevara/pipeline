# Mapa de archivos para la entrega final

**Estado al 16/11/2026:** los dos programas pasan en A, B y C; el informe PDF y su DOCX editable están completos. **Falta el PDF de presentación.** Este mapa identifica los archivos de entrega y los materiales de reproducción; no representa aún un paquete definitivo listo para subir.

| Requisito de la rúbrica | Ubicación en `EF/` | Estado |
|---|---|---|
| Procesador A, Pipeline Single-Issue | `A_single_issue/rtl/`; pruebas en `A_single_issue/testbenches/`, `tests/` y `run_e1.ps1` | Verificado |
| Procesador B, Dual-Issue de E2 | `B_dual_issue/rtl/`; pruebas en `B_dual_issue/testbenches/`, `tests/` y `run_e2.ps1` | Verificado |
| Procesador C, Dual-Issue con BTB | `C_dual_issue_optimizado/rtl/`, incluido `btb.v`; pruebas en `C_dual_issue_optimizado/testbenches/` y `tests/` | Verificado |
| Assembly y memorias comunes a A/B/C | `programas/propio.S`, `propio.mem`, `docente.S`, `docente.mem`; PDF original del docente en la misma carpeta | Verificado |
| Testbenches finales de los dos programas | `testbenches/propio_tb.v` y `docente_tb.v`; `run_code_checks.ps1` recompila y ejecuta las seis corridas | Verificado |
| Resultados y waveforms interpretadas | `resultados/comparacion_codigo.md`, `resultados/waveforms/`, secciones 8.1–8.7 del informe | Verificado |
| Informe final PDF | `informe/Informe_Final_Proyecto2_BTB.pdf` | Presente, 14 páginas |
| Informe final editable | `informe/Informe_Final_Proyecto2_BTB_editable.docx` | Presente; conservar |
| Presentación final PDF | `presentacion/` | **Pendiente** |

## Reproducción

Desde PowerShell en `EF/`, con Python, Icarus Verilog (`iverilog`, `vvp`) y las rutas de `.mem` actuales:

```powershell
./run_code_checks.ps1
```

El 16/11/2026 pasó las seis corridas, la prueba unitaria del BTB, cuatro casos E2 y cinco comparaciones E1 en C. También pasaron por separado `A_single_issue/run_e1.ps1` y `B_dual_issue/run_e2.ps1`. El mismo Assembly se usa en las tres arquitecturas. Los resultados medidos están en `resultados/comparacion_codigo.md`; las capturas e interpretaciones están en el informe.

## Material de apoyo

- `BTB_DOCUMENTACION.md`: diseño, integración, pruebas y límites del BTB.
- `programas/assemble_docente.py`: regenera ambos `.mem` desde los Assembly.
- `run_propio_wave.ps1`, `run_docente_wave.ps1` y archivos `.gtkw`/`.vcd`: reproducen e inspeccionan las ondas de C.
- `informe/build_*.py` y `informe/datapath_e2_refinado.png`: fuentes de construcción del informe.
- `resultados/medicion_docente_preliminar.md`: medición intermedia; la comparación consolidada está en `comparacion_codigo.md`.

Los productos compilados `.out`, archivos temporales externos a `EF/` y carpetas anteriores E1/E2 no forman parte del mapa de entrega. No se han borrado ni movido. La checklist viva está en `../memoria/entrega final.md`.

## Antes de subir

1. Crear y exportar `presentacion/Presentacion_Final_Proyecto2_BTB.pdf`.
2. Revisar que presentación e informe citen las mismas cifras y que los diagramas correspondan al RTL.
3. Copiar el conjunto definitivo a una carpeta limpia y ejecutar allí la verificación; confirmar que incluye los archivos de la rúbrica y los PDF.
4. Preparar la exposición de 15 minutos y las preguntas.
