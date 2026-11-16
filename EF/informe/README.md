# Informe de la entrega final

- `Informe_Final_Proyecto2_BTB_editable.docx`: versión editable, con las capturas e interpretaciones y la redacción revisada en voz del equipo.
- `Informe_Final_Proyecto2_BTB.pdf`: exportación del DOCX revisado.

Ambas versiones tienen 14 páginas. Las secciones 8.1–8.7 contienen las siete evidencias requeridas, interpretaciones y tablas de señales; 8.4 ocupa dos páginas para conservar legibles las tres capturas de la etapa D. La portada conserva el diseño, logo, curso e integrantes de E2; el título se actualizó a «Entrega final» y se retiró la fecha anterior, según la indicación del equipo. El cuerpo incluye la arquitectura, implementación y pruebas del BTB, los dos programas y la comparación de seis corridas. El docente aprobó verbalmente la elección del BTB en clase, según confirmó el equipo.

El informe se renderizó y revisó página por página: no quedan recuadros de waveform ni tablas o figuras cortadas. La presentación PDF es un entregable aparte.

Para regenerar el editable, `build_informe_docx.py` produce el documento base en `tmp/informe_final_raw.docx`; después `revisar_redaccion.py --input tmp/informe_final_raw.docx --output EF/informe/Informe_Final_Proyecto2_BTB_editable.docx` aplica la versión editorial. El PDF final se exporta desde ese DOCX. `build_diagram.py` regenera el diagrama y `build_informe_final.py` conserva el constructor previo del PDF, anterior a esta revisión de redacción.
