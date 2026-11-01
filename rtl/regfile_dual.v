// Four asynchronous reads and two WB writes. Lane 1 is younger and wins
// when both writes target the same nonzero register in the same cycle.
module regfile_dual(
    input clk,
    input we0, we1,
    input [4:0] ra0, rb0, ra1, rb1, wa0, wa1,
    input [31:0] wd0, wd1,
    output [31:0] rd0a, rd0b, rd1a, rd1b
);
  reg [31:0] rf[0:31];
  integer i;
  initial for (i = 0; i < 32; i = i + 1) rf[i] = 0;
  always @(negedge clk) begin
    if (we0 && wa0 != 0 && !(we1 && wa1 == wa0)) rf[wa0] <= wd0;
    if (we1 && wa1 != 0) rf[wa1] <= wd1;
  end
  assign rd0a = (ra0 == 0) ? 0 : rf[ra0];
  assign rd0b = (rb0 == 0) ? 0 : rf[rb0];
  assign rd1a = (ra1 == 0) ? 0 : rf[ra1];
  assign rd1b = (rb1 == 0) ? 0 : rf[rb1];
endmodule
