# Guía de objetivos y entregables — Proyecto 2 de Arquitectura de Computadoras

**Actualizada:** 29 de octubre de 2026

**Meta:** obtener el máximo puntaje mediante tres procesadores correctos, pruebas reproducibles y una explicación técnica que demuestre cada criterio de la rúbrica.

**Avance de implementación (29/10/2026):** el pipeline A pasa las cuatro pruebas dirigidas de E1; también pasan el prototipo independiente de Dual Fetch/Dual Decode con dos ALU preliminares y el Register File doble. Ver [estado técnico y reproducción](../E1_IMPLEMENTACION.md). Ya existe un borrador del [informe PDF de E1](../output/pdf/Informe_E1_Proyecto2.pdf); faltan datos del equipo y revisión antes de presentarlo. El prototipo deberá convertirse en el procesador B funcional para E2.

## 1. Qué hay que lograr

Construir y conservar ejecutables tres versiones del mismo procesador:

- **A — Single-Issue:** pipeline RV32I de cinco etapas (IF, ID, EX, MEM, WB), con forwarding, stalls y flushes correctos.
- **B — Dual-Issue In-Order:** hasta dos instrucciones consecutivas por ciclo, dos ALU, hasta cuatro lecturas y dos escrituras del Register File, un puerto de memoria de datos y un recurso de branches compartidos. La Issue Unit decide si emite cero, una o dos instrucciones sin alterar el orden.
- **C — Dual-Issue optimizado:** B más una mejora microarquitectónica adicional, justificada, aprobada por el profesor, implementada y medida.

Las tres versiones deben ejecutar **sin modificar** el programa Assembly propio y el programa entregado por el profesor, con los mismos datos y resultados funcionales. La comparación final incluye instrucciones retiradas, ciclos, IPC, CPI y speedup. El informe y la presentación deben demostrar *por qué* cambian esas métricas, no solo mostrar números.

**Fuentes:** [Enunciado](Proyecto2_Enunciado.pdf), secciones 1–5; [indicaciones y rúbrica](Proyecto2_Indicaciones_Generales_Rubrica.pdf), secciones 1–6. Si el profesor comunica precisiones posteriores, registrarlas aquí con fecha.

## 2. Fechas, puntaje y estrategia

Los PDF indican sesiones, **no fechas de calendario**. Anotar las fechas y horas reales apenas el curso las confirme; las entregas E1, E2 y EF vencen **antes** de la sesión indicada.

| Hito | Plazo oficial | Puntos | Resultado que debe estar listo |
|---|---|---:|---|
| E1 | Antes de sesión 13.1 | 4 | A funcional y verificado; Dual Fetch/Decode y datapath B preliminar; código, `.mem`, testbenches e informe PDF. |
| Trivia 1 | Sesión 13.2 | Hasta +0.5 | Repaso individual del diseño y hazards. |
| E2 | Antes de sesión 14.1 | 4 | B completamente funcional; pruebas de emisión, recursos compartidos, dependencias y branches; informe PDF. |
| Propuesta de optimización | Sesión 14.1 | Requisito sin puntos propios | Presentar al profesor y obtener aprobación de la mejora para C. |
| Trivia 2 | Sesión 14.2 | Hasta +0.5 | Repaso individual de Issue Unit, forwarding, stalls y resultados. |
| EF | Antes de sesión 15.1 | 4 | C funcional; A/B/C reproducibles; dos programas, seis corridas comparables; informe y presentación en PDF. |
| Presentación | Semana 15, horario asignado | 8 | Aproximadamente 15 min de exposición y 5 min de preguntas. |

**Base:** 20 puntos. Las dos trivias permiten hasta +1 punto adicional según la rúbrica. E1 y E2 reservan 1 punto cada una para pregunta individual; la presentación reserva 2 puntos individuales y 1 grupal. Por eso todos los integrantes deben saber explicar código, pruebas y resultados. La entrega tardía descuenta 1 punto; faltar o llegar tarde a una sesión de evaluación descuenta 0.5 o 0.25 puntos individuales, respectivamente. No hay bonificación por adelantar la entrega.

**Fechas reales por completar:** sesión 13.1: ___; 13.2: ___; 14.1: ___; 14.2: ___; 15.1: ___; presentación: ___. **Meta interna recomendada:** cerrar código y pruebas al menos una jornada antes de cada plazo; usar el margen final para reproducir todo desde cero y corregir el informe.

## 3. Diagnóstico del material recibido

En `pipeline/` hay un esqueleto Verilog de procesador segmentado, un testbench y `riscvtest.dat`. Esta inspección es **estática**: aún no se ha compilado ni simulado el diseño.

| Estado observado | Implicación / siguiente objetivo |
|---|---|
| `datapath.v` separa IF, ID, EX, MEM y WB con registros de pipeline. | Sirve como base de A, pero hace falta verificar su comportamiento bajo dependencias y saltos. |
| No aparece un módulo Hazard Unit ni habilitación/retención de PC e IF/ID, burbujas o flush selectivo. Tampoco hay multiplexores de forwarding conectados a operandos de EX. | E1 requiere implementar y probar forwarding, Load-Use stall y flush de control antes de declarar A funcional. |
| `MemWrite` del `controller` de ID sale directamente por `riscvsingle.v`, mientras `DataAdr` y `WriteData` vienen de MEM. | Alinear `MemWrite` con la instrucción en MEM y verificar cada store; es una brecha de corrección prioritaria. |
| `regfile.v` tiene dos puertos de lectura y uno de escritura; `imem.v` entrega una instrucción. | E1 inicia dos fetch/decode; E2 exige hasta cuatro lecturas y dos escrituras y dos vías completas. |
| `imem.v` declara 64 palabras; `riscvtest.dat` contiene 84 líneas. | Ajustar capacidad/carga y comprobar que no se truncan programas. |
| El testbench actual termina al ver una escritura esperada en memoria, sin cubrir los cuatro programas E1 ni una matriz de hazards. | Crear pruebas dirigidas con resultados esperados, tiempo límite y trazas explicadas. |
| El decodificador visible soporta `lw`, `sw`, R-type limitado, `beq`, I-type ALU limitado y `jal`; no implementa toda RV32I. | Definir y documentar el conjunto exacto que se probará. Confirmar con el profesor el alcance esperado y asegurar que ambos programas finales corran en A/B/C. |

**Regla de avance:** no dar por completado un bloque solo porque compila. Debe pasar una prueba que falle si esa función está incorrecta y quedar evidencia clara en el informe.

## 4. Plan de trabajo por entrega

### E1 — Pipeline funcional y comienzo Dual-Issue (4 puntos)

**Objetivo técnico:** terminar A como referencia confiable y dejar visible la primera estructura de B. En E1 **no se exige** ejecutar dos instrucciones a la vez.

1. **Cerrar la especificación de A.** Listar instrucciones soportadas, efecto sobre registros/memoria/PC, tratamiento de `x0`, reset y fin de programa. Corregir la alineación de controles por etapa, especialmente `MemWrite`.
2. **Implementar Hazard Unit.** Comparar registros fuente/destino válidos; priorizar el productor más reciente; llevar datos desde MEM/WB a EX; introducir burbuja en Load-Use; retener PC e IF/ID cuando corresponda; anular instrucciones jóvenes al tomar un branch o jump. Probar que una instrucción anulada jamás escribe registro o memoria.
3. **Crear cuatro programas independientes y sus testbenches:** (P1) ISA soportada sin dependencias que requieran Hazard Unit; (P2) forwarding; (P3) stall Load-Use; (P4) flushing por cambio de flujo. Cada uno debe declarar estado final esperado, observar señales internas relevantes y terminar por éxito o timeout.
4. **Iniciar B.** Fetch de dos instrucciones consecutivas, Decode de ambas y primeros módulos/registros de la segunda vía. Mostrar con waveforms dos PC/instrucciones correctos y un datapath preliminar coherente. Mantener claro qué parte de B es solo preliminar.
5. **Preparar el informe PDF.** Diagrama de A, explicación de pipeline/control/Hazard Unit, cambios de IF/ID para B y diagrama preliminar de B. Para cada P1–P4: propósito, secuencia clave, waveform rotulada, señales y valores intermedios, resultado esperado y observado, interpretación.

| Rúbrica E1 | Puntos | Evidencia mínima para defenderlos |
|---|---:|---|
| Pipeline RV32I funcional con Hazard Unit | 1.25 | P1–P4 pasan; trazas de forwarding, stall y flush; stores y WB correctos. |
| Dual Fetch y Dual Decode | 0.75 | Dos instrucciones/PC consecutivos visibles y decodificados correctamente. |
| Datapath Dual-Issue preliminar | 0.50 | Diagrama y código de segunda vía inicial consistentes. |
| Programas, waveforms y resultados | 0.50 | Cuatro `.mem` y testbenches; capturas interpretadas y resultados verificables. |
| Pregunta individual | 1.00 | Cada integrante explica una traza ciclo por ciclo. |

**Puerta de salida E1:** una ejecución limpia de las cuatro pruebas desde los archivos entregados, sin editar código ni memoria entre corridas salvo seleccionar el caso; informe coherente con la versión exacta del código.

### E2 — Dual-Issue funcional (4 puntos)

**Objetivo técnico:** B debe ejecutar programas correctos y emitir dos instrucciones independientes cuando sea posible.

1. **Formalizar el contrato de emisión.** Identificar instrucción antigua/joven, fuentes realmente leídas, destino escrito, tipo ALU/memoria/branch, `valid` y PC. Emitir dos solo si no hay RAW irresoluble, conflicto de recursos ni hazard anterior pendiente. Si solo sale la antigua, guardar la joven y reagruparla con la siguiente sin perder ni repetir instrucciones.
2. **Completar las dos vías.** Dos ALU y registros IF/ID, ID/EX, EX/MEM y MEM/WB por vía según hagan falta; hasta cuatro lecturas y dos escrituras por ciclo; semántica definida para dos escrituras y prioridad del productor más joven cuando ambos escriban el mismo destino, siempre respetando el orden del programa.
3. **Compartir recursos.** Un único acceso a memoria de datos y un único recurso de branch por ciclo. Permitir ALU + Load/Store en ambos órdenes del par; separar dos operaciones de memoria. Probar la selección de vía y del recurso, no asumir que la instrucción de memoria siempre ocupa una posición fija.
4. **Extender hazards y forwarding.** Cubrir productores/consumidores entre vías y etapas, Load-Use, RAW dentro del par, stalls y colisiones estructurales. En cada decisión de forwarding, elegir el resultado válido más reciente. Mantener `valid` para que burbujas y flushes no cuenten como instrucciones retiradas ni produzcan efectos.
5. **Resolver control.** Branch/jump en posición 1 o 2, tomado y no tomado. Si el de posición 1 se toma, anular la joven incorrecta; si el de posición 2 se toma, conservar la antigua. Actualizar PC y limpiar solo las instrucciones más jóvenes del camino erróneo.
6. **Medir una comparación preliminar A vs B.** Definir punto común de inicio y fin, contar instrucciones retiradas y ciclos, calcular IPC y conservar el programa exacto usado.
7. **Preparar informe PDF y demo.** Datapath B completo, Controller, Issue Unit con tabla de condiciones, reagrupamiento, forwarding/hazards/stalls, branches, waveforms interpretadas y comparación preliminar.

**Matriz mínima de pruebas E2:** dos ALU independientes; RAW entre candidatas; forwarding de cada vía desde MEM/WB; Load-Use; dos memorias en un par; ALU+memoria y memoria+ALU; dos escrituras simultáneas (incluido mismo `rd` y `x0`); branch en ambas posiciones tomado/no tomado; emisión parcial seguida de reagrupamiento; stall de cero emisiones; flush con side effects prohibidos; comparación de registros y memoria finales contra A. Cada caso debe incluir PC/orden de las instrucciones, emisión por vía, stalls/flushes y estado esperado.

| Rúbrica E2 | Puntos | Evidencia mínima para defenderlos |
|---|---:|---|
| Datapath e Issue Unit | 0.75 | Dos vías, doble emisión real y reagrupamiento correcto. |
| Forwarding, hazards y stalls | 1.00 | Matriz de dependencias y trazas con prioridad y burbujas correctas. |
| Memoria, branches y flushing | 0.75 | Un puerto/branch compartidos; casos en ambas posiciones sin efectos incorrectos. |
| Programas, waveforms y resultados | 0.50 | Testbenches repetibles, resultados intermedios y A vs B preliminar. |
| Pregunta individual | 1.00 | Cada integrante razona reglas de emisión y un caso difícil. |

**Puerta de salida E2:** B pasa toda la matriz, produce el mismo estado arquitectónico que A y demuestra al menos un ciclo de doble emisión. Guardar esta versión como **B sin optimización** antes de empezar C.

### Propuesta de optimización — sesión 14.1

Preparar una ficha breve para el profesor y pedir su aprobación **antes de implementar C**:

| Campo | Qué presentar |
|---|---|
| Nombre | Una mejora concreta, distinta de los requisitos obligatorios de E2. |
| Limitación medida | Dato de B que muestre el cuello de botella: stalls, doble emisión desperdiciada, branches, memoria, etc. |
| Cambio de hardware | Qué se añade o modifica en datapath/control y qué módulos toca. |
| Hipótesis | En qué programa o patrón debería ayudar y cuál es el costo esperado. |
| Métrica | IPC/ciclos más una métrica propia de la mejora. |
| Validación | Casos funcionales nuevos y comparación B vs C con mismo programa y entradas. |

Opciones permitidas por el enunciado: predictor de branches de 2 bits, BTB, instruction queue, política de issue **más allá** de lo obligatorio, forwarding adicional, caché o mejora extra de memoria. Elegir después de medir B. Una secuencia Assembly mejorada por sí sola no cuenta como optimización microarquitectónica. Registrar la aprobación y cualquier condición del profesor.

### EF — Optimización y evaluación final (4 puntos)

1. **Implementar C sin romper B.** Mantener A, B y C compilables por separado, con instrucciones y datos iguales. Probar la función nueva, los casos límite y la regresión completa de E1/E2.
2. **Desarrollar un programa Assembly propio no trivial.** Debe mezclar paralelismo, dependencias, memoria y control suficientes para explicar cuándo B emite dos y cuándo la optimización ayuda o no. Documentar algoritmo, entrada, salida esperada y razonamiento del patrón de instrucciones. Ejecutar también el programa del profesor cuando se reciba.
3. **Correr seis experimentos comparables:** 2 programas × A/B/C. Usar mismo criterio de inicio/fin y mismas entradas. Verificar equivalencia de registros/memoria/salida antes de aceptar métricas. Contar instrucciones retiradas reales (excluir burbujas, instrucciones anuladas y fetch no retirado).
4. **Calcular y explicar:** `IPC = retiradas / ciclos`; `CPI = ciclos / retiradas`; `speedup respecto a A = ciclos_A / ciclos_config`; `speedup respecto a B = ciclos_B / ciclos_config`, suponiendo igual período de reloj. Si las frecuencias difieren, comparar además tiempo real. Reportar métricas específicas de C y, si sirve, stalls y porcentaje de doble emisión.
5. **Cerrar informe y presentación en PDF.** Justificación, hardware modificado, diagramas actualizados, pruebas/waveforms, programa propio, programa del profesor, tabla de seis corridas, beneficios, límites y conclusiones respaldadas por mediciones.

| Rúbrica EF | Puntos | Evidencia mínima para defenderlos |
|---|---:|---|
| Justificación y diseño de la optimización | 0.75 | Cuello de botella de B, propuesta aprobada y diagramas. |
| Implementación funcional | 1.75 | C funciona, conserva equivalencia y el cambio está integrado. |
| Testbenches y validación | 0.75 | Pruebas específicas y regresión A/B/C. |
| Comparación cuantitativa y análisis | 0.75 | Seis corridas, métricas calculadas correctamente e interpretación. |

**Archivos EF obligatorios:** Verilog de A/B/C, `.mem`, ambos Assembly, testbenches, informe PDF y presentación PDF. Incluir instrucciones de ejecución y los resultados esperados para que el profesor reproduzca la comparación.

## 5. Presentación final (8 puntos)

**Guion sugerido para ~15 minutos:** 2 min objetivo y A; 4 min arquitectura B/Issue Unit/recursos; 3 min demostración de doble emisión, reagrupamiento y hazards; 3 min C (motivación, cambio, prueba); 2 min comparación A/B/C; 1 min conclusiones y límites. Reservar la demo más simple y sólida para el tiempo disponible; llevar capturas/waveforms de respaldo.

| Criterio | Puntos | Preparación |
|---|---:|---|
| Arquitectura Dual-Issue | 1.50 | Diagrama legible y recorrido de una pareja de instrucciones. |
| Funcionamiento y hazards | 1.50 | Demo de emisión, stall, forwarding, reagrupamiento y flush. |
| Optimización y resultados | 1.50 | Problema medido, hardware, pruebas y efecto observado. |
| Conclusiones y rendimiento | 0.50 | Explicar IPC < 2, speedups y casos en que C no ayuda. |
| Pregunta grupal | 1.00 | Respuesta consistente basada en señales y datos. |
| Preguntas individuales | 2.00 | Todos dominan A/B/C, código, pruebas y números. |

Preparar una ronda de preguntas entre integrantes: qué sucede ciclo a ciclo en Load-Use; cuándo se conserva la instrucción joven; prioridad entre productores; branch tomado en posición 1 frente a 2; por qué una configuración puede tener menos IPC o más ciclos; cómo se contaron retiradas y ciclos.

## 6. Sistema de evidencia y control de calidad

Para cada prueba guardar: fuente Assembly, `.mem` generado, testbench, comando de compilación/ejecución, resultado esperado, salida observada y waveform. En el informe, cada captura debe señalar PC, instrucciones/`valid` por vía y etapa, `issue`, `stall`, `flush`, `forward`, `rd`/escritura y memoria cuando aplique, con una explicación breve del instante decisivo. Los PDF piden resultados intermedios y waveforms interpretadas; una captura sin interpretación no basta.

**Tabla maestra de experimentos** (completar con datos reales):

| Programa | Config. | Resultado final correcto | Retiradas | Ciclos | IPC | CPI | Speedup vs A | Speedup vs B | Métrica de C |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Propio | A |  |  |  |  |  | 1.00 | — | — |
| Propio | B |  |  |  |  |  |  | 1.00 | — |
| Propio | C |  |  |  |  |  |  |  |  |
| Profesor | A |  |  |  |  |  | 1.00 | — | — |
| Profesor | B |  |  |  |  |  |  | 1.00 | — |
| Profesor | C |  |  |  |  |  |  |  |  |

**Checklist antes de subir cada entrega:**

- [ ] El código compila desde la carpeta entregada y todas las pruebas terminan por éxito o error explícito, nunca por espera indefinida.
- [ ] Los `.mem` corresponden al Assembly y caben en la memoria de instrucciones.
- [ ] La versión de los diagramas, señales y cifras coincide con el código entregado.
- [ ] Cada criterio de la rúbrica tiene una prueba, figura o explicación localizable.
- [ ] Los resultados funcionales se contrastaron contra valores esperados; en EF, también entre A/B/C.
- [ ] El informe PDF se revisó visualmente y sus waveforms son legibles.
- [ ] Se hizo una reproducción final desde una copia limpia de los archivos de entrega.
- [ ] Cada integrante puede defender una decisión de arquitectura, un hazard y una cifra de rendimiento.

## 7. Orden inmediato recomendado

1. Confirmar calendario real de sesiones, integrantes, herramienta de simulación y alcance ISA esperado por el profesor.
2. Congelar una copia del código base y preparar la estructura A/B/C con un comando reproducible para pruebas.
3. Corregir `MemWrite` y capacidad de memoria; construir las cuatro pruebas E1 y la Hazard Unit de A.
4. Una vez A pase, implementar Dual Fetch/Decode y dibujar el datapath preliminar para E1.
5. Antes de avanzar a B, definir en una tabla las reglas de emisión, `valid`, edad de instrucciones, prioridad de forwarding, memoria y branches; esa tabla será la especificación de E2 y la base de sus testbenches.

**Decisión pendiente importante:** los documentos no convierten las sesiones 13.1/14.1/15.1 a fechas concretas, y el código visible implementa solo una parte de RV32I. Resolver ambos puntos con el cronograma y las indicaciones del profesor; no asumirlos silenciosamente.
