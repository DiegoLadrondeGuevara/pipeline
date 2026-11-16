# Programas de comparación final

El programa del docente está archivado en `Programa-proyecto-del-docente.pdf`. `docente.S` transcribe sus 90 instrucciones sin cambiar la secuencia; se contrastaron las 90 instrucciones extraídas del PDF con el Assembly. `assemble_docente.py` genera `docente.mem`. La dirección base de datos es 1536 y los estados A–D esperados se verifican en `../testbenches/docente_tb.v`.

`propio.S` es el programa de evaluación del grupo. Genera 12 palabras (3…14) en direcciones 1024…1068 y las recorre dos veces. Guarda siete salidas en 1200…1224: 102, 102, 6, 6, 16368, 66 y 1. `assemble_docente.py --source programas/propio.S --output programas/propio.mem` genera su memoria de instrucciones. El testbench `../testbenches/propio_tb.v` comprueba todas las palabras y salidas. Ambos programas corren sin cambios en A, B y C.
