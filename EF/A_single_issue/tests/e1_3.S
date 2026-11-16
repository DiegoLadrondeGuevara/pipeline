addi x1, x0, 25                  # PC=000
sw x1, 96(x0)                    # PC=004
lw x2, 96(x0)                    # PC=008
add x3, x2, x0                   # PC=012
sw x3, 100(x0)                   # PC=016
