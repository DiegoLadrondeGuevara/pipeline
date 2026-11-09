`timescale 1ns/1ps
// E1 program 2 has eight real instructions and ends with sw to byte 100.
// Both cores start at the same reset edge. Completion is that store's write.
module e2_compare_tb;
  reg clk=0, reset=1;
  wire [31:0] wd_a, adr_a;
  wire we_a;
  integer cycle=0, cycles_a=0, cycles_b=0, i;
  top a(.clk(clk),.reset(reset),.WriteData(wd_a),
    .DataAdr(adr_a),.MemWrite(we_a));
  dualissue b(.clk(clk),.reset(reset));
  always #5 clk=~clk;
  always @(posedge clk) if (!reset) begin
    cycle=cycle+1;
    if (we_a && adr_a==100 && cycles_a==0) cycles_a=cycle;
    if (b.mem_write && b.mem_address==100 && cycles_b==0) cycles_b=cycle;
  end
  initial begin
    for(i=0;i<32;i=i+1) begin
      a.rvpipelined.dp.rf.rf[i]=0;
      b.rf.rf[i]=0;
    end
    repeat(2) @(negedge clk);
    reset=0;
    wait(cycles_a!=0 && cycles_b!=0);
    repeat(2) @(negedge clk);
    if (cycle>80) $fatal(1,"Comparison timeout");
    for(i=0;i<32;i=i+1)
      if (a.rvpipelined.dp.rf.rf[i] !== b.rf.rf[i])
        $fatal(1,"Comparison register x%0d mismatch",i);
    if (a.dmem.RAM[24] !== 25 || b.dm.RAM[24] !== 25 ||
        a.dmem.RAM[25] !== 25 || b.dm.RAM[25] !== 25)
      $fatal(1,"Comparison memory mismatch");
    $display("PASS A/B benchmark e1_2: retired=8 A_cycles=%0d B_cycles=%0d A_IPC=%0f B_IPC=%0f speedup=%0f",
      cycles_a,cycles_b,8.0/cycles_a,8.0/cycles_b,
      1.0*cycles_a/cycles_b);
    $finish;
  end
  initial begin
    #1000; $fatal(1,"Comparison timeout");
  end
endmodule
