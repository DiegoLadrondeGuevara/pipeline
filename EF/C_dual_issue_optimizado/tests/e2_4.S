addi x1, x0, 25                  # PC=000
addi x2, x0, 1                   # PC=004
sw x1, 96(x0)                    # PC=008
lw x3, 96(x0)                    # PC=012
add x4, x3, x2                   # PC=016
sw x4, 100(x0)                   # PC=020
