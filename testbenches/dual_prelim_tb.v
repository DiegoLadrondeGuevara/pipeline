`timescale 1ns/1ps
module dual_prelim_tb;
  reg clk = 0, reset = 1, hold = 0, flush = 0;
  reg [31:0] redirect_pc = 0;
  wire [31:0] pc0f, pc1f, instr0d, instr1d, pc0e, pc1e, result0, result1;
  wire valid0, valid1;
  dualissue_prelim dut(.clk(clk), .reset(reset), .hold(hold), .flush(flush),
    .redirect_pc(redirect_pc), .PC0_F(pc0f), .PC1_F(pc1f),
    .Instr0_D(instr0d), .Instr1_D(instr1d), .PC0_E(pc0e), .PC1_E(pc1e),
    .ALUResult0_E(result0), .ALUResult1_E(result1),
    .Valid0_E(valid0), .Valid1_E(valid1));
  always #5 clk = ~clk;
  initial begin
    $dumpfile("tests/e1_dual.vcd"); $dumpvars(0, dual_prelim_tb);
    repeat (2) @(negedge clk);
    reset = 0;
    @(posedge clk); #1;
    if (pc0f !== 8 || pc1f !== 12 ||
        instr0d !== 32'h00a00093 || instr1d !== 32'h00f00113 ||
        dut.imm0_d !== 10 || dut.imm1_d !== 15 ||
        dut.alu0_ctrl_d !== 0 || dut.alu1_ctrl_d !== 0 ||
        !dut.write0_d || !dut.write1_d)
      $fatal(1, "Dual Fetch/Decode pair 0 failed");
    @(posedge clk); #1;
    if (instr0d !== 32'h00400193 || instr1d !== 32'h00500213 ||
        dut.imm0_d !== 4 || dut.imm1_d !== 5 ||
        dut.alu0_ctrl_d !== 0 || dut.alu1_ctrl_d !== 0 ||
        !dut.write0_d || !dut.write1_d ||
        !valid0 || !valid1 || pc0e !== 0 || pc1e !== 4 ||
        result0 !== 10 || result1 !== 15)
      $fatal(1, "Dual Fetch/Decode pair 1 or preliminary EX pair 0 failed");
    @(posedge clk); #1;
    if (!valid0 || !valid1 || pc0e !== 8 || pc1e !== 12 ||
        result0 !== 4 || result1 !== 5)
      $fatal(1, "Preliminary two-lane EX pair 1 failed");
    hold = 1;
    @(posedge clk); #1;
    if (valid0 || valid1 || pc0f !== 24)
      $fatal(1, "Hold did not preserve the pending pair");
    hold = 0; flush = 1; redirect_pc = 64;
    @(posedge clk); #1;
    if (pc0f !== 64 || pc1f !== 68 || valid0 || valid1)
      $fatal(1, "Dual front-end redirect failed");
    $display("PASS dual fetch/decode and preliminary two-lane EX");
    $finish;
  end
endmodule
