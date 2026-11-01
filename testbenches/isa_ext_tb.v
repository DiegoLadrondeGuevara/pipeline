`timescale 1ns/1ps
module isa_ext_tb;
  reg clk = 0, reset = 1;
  wire [31:0] WriteData, DataAdr;
  wire MemWrite;
  integer cycles = 0;
  top dut(.clk(clk), .reset(reset), .WriteData(WriteData),
          .DataAdr(DataAdr), .MemWrite(MemWrite));
  always #5 clk = ~clk;
  initial begin
    $dumpfile("tests/e1_isa_ext.vcd");
    $dumpvars(0, isa_ext_tb);
    repeat (2) @(negedge clk);
    reset = 0;
  end
  always @(posedge clk) if (!reset) begin
    cycles = cycles + 1;
    if (cycles > 150) $fatal(1, "Extended ISA timeout");
    if (MemWrite && DataAdr === 32'd124) begin
      if (WriteData !== 32'd1) $fatal(1, "JALR/branch wrong path executed");
      @(negedge clk); #1;
      if (dut.dmem.RAM[32] !== 32'hff808000 ||
          dut.rvpipelined.dp.rf.rf[3] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[4] !== 32'd0 ||
          dut.rvpipelined.dp.rf.rf[5] !== 32'hfffffffe ||
          dut.rvpipelined.dp.rf.rf[6] !== 32'hfffffffe ||
          dut.rvpipelined.dp.rf.rf[7] !== 32'hffffffff ||
          dut.rvpipelined.dp.rf.rf[8] !== 32'hffffffff ||
          dut.rvpipelined.dp.rf.rf[9] !== 32'h12345000 ||
          dut.rvpipelined.dp.rf.rf[10] !== 32'd36 ||
          dut.rvpipelined.dp.rf.rf[13] !== 32'hffffff80 ||
          dut.rvpipelined.dp.rf.rf[14] !== 32'h00000080 ||
          dut.rvpipelined.dp.rf.rf[15] !== 32'hffffff80 ||
          dut.rvpipelined.dp.rf.rf[16] !== 32'h0000ff80 ||
          dut.rvpipelined.dp.rf.rf[17] !== 32'hff808000 ||
          dut.rvpipelined.dp.rf.rf[19] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[20] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[21] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[22] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[23] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[24] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[25] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[26] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[27] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[28] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[29] !== 32'd1 ||
          dut.rvpipelined.dp.rf.rf[30] !== 32'd209 ||
          dut.rvpipelined.dp.rf.rf[31] !== 32'd204)
        $fatal(1, "Extended ISA register or memory mismatch");
      $display("PASS extended RV32I integer-path case cycles=%0d", cycles);
      $finish;
    end
  end
endmodule
