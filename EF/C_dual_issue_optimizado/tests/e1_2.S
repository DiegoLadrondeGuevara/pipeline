addi x1, x0, 10                  # PC=000
addi x2, x1, 5                   # PC=004
add x3, x2, x1                   # PC=008
sw x3, 96(x0)                    # PC=012
addi x4, x0, 1                   # PC=016
addi x4, x4, 2                   # PC=020
addi x5, x4, 22                  # PC=024
sw x5, 100(x0)                   # PC=028
