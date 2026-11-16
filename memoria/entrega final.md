# Requerimientos y estado de la entrega final (EF)

**Actualizado:** 16 de noviembre de 2026. **Estado:** A/B/C pasan ambos programas y la comparación de seis corridas; C incluye un BTB probado a nivel de código. El equipo confirma aprobación verbal del BTB en clase. Las siete evidencias de waveforms están interpretadas en el informe (tres del propio y cierres A–D del docente); falta la presentación PDF y la revisión final del paquete.

## Fuentes y alcance

- [Enunciado oficial](../../Proyecto2_Enunciado.pdf), secciones 1–5.
- [Indicaciones generales y rúbrica](../../Proyecto2_Indicaciones_Generales_Rubrica.pdf), secciones 1 y 4–6.
- [Guía previa del proyecto](../../GUIA_OBJETIVOS_PROYECTO2.md), útil como plan, pero subordinada a los PDF oficiales.
- [Programa y pautas adicionales del docente](../EF/programas/Programa-proyecto-del-docente.pdf), páginas 1–4: programa de cuatro etapas, estados esperados, cierre en `fin`, waveforms y medición sin el bucle final.

**Aclaración clave:** no se piden tres programas distintos. Se piden **tres versiones ejecutables del procesador**: A (pipeline Single-Issue), B (Dual-Issue In-Order sin optimización) y C (Dual-Issue con una optimización microarquitectónica adicional y aprobada). Deben ejecutar **dos programas Assembly iguales en las tres versiones**: uno propio y otro proporcionado por el profesor. Esto produce **seis corridas** de evaluación.

## Entrega exigida por la rúbrica

- [x] **A — Single-Issue:** código Verilog del pipeline RV32I de cinco etapas (IF, ID, EX, MEM, WB), separado en `EF/A_single_issue/`; pasa E1 y ambos programas finales.
- [x] **B — Dual-Issue:** código Verilog del procesador de E2, in-order, con dos vías, dos ALU, Issue Unit y recursos de memoria/branch compartidos; copia independiente sin optimización en `EF/B_dual_issue/`; pasa E2 y ambos programas finales.
- [x] **C — Dual-Issue optimizado:** BTB de 16 entradas, dos consultas por ciclo, destino y contador de 2 bits; se integra en fetch/control de la copia B y conserva el resultado de ambos programas y la regresión E2. Las waveforms de la optimización están en la sección 8.7 del informe.
- [x] Registrar elección y diseño de la optimización: **Branch Target Buffer** para anticipar destinos de saltos repetidos y reducir el flush por branches tomados. Solo cambian `C/rtl/dualissue.v` y el nuevo `C/rtl/btb.v` frente a B, aparte de ampliar la memoria de datos por igual en A/B/C. Métricas: ciclos, IPC, predicciones de salto tomado, decisiones de control correctas y fallidas.
- [x] **Aprobación previa del profesor:** el equipo confirma que el docente aprobó verbalmente el Branch Target Buffer en clase y pidió implementarlo. No se proporcionó fecha exacta ni constancia escrita; no inventarlas en el informe.
- [x] Programa Assembly propio **no trivial** en `EF/programas/propio.S` y `propio.mem`: genera y recorre 12 datos, usa Load-Use, memoria, branches y bucles; comprueba siete salidas y los 12 datos generados. Su algoritmo y resultados se explican en `EF/BTB_DOCUMENTACION.md` y el informe.
- [x] Programa Assembly del profesor: PDF original copiado a `EF/programas/`, fuente `docente.S` transcrita sin cambios de secuencia y `.mem` generado por `assemble_docente.py`. Dirección base `x1=1536`; los valores esperados de las etapas A–D se comprueban en `EF/testbenches/docente_tb.v`.
- [x] **Programa del docente** ejecutado sin cambios en A/B/C: las cuatro etapas y el estado final coinciden; 312 instrucciones retiradas antes de `fin` en cada versión. El script de regresión no genera waveforms; las capturas de C se generaron con `run_docente_wave.ps1`.
- [x] Ejecutar ambos programas **sin cambios** sobre A, B y C, con los mismos datos de entrada y condiciones de inicio/fin comparables.
- [x] Verificar equivalencia funcional: estados A–D del docente y arreglo/salidas del propio coinciden en A/B/C.
- [x] Para las seis corridas, reportar **instrucciones retiradas, ciclos, IPC, CPI y speedup** en `EF/resultados/comparacion_codigo.md` y el informe. `IPC = retiradas/ciclos`, `CPI = ciclos/retiradas`, `speedup vs A = ciclos_A/ciclos_config`, `speedup vs B = ciclos_B/ciclos_config`, suponiendo igual período de reloj. No se ha medido frecuencia de síntesis.
- [x] Registrar contadores de BTB, stalls Load-Use, doble emisión y emisión parcial en ambos programas.
- [x] Explicar con mediciones por qué B mejora frente a A, por qué IPC no llega a 2 y cómo C reduce ciclos pese a menos ciclos de doble emisión. Conclusión limitada a los dos programas y períodos de reloj iguales.
- [ ] Entregar **Verilog de A/B/C, programas Assembly, archivos `.mem`, testbenches, informe final PDF y presentación final PDF**. Todo salvo la presentación PDF está localizado en el [mapa de entrega](../EF/ENTREGA_FINAL.md). Las tres versiones pasan la regresión actual; falta comprobar el paquete definitivo una vez añadida la presentación.

## Pruebas y evidencia necesarias

- [x] Regresión existente de A y B reproducida desde `EF/`, pruebas específicas del BTB, regresión E2 en C y ambos programas finales; `EF/run_code_checks.ps1` pasa sin producir waveforms.
- [x] Verificar emisión simultánea de instrucciones independientes, RAW, forwarding entre vías y etapas, Load-Use/stalls y conflictos estructurales. `EF/C_dual_issue_optimizado/testbenches/e2_tb.v` comprueba eventos y resultados en los casos 1, 2 y 4; `run_code_checks.ps1` los pasó el 16/11/2026. Las secciones 8.5 y 8.6 muestran ejemplos en ondas.
- [x] Verificar memoria compartida, ALU + Load/Store en ambos órdenes, dos escrituras de registros y conservación/reagrupamiento de la instrucción joven tras emisión parcial. Los casos E2 1 y 2 observan doble emisión, selección de memoria en ambas vías, dos escrituras (incluido mismo destino) y secuencia exacta de PC retirados. Las waveforms 8.5 y 8.6 ilustran emisión parcial y memoria.
- [x] Verificar branches tomados y no tomados en ambas posiciones, PC y flush de instrucciones jóvenes sin efectos indebidos. El caso E2 3 exige los cuatro tipos de branch, orden de retiro y ausencia de stores del camino anulado; C pasa la regresión.
- [x] Guardar waveforms legibles con señales y resultados intermedios; **interpretarlas** en el informe, no solo insertar capturas. Las siete evidencias fueron proporcionadas por el equipo y se incorporaron en 8.1–8.7 con párrafos y tablas. El cierre D usa tres capturas consecutivas.
- [x] Según el PDF del docente, capturar el **cierre de cada etapa A–D** (individual o consolidado), señal de comprobación del testbench y registros/memoria que demuestran el resultado. Las cuatro etapas aparecen en 8.1–8.4 con `checkpoint_passed` y estado comprobado.
- [x] Capturar **al menos dos casos clave adicionales** (RAW, Load-Use, conflicto de memoria, stall o doble emisión), con instrucciones y explicación ciclo a ciclo. RAW/Load-Use está en 8.5; conflicto de memoria y doble emisión en 8.6; BTB en 8.7.
- [x] Preparar ondas comparables del **programa docente en A/B/C** para la presentación. `EF/run_docente_comparativa.ps1` generó tres VCD y `EF/resultados/waveforms/comparativa_docente/` contiene tres imágenes interpretadas del retorno C1: A/B redirigen en las dos iteraciones; C acierta con el BTB en la segunda. Las tres corridas pasaron los cuatro cierres A–D el 16/11/2026.
- [x] Reproducir las seis corridas con `EF/run_code_checks.ps1`, sin editar programas entre configuraciones.
- [ ] Repetir la verificación final desde una **copia limpia del paquete definitivo** cuando se añada la presentación PDF, y comprobar que todos los archivos requeridos estén incluidos. Las waveforms y el informe ya están cerrados.

## Informe final y presentación

- [x] **Informe editable y PDF preparados:** `EF/informe/Informe_Final_Proyecto2_BTB_editable.docx` y `EF/informe/Informe_Final_Proyecto2_BTB.pdf`, 14 páginas, portada basada en E2 con título actualizado a entrega final y sin la fecha E2; arquitectura E2 y adición BTB, dos programas, seis corridas, análisis y siete evidencias interpretadas. El DOCX se renderizó y revisó visualmente.
- [x] Completar el informe PDF con **waveforms propias anotadas e interpretadas** de C y de los casos del docente; revisar las cifras y conclusiones tras incorporarlas. No quedan recuadros pendientes; ambas versiones tienen 14 páginas y las seis corridas se volvieron a verificar con `run_code_checks.ps1`.
- [ ] **Crear y exportar la presentación PDF:** arquitectura A/B, datapath B, Controller, Issue Unit, forwarding, hazards, stalls y flush; demostración de doble emisión y reagrupamiento; motivación/implementación/resultados de C; ambos programas, equivalencia y comparación cuantitativa. Las tres imágenes comparativas del docente ya están listas en `EF/resultados/waveforms/comparativa_docente/`; no existe todavía el archivo de presentación en `EF/`.
- [ ] Preparar exposición de aproximadamente **15 minutos** y **5 minutos** de preguntas; todos los integrantes deben poder explicar arquitectura, código, pruebas y resultados.
- [ ] Hacer una revisión cruzada final de informe, presentación, diagramas, cifras y código cuando exista la presentación. El informe actual ya contiene las capturas, pero la revisión conjunta de ambos PDF aún no es posible.

## Rúbrica EF (4 puntos) y presentación (8 puntos)

| Criterio EF | Puntos | Evidencia a localizar |
|---|---:|---|
| Justificación y diseño de C | 0.75 | Limitación medida, mejora aprobada, diseño y diagramas. |
| Implementación funcional | 1.75 | C integrado y resultado equivalente a A/B. |
| Testbenches y validación | 0.75 | Pruebas específicas, regresión y waveforms interpretadas. |
| Comparación cuantitativa y análisis | 0.75 | Seis corridas, métricas y explicación. |

| Criterio de presentación | Puntos |
|---|---:|
| Arquitectura Dual-Issue | 1.50 |
| Funcionamiento y hazards | 1.50 |
| Optimización y resultados | 1.50 |
| Conclusiones y rendimiento | 0.50 |
| Pregunta grupal | 1.00 |
| Preguntas individuales | 2.00 |

**Plazo oficial:** EF antes de la sesión **15.1**; presentación en semana 15, horario asignado. Los PDF no indican fecha ni hora de calendario. Entrega tardía: −1 punto según la rúbrica.

## Estado actual del repositorio EF

| Elemento | Estado observado | Próxima acción |
|---|---|---|
| A | Copia independiente en `EF/A_single_issue/`; pasan E1, docente y propio. Memoria de datos de 512 palabras. | Conservar para evidencia final. |
| B | Copia independiente en `EF/B_dual_issue/`; pasan E2, docente y propio. Sigue sin optimización. | Conservar para evidencia final. |
| C | Copia de B con BTB en `EF/C_dual_issue_optimizado/`; pasan unidad BTB, casos E2, equivalencia E1 y ambos programas finales. | Conservar código y evidencia para el paquete. |
| Programa propio EF | `EF/programas/propio.S` y `.mem`; dos bucles y salidas verificadas en A/B/C. | Conservar las capturas 8.5–8.7 del informe. |
| Programa del profesor | PDF, `docente.S` y `docente.mem` en `EF/programas/`. Las etapas A–D pasan en A/B/C. | Conservar las capturas 8.1–8.4 del informe. |
| Informe/presentación EF | Informe DOCX editable y PDF de 14 páginas en `EF/informe/`, con siete evidencias interpretadas; presentación PDF aún no creada. | Crear y exportar presentación; después revisar el paquete completo. |
| E2 de entrega anterior | Hay además `E2_LadronDeGuevara_Burgos_Morales_Heredia/` y su `.zip` en la raíz. | Conservarlos como archivo de entrega, sin mezclarlos con B de EF. |

Hay cambios locales previos en `E2/` (README, informe y archivos de ondas). **No sobrescribir ni borrar** esos cambios al organizar EF.

## Estructura actual de EF

```text
pipeline/
  memoria/entrega final.md       # esta checklist viva
  EF/
    A_single_issue/             # copia independiente del código y pruebas de A
    B_dual_issue/               # copia independiente de B sin optimización
    C_dual_issue_optimizado/    # trabajo de C, separado de B
    programas/                  # Assembly y .mem finales compartidos
    resultados/                 # datos, waveforms y métricas de seis corridas
    informe/                    # informe PDF y DOCX editable
    presentacion/               # PDF de exposición pendiente
```

Las carpetas originales de E1/E2 quedan como historial. A/B/C están verificados con **ambos** programas EF por testbenches; las waveforms de C se generaron aparte. El [mapa de entrega](../EF/ENTREGA_FINAL.md) distingue los archivos obligatorios de los materiales de reproducción. La checklist se actualiza con fecha, comando, resultado y evidencia al cerrar cada punto.

### Verificación de la preparación (16/11/2026)

| Copia | Comando desde su carpeta | Resultado observado | Límite de la evidencia |
|---|---|---|---|
| A | `./run_e1.ps1` | PASS el 16/11/2026 en 4 programas E1, Dual Fetch/Decode preliminar, Register File doble y caso ISA extendido (7 verificaciones). | Son pruebas de E1, además de los dos benchmarks finales ejecutados por el script EF. |
| B | `./run_e2.ps1` | PASS el 16/11/2026 en 4 casos E2, equivalencia A/B en 5 programas E1 y benchmark preliminar `e1_2.mem` (10 verificaciones). | La medición preliminar no sustituye las seis corridas EF ejecutadas por el script central. |

### Avance de código BTB y programa del docente (16/11/2026)

- `EF/run_code_checks.ps1` regenera `docente.mem` y pasa los cuatro checkpoints A–D en A, B y C, la prueba unitaria del BTB, cuatro casos E2 y cinco comparaciones E1 en C. No genera `.vcd`.
- El programa tiene 90 instrucciones estáticas, `fin` en PC 356 y 312 instrucciones dinámicas retiradas antes de ese bucle. Los tres procesadores terminan con los estados de referencia del PDF.
- [Medición preliminar sin waveforms](../EF/resultados/medicion_docente_preliminar.md): 458 ciclos A, 386 B, 320 C, con el mismo inicio y fin. Excluyendo incluso la primera resolución de `fin`, C registra 63 predicciones de salto tomado, 57 decisiones de control correctas y 32 correcciones (89 controles previos a `fin`). La tabla consolidada con ambos programas aparece abajo.

### Programa propio e informe (16/11/2026)

- `EF/programas/propio.S` tiene 45 instrucciones estáticas; el testbench comprueba 12 palabras generadas (3…14), sumas 102/102, conteos 6/6, hash 16368, suma de índices 66 y marcador 1. A/B/C retiran 268 instrucciones dinámicas.
- La [tabla consolidada de seis corridas](../EF/resultados/comparacion_codigo.md) registra 363/288/233 ciclos A/B/C en el propio y 458/386/320 en el docente; los estados funcionales coinciden.
- [Documentación técnica del BTB](../EF/BTB_DOCUMENTACION.md) describe tabla, política, integración mínima a E2, validación, análisis y límites.
- La portada conserva el diseño, logo, curso e integrantes de E2; por instrucción posterior del equipo, el título cambia a **Entrega final** y se elimina la fecha de E2. El informe dedica ocho páginas a siete evidencias: 8.1–8.7 contienen capturas reales aportadas por el equipo, con interpretaciones y tablas. La etapa D ocupa dos páginas y tres capturas para conservar legibilidad. Las capturas corresponden al programa propio y al docente, ejecutados en C.

## Datos externos pendientes

- [ ] Fecha/hora concretas de la sesión 15.1 y de la presentación.
- [x] Confirmación del equipo de que el profesor aprobó verbalmente el **Branch Target Buffer** en clase; fecha exacta no indicada.

