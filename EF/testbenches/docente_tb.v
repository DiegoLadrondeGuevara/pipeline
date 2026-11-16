`timescale 1ns/1ps
// Compile with -DSINGLE for A; without it for B or C. VCD is opt-in with -DWAVES.
// The checkpoint stores are the last instructions in stages A, B, C and D.
module docente_tb;
  reg clk=0, reset=1;
  integer cycles=0, retired=0, stage, i;
  reg [3:0] stage_seen=0;
  reg [31:0] expected_reg[0:31], expected_mem[0:13];
  reg [13:0] mem_known=0;
  localparam BASE=1536, FIN_PC=356, FINAL_STORE_PC=352;
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

`ifdef WAVES
  reg [1023:0] vcd_file;
  reg [3:0] checkpoint_passed=0;
`ifndef SINGLE
  // Named probes expose the stage-A state and the active memory lane.
  wire [31:0] wave_pc_mem = dut.mem_lane1 ? dut.pc_m[1] : dut.pc_m[0];
  wire [31:0] wave_store_data = dut.mem_store_data;
  wire [31:0] wave_x5 = dut.rf.rf[5], wave_x6 = dut.rf.rf[6];
  wire [31:0] wave_x10 = dut.rf.rf[10];
  wire [31:0] wave_mem_0 = dut.dm.RAM[384];
  wire [31:0] wave_mem_1 = dut.dm.RAM[385];
  wire [31:0] wave_mem_2 = dut.dm.RAM[386];
  wire [31:0] wave_x11 = dut.rf.rf[11], wave_x12 = dut.rf.rf[12];
  wire [31:0] wave_x13 = dut.rf.rf[13], wave_x14 = dut.rf.rf[14];
  wire [31:0] wave_x15 = dut.rf.rf[15], wave_x16 = dut.rf.rf[16];
  wire [31:0] wave_x17 = dut.rf.rf[17], wave_x18 = dut.rf.rf[18];
  wire [31:0] wave_mem_3 = dut.dm.RAM[387];
  wire [31:0] wave_mem_4 = dut.dm.RAM[388];
  wire [31:0] wave_mem_5 = dut.dm.RAM[389];
  wire [31:0] wave_x19 = dut.rf.rf[19], wave_x20 = dut.rf.rf[20];
  wire [31:0] wave_x21 = dut.rf.rf[21], wave_x22 = dut.rf.rf[22];
  wire [31:0] wave_x24 = dut.rf.rf[24], wave_x26 = dut.rf.rf[26];
  wire [31:0] wave_mem_6 = dut.dm.RAM[390];
  wire [31:0] wave_mem_7 = dut.dm.RAM[391];
  wire [31:0] wave_mem_8 = dut.dm.RAM[392];
  wire [31:0] wave_x28 = dut.rf.rf[28], wave_x29 = dut.rf.rf[29];
  wire [31:0] wave_x31 = dut.rf.rf[31];
  wire [31:0] wave_mem_9 = dut.dm.RAM[393];
  wire [31:0] wave_mem_10 = dut.dm.RAM[394];
  wire [31:0] wave_mem_11 = dut.dm.RAM[395];
  wire [31:0] wave_mem_12 = dut.dm.RAM[396];
  wire [31:0] wave_mem_13 = dut.dm.RAM[397];
`endif
  initial begin
    if (!$value$plusargs("VCD=%s", vcd_file))
      vcd_file="../resultados/waveforms/docente_C.vcd";
    $dumpfile(vcd_file);
    $dumpvars(0, docente_tb);
  end
`endif

  always #5 clk=~clk;

  task check_state;
    input integer checkpoint;
    begin
      for (i=0; i<32; i=i+1)
        if (`REG(i) !== expected_reg[i])
          $fatal(1,"Stage %0d register x%0d: got %0d expected %0d",
            checkpoint,i,`REG(i),expected_reg[i]);
      for (i=0; i<14; i=i+1)
        if (mem_known[i] && `MEM(384+i) !== expected_mem[i])
          $fatal(1,"Stage %0d memory[%0d]: got %0d expected %0d",
            checkpoint,BASE+i*4,`MEM(384+i),expected_mem[i]);
`ifdef WAVES
      checkpoint_passed[checkpoint-1]=1;
`endif
      $display("PASS teacher stage %0d at cycle %0d",checkpoint,cycles);
    end
  endtask

  task prepare_expected;
    input integer checkpoint;
    begin
      case (checkpoint)
        1: begin
          expected_reg[1]=1536; expected_reg[2]=1;
          expected_reg[3]=8; expected_reg[4]=3;
          expected_reg[5]=11; expected_reg[6]=5;
          expected_reg[7]=16; expected_reg[8]=2;
          expected_reg[9]=7; expected_reg[10]=12;
          expected_mem[0]=11; expected_mem[1]=5; expected_mem[2]=12;
          mem_known[0]=1; mem_known[1]=1; mem_known[2]=1;
        end
        2: begin
          expected_reg[11]=11; expected_reg[12]=16;
          expected_reg[13]=5; expected_reg[14]=12;
          expected_reg[15]=7; expected_reg[16]=7;
          expected_reg[17]=16; expected_reg[18]=23;
          expected_mem[3]=7; expected_mem[4]=16; expected_mem[5]=23;
          mem_known[3]=1; mem_known[4]=1; mem_known[5]=1;
        end
        3: begin
          expected_reg[19]=12; expected_reg[20]=12;
          expected_reg[21]=24; expected_reg[22]=18;
          expected_reg[24]=24; expected_reg[26]=6;
          expected_mem[6]=24; expected_mem[7]=18; expected_mem[8]=24;
          mem_known[6]=1; mem_known[7]=1; mem_known[8]=1;
        end
        4: begin
          expected_reg[19]=6; expected_reg[20]=6;
          expected_reg[25]=4; expected_reg[26]=4;
          expected_reg[27]=1560; expected_reg[28]=74;
          expected_reg[29]=4; expected_reg[30]=23;
          expected_reg[31]=1;
          expected_mem[9]=74; expected_mem[10]=4;
          expected_mem[11]=0; expected_mem[12]=1;
          expected_mem[13]=1;
          mem_known[9]=1; mem_known[10]=1; mem_known[11]=1;
          mem_known[12]=1; mem_known[13]=1;
        end
      endcase
    end
  endtask

  initial begin
    for (i=0; i<32; i=i+1) expected_reg[i]=0;
    for (i=0; i<14; i=i+1) expected_mem[i]=0;
    for (i=0; i<32; i=i+1) `REG(i)=0;
    repeat (2) @(negedge clk);
    reset=0;
  end

  always @(posedge clk) if (!reset) begin
    cycles=cycles+1;
    if (mem_write) begin
      case (mem_address)
        BASE+8:  stage=1;
        BASE+20: stage=2;
        BASE+32: stage=3;
        BASE+52: stage=4;
        default: stage=0;
      endcase
      if (stage!=0) begin
        if (stage_seen[stage-1]) $fatal(1,"Repeated stage %0d store",stage);
        stage_seen[stage-1]=1;
        prepare_expected(stage);
        // Memory commits on this rising edge. Inspect before the falling-edge
        // register-file write of a younger instruction in the same issue pair.
        #1;
        check_state(stage);
        if (stage==4) begin
          @(negedge clk); #1;
          if (stage_seen !== 4'b1111)
            $fatal(1,"Missing teacher stage checkpoint");
          if (!`FINAL_W) $fatal(1,"Final store did not reach WB");
`ifdef OPTIMIZED
          if (btb_predictions==0 || btb_correct==0)
            $fatal(1,"BTB did not make a useful prediction");
          $display("BTB controls=%0d predictions=%0d correct=%0d corrections=%0d (fin excluded)",
            btb_controls,btb_predictions,btb_correct,btb_corrections);
`endif
`ifndef SINGLE
          $display("Dual issue=%0d load stalls=%0d partial issue=%0d",
            dut.double_issue_count,dut.stall_count,dut.split_count);
`endif
          $display("PASS teacher complete cycles=%0d retired=%0d",cycles,retired);
          $finish;
        end
      end
    end
  end

  always @(negedge clk) if (!reset) begin
    if (`RETIRE0) retired=retired+1;
    if (`RETIRE1) retired=retired+1;
  end

  initial begin
    #200000;
    $fatal(1,"Teacher program timeout");
  end
endmodule
