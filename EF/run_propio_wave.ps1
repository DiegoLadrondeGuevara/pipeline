param(
    [switch]$Open,
    [ValidateSet('load_use','memoria','btb')][string]$View = 'load_use'
)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python programas/assemble_docente.py --source programas/propio.S --output programas/propio.mem
    if ($LASTEXITCODE -ne 0) { throw 'Own program assembly failed' }

    $waveDir = Join-Path $PSScriptRoot 'resultados/waveforms'
    New-Item -ItemType Directory -Path $waveDir -Force | Out-Null
    $waveFile = Join-Path $waveDir 'propio_C.vcd'

    Push-Location C_dual_issue_optimizado
    try {
        $rtl = @(Get-ChildItem rtl -Filter '*.v' | ForEach-Object FullName)
        & iverilog -g2012 -DOPTIMIZED -DWAVES -s propio_tb -o tests/propio_wave.out $rtl ../testbenches/propio_tb.v
        if ($LASTEXITCODE -ne 0) { throw 'Waveform compile failed' }
        & vvp tests/propio_wave.out "+PROGRAM=../programas/propio.mem" "+VCD=$waveFile"
        if ($LASTEXITCODE -ne 0) { throw 'Waveform simulation failed' }
    } finally { Pop-Location }

    Write-Output "Waveform: $waveFile"
    if ($Open) {
        $viewer = (Get-Command gtkwave -ErrorAction Stop).Source
        $viewName = switch ($View) {
            'memoria' { 'propio_C_02_memoria_emision.gtkw' }
            'btb' { 'propio_C_03_btb.gtkw' }
            default { 'propio_C_01_load_use.gtkw' }
        }
        $viewFile = Join-Path $waveDir $viewName
        Start-Process -FilePath $viewer -ArgumentList ('"' + $waveFile + '"'), ('"' + $viewFile + '"')
    }
} finally { Pop-Location }
