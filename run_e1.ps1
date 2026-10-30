$ErrorActionPreference = 'Stop'
python tests/gen_programs.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$sources = (Get-ChildItem -Filter '*.v').Name
$iverilogCommand = Get-Command iverilog -ErrorAction SilentlyContinue
$vvpCommand = Get-Command vvp -ErrorAction SilentlyContinue
if ($iverilogCommand -and $vvpCommand) {
    $iverilog = $iverilogCommand.Source
    $vvp = $vvpCommand.Source
} elseif ((Test-Path 'C:\msys64\ucrt64\bin\iverilog.exe') -and
          (Test-Path 'C:\msys64\ucrt64\bin\vvp.exe')) {
    $iverilog = 'C:\msys64\ucrt64\bin\iverilog.exe'
    $vvp = 'C:\msys64\ucrt64\bin\vvp.exe'
} else {
    throw 'Icarus Verilog (iverilog y vvp) debe estar en PATH o instalado en C:\msys64\ucrt64\bin.'
}
& $iverilog -g2012 -s testbench -o tests/e1_sim.out $sources
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
foreach ($case in 1..4) {
    & $vvp tests/e1_sim.out "+CASE=$case" "+PROGRAM=tests/e1_$case.mem" "+VCD=tests/e1_$case.vcd"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
& $iverilog -g2012 -s dual_prelim_tb -o tests/e1_dual_sim.out $sources
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $vvp tests/e1_dual_sim.out '+PROGRAM=tests/e1_dual.mem'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $iverilog -g2012 -s regfile_dual_tb -o tests/regfile_dual_sim.out $sources
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $vvp tests/regfile_dual_sim.out
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
