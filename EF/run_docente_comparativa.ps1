$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python programas/assemble_docente.py
    if ($LASTEXITCODE -ne 0) { throw 'Teacher assembly failed' }
    $waveDir = Join-Path $PSScriptRoot 'resultados/waveforms/comparativa_docente'
    New-Item -ItemType Directory -Path $waveDir -Force | Out-Null
    foreach ($item in @(
        @{ Name='A'; Folder='A_single_issue'; Flags=@('-DSINGLE') },
        @{ Name='B'; Folder='B_dual_issue'; Flags=@() },
        @{ Name='C'; Folder='C_dual_issue_optimizado'; Flags=@('-DOPTIMIZED') }
    )) {
        $waveFile = Join-Path $waveDir ("docente_{0}.vcd" -f $item.Name)
        Push-Location $item.Folder
        try {
            $rtl = @(Get-ChildItem rtl -Filter '*.v' | ForEach-Object FullName)
            & iverilog -g2012 -DWAVES @($item.Flags) -s docente_tb -o tests/docente_comparativa.out $rtl ../testbenches/docente_tb.v
            if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $($item.Name)" }
            & vvp tests/docente_comparativa.out '+PROGRAM=../programas/docente.mem' "+VCD=$waveFile"
            if ($LASTEXITCODE -ne 0) { throw "Simulation failed: $($item.Name)" }
        } finally { Pop-Location }
        Write-Output "$($item.Name): $waveFile"
    }
} finally { Pop-Location }
