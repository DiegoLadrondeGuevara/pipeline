$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python tests/gen_e2.py
    if ($LASTEXITCODE -ne 0) { throw 'Program generation failed.' }
    $iverilog = (Get-Command iverilog -ErrorAction Stop).Source
    $vvp = (Get-Command vvp -ErrorAction Stop).Source
    $rtl = @((Get-ChildItem rtl -Filter '*.v').FullName)

    function Compile-Case($top, $bench, $output) {
        & $iverilog -g2012 -s $top -o $output ($rtl + @((Resolve-Path $bench).Path))
        if ($LASTEXITCODE -ne 0) { throw "Compile failed: $top" }
    }
    function Simulate($output, $program, $extraArgs) {
        & $vvp $output "+PROGRAM=$program" @extraArgs
        if ($LASTEXITCODE -ne 0) { throw "Simulation failed: $program" }
    }

    Compile-Case 'e2_tb' 'testbenches/e2_tb.v' 'tests/e2_sim.out'
    foreach ($case in 1..4) {
        Simulate 'tests/e2_sim.out' "tests/e2_$case.mem" @("+CASE=$case", "+VCD=tests/e2_$case.vcd")
    }

    Compile-Case 'e2_equiv_tb' 'testbenches/e2_equiv_tb.v' 'tests/e2_equiv.out'
    foreach ($program in @('e1_1', 'e1_2', 'e1_3', 'e1_4', 'e1_isa_ext')) {
        Simulate 'tests/e2_equiv.out' "tests/$program.mem" @()
    }

    Compile-Case 'e2_compare_tb' 'testbenches/e2_compare_tb.v' 'tests/e2_compare.out'
    Simulate 'tests/e2_compare.out' 'tests/e1_2.mem' @()
    Write-Output 'PASS complete E2 suite'
} finally {
    Pop-Location
}
