# Programa propio EF: generar y recorrer 12 datos, con dependencias,
# memoria compartida, branches alternantes y bucles de retorno.
# Entrada: registros y memoria inicializados por el testbench; N=12.
.text
.globl _start
_start:
    addi x1, x0, 1024       # puntero del arreglo
    addi x2, x0, 0          # indice
    addi x3, x0, 12         # cantidad de elementos
    addi x4, x0, 0          # suma durante generacion
    addi x5, x0, 0          # cantidad de valores menores que 9
    addi x6, x0, 0          # cantidad de valores mayores o iguales a 9
    addi x10, x0, 9         # umbral
    addi x13, x0, 1         # true para los branches de retorno

llenar:
    addi x8, x2, 3         # datos 3, 4, ..., 14
    sw x8, 0(x1)
    lw x9, 0(x1)           # dependencia de memoria y Load-Use
    add x4, x4, x9
    slt x11, x9, x10
    beq x11, x0, grande
    addi x5, x5, 1
    jal x0, continuar
grande:
    addi x6, x6, 1
continuar:
    addi x1, x1, 4
    addi x2, x2, 1
    slt x12, x2, x3
    beq x12, x13, llenar

    addi x1, x0, 1024
    addi x2, x0, 0
    addi x14, x0, 0        # suma independiente por segundo recorrido
    addi x16, x0, 0        # hash: h <- 2h + dato
    addi x17, x0, 0        # suma de indices
recorrer:
    lw x9, 0(x1)
    add x14, x14, x9
    add x16, x16, x16
    add x16, x16, x9
    add x17, x17, x2
    addi x1, x1, 4
    addi x2, x2, 1
    slt x12, x2, x3
    beq x12, x13, recorrer

    addi x15, x0, 1200
    sw x4, 0(x15)
    sw x14, 4(x15)
    sw x5, 8(x15)
    sw x6, 12(x15)
    sw x16, 16(x15)
    sw x17, 20(x15)
    addi x18, x0, 1
    sw x18, 24(x15)         # store terminal, fuera del bucle fin
fin:
    jal x0, fin
