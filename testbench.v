`timescale 1ns/1ps
module testbench;
  reg clk = 0;
  reg reset = 1;
  wire [31:0] WriteData, DataAdr;
  wire MemWrite;
  integer test_case = 1;
  integer cycles = 0, stalls = 0, forwards = 0, redirects = 0;
  reg [1023:0] vcd_file;

  top dut(.clk(clk), .reset(reset), .WriteData(WriteData),
          .DataAdr(DataAdr), .MemWrite(MemWrite));
  always #5 clk = ~clk;

  initial begin
    if (!$value$plusargs("CASE=%d", test_case)) test_case = 1;
    if ($value$plusargs("VCD=%s", vcd_file)) begin
      $dumpfile(vcd_file);
      $dumpvars(0, testbench);
    end
    repeat (2) @(negedge clk);
    reset = 0;
  end

  always @(posedge clk) begin
    if (!reset) begin
      cycles = cycles + 1;
      if (dut.rvpipelined.dp.Stall_D) stalls = stalls + 1;
      if (dut.rvpipelined.dp.ForwardAE != 0 ||
          dut.rvpipelined.dp.ForwardBE != 0) forwards = forwards + 1;
      if (dut.rvpipelined.dp.PCSrc_E) redirects = redirects + 1;
      if (cycles > 200) $fatal(1, "Timeout: case %0d", test_case);

      if (MemWrite) begin
        if (DataAdr === 32'd104)
          $fatal(1, "Wrong-path store was not flushed");
        if (DataAdr === 32'd100) begin
          if (WriteData !== 32'd25)
            $fatal(1, "Expected 25 at address 100, got %0d", WriteData);
          @(negedge clk); #1;
          if (dut.dmem.RAM[25] !== 32'd25)
            $fatal(1, "Final store did not reach data memory");
          if (test_case == 1 && stalls != 0)
            $fatal(1, "Independent ISA test stalled");
          if (test_case == 1 && (dut.rvpipelined.dp.rf.rf[3] !== 32'd25 ||
                                 dut.rvpipelined.dp.rf.rf[4] !== 32'd5 ||
                                 dut.rvpipelined.dp.rf.rf[5] !== 32'd1 ||
                                 dut.rvpipelined.dp.rf.rf[6] !== 32'd10 ||
                                 dut.rvpipelined.dp.rf.rf[7] !== 32'd15 ||
                                 dut.rvpipelined.dp.rf.rf[8] !== 32'd1024 ||
                                 dut.rvpipelined.dp.rf.rf[9] !== 32'd512 ||
                                 dut.rvpipelined.dp.rf.rf[10] !== 32'd10 ||
                                 dut.rvpipelined.dp.rf.rf[11] !== 32'd25 ||
                                 dut.rvpipelined.dp.rf.rf[12] !== 32'd1 ||
                                 dut.rvpipelined.dp.rf.rf[13] !== 32'd7 ||
                                 dut.rvpipelined.dp.rf.rf[14] !== 32'd11 ||
                                 dut.rvpipelined.dp.rf.rf[15] !== 32'd4 ||
                                 dut.rvpipelined.dp.rf.rf[16] !== 32'd2 ||
                                 dut.dmem.RAM[24] !== 32'd10))
            $fatal(1, "ISA arithmetic result failed");
          if (test_case == 2 && (forwards < 3 || stalls != 0 ||
                                 dut.rvpipelined.dp.rf.rf[4] !== 32'd3 ||
                                 dut.rvpipelined.dp.rf.rf[5] !== 32'd25))
            $fatal(1, "Forwarding/priority check failed");
          if (test_case == 3 && (stalls != 1 ||
                                 dut.dmem.RAM[24] !== 32'd25 ||
                                 dut.rvpipelined.dp.rf.rf[2] !== 32'd25))
            $fatal(1, "Load-use stall or load result failed");
          if (test_case == 4 && (redirects != 2 ||
                                 dut.rvpipelined.dp.rf.rf[3] !== 32'd24))
            $fatal(1, "Branch/jump flush or JAL link failed");
          $display("PASS case=%0d cycles=%0d stalls=%0d forwards=%0d redirects=%0d",
                   test_case, cycles, stalls, forwards, redirects);
          $finish;
        end
      end
    end
  end
endmodule
