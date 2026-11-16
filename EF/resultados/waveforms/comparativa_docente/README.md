# Ondas comparativas del programa docente (A, B y C)

Las tres simulaciones ejecutan el **mismo `docente.mem`**, con reloj de 10 ns y el mismo testbench. Todas pasan los cuatro cierres A–D y retiran 312 instrucciones. Las imágenes se trazaron desde los VCD generados por Icarus Verilog; no son capturas directas de la ventana de GTKWave. Los VCD se incluyen para inspeccionar otras señales o rehacer el encuadre.

| Arquitectura | Configuración | VCD | Imagen para la PPT | Ciclos |
|---|---|---|---|---:|
| A | Pipeline Single-Issue | `docente_A.vcd` | `captura_docente_A_C1.png` | 458 |
| B | Pipeline Dual-Issue de E2 | `docente_B.vcd` | `captura_docente_B_C1.png` | 386 |
| C | Dual-Issue con BTB | `docente_C.vcd` | `captura_docente_C_C1.png` | 320 |

## Qué muestran las tres imágenes

Se eligieron **dos ejecuciones consecutivas del salto de retorno del bucle C1**, en PC `0x7C`, cuyo destino tomado es `0x70`. Los tiempos absolutos difieren porque cada arquitectura llega al salto en un ciclo distinto. Las líneas verticales marcan la resolución de cada retorno en EX; el pulso de `btb_hit1` y `predict1` de C corresponde a la búsqueda anterior de la instrucción, por la latencia del pipeline.

| Arquitectura | Primer retorno | Segundo retorno |
|---|---|---|
| A | 380 ns: siguiente secuencial `0x80`, real `0x70`, redirección `1` | 440 ns: `0x80` frente a `0x70`, redirección `1` |
| B | 280 ns: siguiente secuencial `0x80`, real `0x70`, redirección `1` | 330 ns: `0x80` frente a `0x70`, redirección `1` |
| C | 280 ns: BTB aún no predice ese retorno; `0x80` frente a `0x70`, redirección `1` | 330 ns: BTB predice `0x70`, coincide con el destino real `0x70`, redirección `0` |

En A y B, `PC previsto` es la dirección secuencial `PC+4` calculada por la sonda del testbench para poder comparar; **no representa un predictor implementado**. En C, `PC previsto` es la salida efectiva del BTB. `PC del salto`, `PC previsto`, `PC real` y `redirección` se leen juntos cuando `control en EX=1`. A muestra `avanza ID a EX`, porque no tiene unidad de doble emisión; B y C muestran las instrucciones en ambas vías y las señales `emite vía 0` y `emite vía 1`. `stall por carga` permite reconocer si una pausa proviene de un Load-Use. `x19` indica el índice del bucle y ayuda a reconocer las iteraciones.

El segundo retorno aporta una demostración local del BTB: C evita una redirección que A y B todavía realizan. El ahorro total de 66 ciclos de C frente a B (386 → 320; rapidez relativa `1,2063×`) es el resultado de **todo el programa**, no solo de este salto. B mejora 72 ciclos frente a A (458 → 386; `1,1865×`) mediante la doble emisión, aunque la cantidad de instrucciones retiradas sigue siendo 312.

## Texto breve sugerido para la presentación

> Ejecutamos el programa del docente sin cambiar el Assembly en las tres arquitecturas. En el retorno del bucle C1, A y B calculan `0x80` como siguiente PC secuencial y deben redirigir a `0x70` en ambas iteraciones. C también corrige el primer retorno, pero el BTB aprende su destino: en el segundo predice `0x70` y evita la redirección. En el programa completo, B pasa de 458 a 386 ciclos y C baja a 320, con los mismos 312 retiros y los mismos resultados funcionales.

## Reproducción

Desde `EF/`, con Python, Icarus Verilog y Matplotlib instalados:

```powershell
./run_docente_comparativa.ps1
python resultados/waveforms/comparativa_docente/generar_capturas.py
```

El primer comando recompila A/B/C y genera los VCD. El segundo ubica automáticamente los dos retornos por `branch_pc=0x7C` y `actual_next_pc=0x70`, y crea las tres imágenes. Para comprobar el programa y la equivalencia funcional sin generar ondas, usar `./run_code_checks.ps1`.
