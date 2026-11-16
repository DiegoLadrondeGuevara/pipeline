$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python programas/assemble_docente.py
    if ($LASTEXITCODE -ne 0) { throw 'Teacher assembly failed' }
    python programas/assemble_docente.py --source programas/propio.S --output programas/propio.mem
    if ($LASTEXITCODE -ne 0) { throw 'Own program assembly failed' }
    $iverilog = (Get-Command iverilog -ErrorAction Stop).Source
    $vvp = (Get-Command vvp -ErrorAction Stop).Source

    foreach ($arch in @('A_single_issue','B_dual_issue','C_dual_issue_optimizado')) {
        Push-Location $arch
        try {
            $rtl = @(Get-ChildItem rtl -Filter '*.v' | ForEach-Object FullName)
            $flags = @()
            if ($arch -eq 'A_single_issue') { $flags += '-DSINGLE' }
            if ($arch -eq 'C_dual_issue_optimizado') { $flags += '-DOPTIMIZED' }
            & $iverilog -g2012 @flags -s docente_tb -o tests/docente_tb.out $rtl ../testbenches/docente_tb.v
            if ($LASTEXITCODE -ne 0) { throw "Compile failed: $arch teacher" }
            & $vvp tests/docente_tb.out '+PROGRAM=../programas/docente.mem'
            if ($LASTEXITCODE -ne 0) { throw "Simulation failed: $arch teacher" }
            & $iverilog -g2012 @flags -s propio_tb -o tests/propio_tb.out $rtl ../testbenches/propio_tb.v
            if ($LASTEXITCODE -ne 0) { throw "Compile failed: $arch own program" }
            & $vvp tests/propio_tb.out '+PROGRAM=../programas/propio.mem'
            if ($LASTEXITCODE -ne 0) { throw "Simulation failed: $arch own program" }
        } finally { Pop-Location }
    }

    Push-Location C_dual_issue_optimizado
    try {
        $rtl = @(Get-ChildItem rtl -Filter '*.v' | ForEach-Object FullName)
        & $iverilog -g2012 -s btb_tb -o tests/btb_tb.out rtl/btb.v testbenches/btb_tb.v
        if ($LASTEXITCODE -ne 0) { throw 'BTB unit compile failed' }
        & $vvp tests/btb_tb.out
        if ($LASTEXITCODE -ne 0) { throw 'BTB unit test failed' }

        & $iverilog -g2012 -DNO_WAVE -s e2_tb -o tests/e2_no_wave.out $rtl testbenches/e2_tb.v
        if ($LASTEXITCODE -ne 0) { throw 'E2 regression compile failed' }
        foreach ($case in 1..4) {
            & $vvp tests/e2_no_wave.out "+PROGRAM=tests/e2_$case.mem" "+CASE=$case"
            if ($LASTEXITCODE -ne 0) { throw "E2 regression failed: case $case" }
        }

        & $iverilog -g2012 -s e2_equiv_tb -o tests/e2_equiv_no_wave.out $rtl testbenches/e2_equiv_tb.v
        if ($LASTEXITCODE -ne 0) { throw 'E1 equivalence compile failed' }
        foreach ($program in @('e1_1','e1_2','e1_3','e1_4','e1_isa_ext')) {
            & $vvp tests/e2_equiv_no_wave.out "+PROGRAM=tests/$program.mem"
            if ($LASTEXITCODE -ne 0) { throw "E1 equivalence failed: $program" }
        }
    } finally { Pop-Location }

    Write-Output 'PASS all code checks; no waveforms generated'
} finally { Pop-Location }
