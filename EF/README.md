# Entrega final — Proyecto 2

El [mapa de archivos para subir](ENTREGA_FINAL.md) y la [checklist de requerimientos y estado](../memoria/entrega%20final.md) son las referencias para cerrar la entrega. El enunciado y la rúbrica oficiales están en la carpeta padre de `pipeline/`.

| Carpeta | Uso | Estado actual |
|---|---|---|
| `A_single_issue/` | Copia independiente del pipeline de E1. | `./run_e1.ps1` pasa. |
| `B_dual_issue/` | Copia independiente de E2, que debe conservarse sin la optimización de C. | `./run_e2.ps1` pasa. |
| `C_dual_issue_optimizado/` | Copia de B con BTB en fetch/control. | Pruebas de código y waveforms del informe completas. |
| `programas/` | Los dos Assembly finales y sus `.mem`, comunes a A/B/C. | Docente y propio verificados. |
| `resultados/` | Evidencia y tabla de las seis corridas. | Comparación de código completa. |
| `informe/` | Informe final PDF y DOCX editable. | Ambas versiones presentes, 14 páginas. |
| `presentacion/` | PDF de la exposición final. | Pendiente de crear. |

Las copias A y B contienen sus pruebas y scripts para que puedan ejecutarse por separado. Los archivos de la raíz y `E2/` se conservan como historial; `E2_LadronDeGuevara_Burgos_Morales_Heredia/` y su ZIP son la entrega anterior archivada. Las ondas `.vcd` producidas al verificar las copias quedan dentro de cada `tests/`.

Para ejecutar las pruebas de código sin generar waveforms:

```powershell
./run_code_checks.ps1
```

Para generar y abrir la waveform del programa propio en C:

```powershell
./run_propio_wave.ps1 -Open
```

La primera vista guiada está en `resultados/waveforms/propio_C_01_load_use.gtkw`.

Para generar y abrir la primera waveform de cierre del programa docente en C:

```powershell
./run_docente_wave.ps1 -Open
```

La vista de etapa A está en `resultados/waveforms/docente_C_01_etapa_A.gtkw`.

Los programas docente y propio están integrados y pasan las seis corridas. La documentación de la optimización está en `BTB_DOCUMENTACION.md`; el informe editable y su PDF están en `informe/`. El equipo confirmó la aprobación verbal del BTB por el profesor en clase. Las siete evidencias del informe están completas; el PDF de presentación sigue pendiente.
