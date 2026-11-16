`timescale 1ns/1ps
// End-state equivalence of the unchanged E1 programs on A and B.
module e2_equiv_tb;
  reg clk=0, reset=1;
  wire [31:0] wd_a, adr_a;
  wire we_a;
  integer i, cycles;
  top a(.clk(clk), .reset(reset), .WriteData(wd_a),
        .DataAdr(adr_a), .MemWrite(we_a));
  dualissue b(.clk(clk), .reset(reset));
  always #5 clk=~clk;
  initial begin
    if (!$value$plusargs("CYCLES=%d",cycles)) cycles=130;
    for(i=0;i<32;i=i+1) begin
      a.rvpipelined.dp.rf.rf[i]=0;
      b.rf.rf[i]=0;
    end
    repeat (2) @(negedge clk);
    reset=0;
    repeat (cycles) @(negedge clk);
    for(i=0;i<32;i=i+1)
      if (a.rvpipelined.dp.rf.rf[i] !== b.rf.rf[i])
        $fatal(1,"A/B register x%0d: A=%h B=%h",i,
          a.rvpipelined.dp.rf.rf[i],b.rf.rf[i]);
    for(i=0;i<256;i=i+1)
      if (a.dmem.RAM[i] !== b.dm.RAM[i])
        $fatal(1,"A/B memory word %0d: A=%h B=%h",i,
          a.dmem.RAM[i],b.dm.RAM[i]);
    $display("PASS A/B equivalence after %0d cycles",cycles);
    $finish;
  end
endmodule
