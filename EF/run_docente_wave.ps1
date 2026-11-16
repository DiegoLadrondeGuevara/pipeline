param(
    [switch]$Open,
    [ValidateSet('etapa_A','etapa_B','etapa_C','etapa_D')][string]$View = 'etapa_A'
)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python programas/assemble_docente.py
    if ($LASTEXITCODE -ne 0) { throw 'Teacher assembly failed' }

    $waveDir = Join-Path $PSScriptRoot 'resultados/waveforms'
    New-Item -ItemType Directory -Path $waveDir -Force | Out-Null
    $waveFile = Join-Path $waveDir 'docente_C.vcd'

    Push-Location C_dual_issue_optimizado
    try {
        $rtl = @(Get-ChildItem rtl -Filter '*.v' | ForEach-Object FullName)
        & iverilog -g2012 -DOPTIMIZED -DWAVES -s docente_tb -o tests/docente_wave.out $rtl ../testbenches/docente_tb.v
        if ($LASTEXITCODE -ne 0) { throw 'Teacher waveform compile failed' }
        & vvp tests/docente_wave.out "+PROGRAM=../programas/docente.mem" "+VCD=$waveFile"
        if ($LASTEXITCODE -ne 0) { throw 'Teacher waveform simulation failed' }
    } finally { Pop-Location }

    Write-Output "Waveform: $waveFile"
    if ($Open) {
        $viewer = (Get-Command gtkwave -ErrorAction Stop).Source
        $viewName = switch ($View) {
            'etapa_B' { 'docente_C_02_etapa_B.gtkw' }
            'etapa_C' { 'docente_C_03_etapa_C.gtkw' }
            'etapa_D' { 'docente_C_04_etapa_D.gtkw' }
            default { 'docente_C_01_etapa_A.gtkw' }
        }
        $viewFile = Join-Path $waveDir $viewName
        Start-Process -FilePath $viewer -ArgumentList ('"' + $waveFile + '"'), ('"' + $viewFile + '"')
    }
} finally { Pop-Location }
