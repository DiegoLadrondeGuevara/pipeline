`timescale 1ns/1ps
module regfile_dual_tb;
  reg clk = 0;
  reg we0 = 0, we1 = 0;
  reg [4:0] wa0 = 0, wa1 = 0;
  reg [31:0] wd0 = 0, wd1 = 0;
  wire [31:0] r0a, r0b, r1a, r1b;
  regfile_dual dut(.clk(clk), .we0(we0), .we1(we1),
    .ra0(5'd1), .rb0(5'd2), .ra1(5'd1), .rb1(5'd0),
    .wa0(wa0), .wa1(wa1), .wd0(wd0), .wd1(wd1),
    .rd0a(r0a), .rd0b(r0b), .rd1a(r1a), .rd1b(r1b));
  always #5 clk = ~clk;
  initial begin
    we0 = 1; wa0 = 1; wd0 = 11;
    we1 = 1; wa1 = 2; wd1 = 22;
    @(negedge clk); #1;
    if (r0a !== 11 || r0b !== 22 || r1a !== 11 || r1b !== 0)
      $fatal(1, "Independent dual write or four reads failed");
    wa0 = 1; wd0 = 33; wa1 = 1; wd1 = 44;
    @(negedge clk); #1;
    if (r0a !== 44 || r1a !== 44)
      $fatal(1, "Younger lane must win same-register writes");
    wa0 = 0; wa1 = 0; wd0 = 99; wd1 = 99;
    @(negedge clk); #1;
    if (r1b !== 0) $fatal(1, "x0 changed");
    $display("PASS dual register file: four reads, two writes, youngest wins");
    $finish;
  end
endmodule
