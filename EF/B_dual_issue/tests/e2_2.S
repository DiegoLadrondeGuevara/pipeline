addi x1, x0, 25                  # PC=000
addi x2, x0, 4                   # PC=004
sw x1, 96(x0)                    # PC=008
addi x3, x2, 3                   # PC=012
addi x4, x3, 1                   # PC=016
lw x5, 96(x0)                    # PC=020
sw x4, 100(x0)                   # PC=024
sw x5, 104(x0)                   # PC=028
