# C — Dual-Issue con Branch Target Buffer

Esta versión parte de la copia B de E2. El único cambio microarquitectónico de C está en `rtl/btb.v` y la ruta de fetch/control de `rtl/dualissue.v`; la ampliación de memoria de datos para el programa del docente se aplicó por igual a A, B y C.

El BTB tiene 16 entradas de mapeo directo, etiqueta completa de PC, destino y contador saturante de 2 bits. Consulta las dos posiciones de fetch y anticipa el PC cuando una entrada predice salto tomado. En EX se comprueba el siguiente PC real, se actualiza el BTB y solo se hace flush si hubo predicción errónea. Las señales `btb_prediction_count`, `btb_correct_count` y `btb_mispredict_count` permiten medir el efecto. La segunda instrucción no se emite junto a una instrucción de control que predijo un salto tomado.

**Estado:** compila y pasa la prueba unitaria del BTB, los cuatro casos E2, cinco comparaciones E1 y las cuatro etapas del programa del docente mediante `../run_code_checks.ps1`. La aprobación del profesor aún no está documentada. Las waveforms y su análisis quedan para el siguiente paso.
