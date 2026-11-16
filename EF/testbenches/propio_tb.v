`timescale 1ns/1ps
// Shared benchmark: same propio.mem, reset and completion event for A/B/C.
// Waveform output is opt-in with -DWAVES; routine code checks stay trace-free.
module propio_tb;
  reg clk=0, reset=1;
  integer cycles=0, retired=0, i;
`ifdef WAVES
  reg [1023:0] vcd_file;
  // Named probes make unpacked per-lane arrays visible in GTKWave/Icarus.
  wire [31:0] wave_pc_d0 = dut.pc_d[0], wave_pc_d1 = dut.pc_d[1];
  wire [31:0] wave_instr_d0 = dut.instr_d[0], wave_instr_d1 = dut.instr_d[1];
  wire wave_valid_d0 = dut.valid_d[0], wave_valid_d1 = dut.valid_d[1];
  wire [31:0] wave_pc_e0 = dut.pc_e[0], wave_pc_e1 = dut.pc_e[1];
  wire wave_valid_e0 = dut.valid_e[0], wave_valid_e1 = dut.valid_e[1];
  wire [31:0] wave_pc_m0 = dut.pc_m[0], wave_pc_m1 = dut.pc_m[1];
  wire wave_valid_m0 = dut.valid_m[0], wave_valid_m1 = dut.valid_m[1];
  wire [31:0] wave_pc_w0 = dut.pc_w[0], wave_pc_w1 = dut.pc_w[1];
  wire wave_valid_w0 = dut.valid_w[0], wave_valid_w1 = dut.valid_w[1];
  wire [31:0] wave_x4 = dut.rf.rf[4], wave_x9 = dut.rf.rf[9];
  initial begin
    if (!$value$plusargs("VCD=%s", vcd_file))
      vcd_file="../resultados/waveforms/propio_C.vcd";
    $dumpfile(vcd_file);
    $dumpvars(0, propio_tb);
  end
`endif
  localparam FIN_PC=176, FINAL_STORE_PC=172;
`ifdef OPTIMIZED
  integer btb_controls=0, btb_predictions=0, btb_correct=0, btb_corrections=0;
  always @(posedge clk) if (!reset && dut.control_resolved && dut.branch_pc < FIN_PC) begin
    btb_controls=btb_controls+1;
    if (dut.predicted_next_pc != dut.branch_pc+4) btb_predictions=btb_predictions+1;
    if (dut.predicted_next_pc == dut.actual_next_pc) btb_correct=btb_correct+1;
    else btb_corrections=btb_corrections+1;
  end
`endif
  wire mem_write;
  wire [31:0] mem_address;
`ifdef SINGLE
  wire [31:0] write_data;
  top dut(.clk(clk), .reset(reset), .WriteData(write_data),
          .DataAdr(mem_address), .MemWrite(mem_write));
`define REG(n) dut.rvpipelined.dp.rf.rf[n]
`define MEM(n) dut.dmem.RAM[n]
`define RETIRE0 (dut.rvpipelined.dp.Valid_W && dut.rvpipelined.dp.PCPlus4_W >= 4 && dut.rvpipelined.dp.PCPlus4_W <= FIN_PC)
`define RETIRE1 1'b0
`define FINAL_W (dut.rvpipelined.dp.Valid_W && dut.rvpipelined.dp.PCPlus4_W == FINAL_STORE_PC+4)
`else
  dualissue dut(.clk(clk), .reset(reset));
  assign mem_write = dut.mem_write;
  assign mem_address = dut.mem_address;
`define REG(n) dut.rf.rf[n]
`define MEM(n) dut.dm.RAM[n]
`define RETIRE0 (dut.valid_w[0] && dut.pc_w[0] < FIN_PC)
`define RETIRE1 (dut.valid_w[1] && dut.pc_w[1] < FIN_PC)
`define FINAL_W ((dut.valid_w[0] && dut.pc_w[0] == FINAL_STORE_PC) || (dut.valid_w[1] && dut.pc_w[1] == FINAL_STORE_PC))
`endif

  always #5 clk=~clk;
  initial begin
    for (i=0; i<32; i=i+1) `REG(i)=0;
    repeat (2) @(negedge clk);
    reset=0;
  end

  always @(negedge clk) if (!reset) begin
    if (`RETIRE0) retired=retired+1;
    if (`RETIRE1) retired=retired+1;
  end

  always @(posedge clk) if (!reset) begin
    cycles=cycles+1;
    if (mem_write && mem_address==1224) begin
      #1;
      for (i=0; i<12; i=i+1)
        if (`MEM(256+i) !== i+3)
          $fatal(1,"Own program array[%0d] incorrect: got %0d",i,`MEM(256+i));
      if (`MEM(300) !== 102 || `MEM(301) !== 102 ||
          `MEM(302) !== 6 || `MEM(303) !== 6 ||
          `MEM(304) !== 16368 || `MEM(305) !== 66 ||
          `MEM(306) !== 1)
        $fatal(1,"Own program result memory incorrect");
      if (`REG(4) !== 102 || `REG(5) !== 6 || `REG(6) !== 6 ||
          `REG(14) !== 102 || `REG(16) !== 16368 || `REG(17) !== 66 ||
          `REG(18) !== 1)
        $fatal(1,"Own program result registers incorrect");
      @(negedge clk); #1;
      if (!`FINAL_W) $fatal(1,"Own program final store did not reach WB");
`ifndef SINGLE
      if (dut.double_issue_count==0 || dut.stall_count==0)
        $fatal(1,"Own program did not exercise dual issue and load stall");
`endif
`ifdef OPTIMIZED
      if (btb_predictions==0 || btb_correct==0)
        $fatal(1,"Own program did not exercise useful BTB predictions");
      $display("BTB controls=%0d predictions=%0d correct=%0d corrections=%0d (fin excluded)",
        btb_controls,btb_predictions,btb_correct,btb_corrections);
`endif
`ifndef SINGLE
      $display("Dual issue=%0d load stalls=%0d partial issue=%0d",
        dut.double_issue_count,dut.stall_count,dut.split_count);
`endif
      $display("PASS own program cycles=%0d retired=%0d",cycles,retired);
      $finish;
    end
  end

  initial begin
    #200000;
    $fatal(1,"Own program timeout");
  end
endmodule
