`timescale 1ns/1ps
module e2_tb;
  reg clk=0, reset=1;
  integer case_num, n, retired_seen=0, expected_count;
  reg [1023:0] vcd_file;
  reg [31:0] terminal_address;
  reg [31:0] terminal_pc, expected_pc[0:16];
  reg seen_double=0, seen_raw=0, seen_resource=0, seen_stall=0;
  reg seen_mem0=0, seen_mem1=0, seen_taken0=0, seen_taken1=0;
  reg seen_not_taken0=0, seen_not_taken1=0;
  reg seen_forward0=0, seen_forward1=0;
  reg seen_m0=0, seen_m1=0, seen_w0=0, seen_w1=0;
  reg seen_same_rd=0;
  dualissue dut(.clk(clk), .reset(reset));
  always #5 clk=~clk;
  always @(negedge clk) if (!reset) begin
    if (dut.issue1) seen_double=1;
    if (dut.split_raw) seen_raw=1;
    if (dut.split_resource) seen_resource=1;
    if (dut.stall_load && !dut.issue0) seen_stall=1;
    if (dut.valid_m[0] && (dut.store_m[0] || dut.result_src_m[0]==1)) seen_mem0=1;
    if (dut.mem_lane1) seen_mem1=1;
    if (dut.taken0) seen_taken0=1;
    if (dut.taken1) seen_taken1=1;
    if (dut.valid_e[0] && dut.branch_e[0] && !dut.branch_taken_e[0])
      seen_not_taken0=1;
    if (dut.valid_e[1] && dut.branch_e[1] && !dut.branch_taken_e[1])
      seen_not_taken1=1;
    if (dut.forward_a[0]!=0 || dut.forward_b[0]!=0) seen_forward0=1;
    if (dut.forward_a[1]!=0 || dut.forward_b[1]!=0) seen_forward1=1;
    if (dut.forward_a[0]==3 || dut.forward_b[0]==3 ||
        dut.forward_a[1]==3 || dut.forward_b[1]==3) seen_m0=1;
    if (dut.forward_a[0]==4 || dut.forward_b[0]==4 ||
        dut.forward_a[1]==4 || dut.forward_b[1]==4) seen_m1=1;
    if (dut.forward_a[0]==1 || dut.forward_b[0]==1 ||
        dut.forward_a[1]==1 || dut.forward_b[1]==1) seen_w0=1;
    if (dut.forward_a[0]==2 || dut.forward_b[0]==2 ||
        dut.forward_a[1]==2 || dut.forward_b[1]==2) seen_w1=1;
    if (dut.valid_w[0] && dut.valid_w[1] && dut.write_w[0] &&
        dut.write_w[1] && dut.rd_w[0]!=0 && dut.rd_w[0]==dut.rd_w[1])
      seen_same_rd=1;
    if (dut.valid_w[0] && dut.pc_w[0]<=terminal_pc) begin
      if (retired_seen>=expected_count || dut.pc_w[0] !== expected_pc[retired_seen])
        $fatal(1,"E2 case %0d retirement order at index %0d PC=%0d",
          case_num,retired_seen,dut.pc_w[0]);
      retired_seen=retired_seen+1;
    end
    if (dut.valid_w[1] && dut.pc_w[1]<=terminal_pc) begin
      if (retired_seen>=expected_count || dut.pc_w[1] !== expected_pc[retired_seen])
        $fatal(1,"E2 case %0d retirement order at index %0d PC=%0d",
          case_num,retired_seen,dut.pc_w[1]);
      retired_seen=retired_seen+1;
    end
  end
  initial begin
    if (!$value$plusargs("CASE=%d", case_num)) case_num=1;
    if (!$value$plusargs("VCD=%s", vcd_file)) vcd_file="tests/e2.vcd";
    case (case_num)
      1: begin terminal_address=96; terminal_pc=40; expected_count=11;
        for(n=0;n<11;n=n+1) expected_pc[n]=n*4;
      end
      2: begin terminal_address=104; terminal_pc=28; expected_count=8;
        for(n=0;n<8;n=n+1) expected_pc[n]=n*4;
      end
      3: begin terminal_address=100; terminal_pc=64; expected_count=12;
        expected_pc[0]=0; expected_pc[1]=4; expected_pc[2]=8;
        expected_pc[3]=20; expected_pc[4]=24; expected_pc[5]=28;
        expected_pc[6]=32; expected_pc[7]=36; expected_pc[8]=40;
        expected_pc[9]=52; expected_pc[10]=56; expected_pc[11]=64;
      end
      4: begin terminal_address=100; terminal_pc=20; expected_count=6;
        for(n=0;n<6;n=n+1) expected_pc[n]=n*4;
      end
      default: $fatal(1,"Unknown CASE");
    endcase
`ifndef NO_WAVE
    $dumpfile(vcd_file); $dumpvars(0,e2_tb);
`endif
    repeat (2) @(negedge clk);
    reset=0;
    n=0;
    while (n<100 && !(dut.mem_write === 1'b1 &&
                       dut.mem_address === terminal_address)) begin
      @(negedge clk); n=n+1;
    end
    if (n==100) $fatal(1,"E2 case %0d timeout",case_num);
    @(negedge clk); #1; // terminal store has committed and retired
    $display("OBS case=%0d dual=%0d raw=%0d res=%0d stall=%0d mem0=%0d mem1=%0d taken0=%0d taken1=%0d fwd0=%0d fwd1=%0d M0=%0d M1=%0d W0=%0d W1=%0d",
      case_num,seen_double,seen_raw,seen_resource,seen_stall,
      seen_mem0,seen_mem1,seen_taken0,seen_taken1,seen_forward0,seen_forward1,
      seen_m0,seen_m1,seen_w0,seen_w1);
    case (case_num)
      1: begin
        if (dut.rf.rf[1] !== 10 || dut.rf.rf[2] !== 15 ||
            dut.rf.rf[3] !== 25 || dut.rf.rf[4] !== 7 ||
            dut.rf.rf[5] !== 9 || dut.rf.rf[6] !== 10 ||
            dut.rf.rf[7] !== 11 || dut.rf.rf[8] !== 12 ||
            dut.rf.rf[0] !== 0 || dut.dm.RAM[24] !== 12)
          $fatal(1,"E2 case 1 registers or memory incorrect");
        if (!seen_double || !seen_raw || !seen_forward0 ||
            !seen_forward1 || !seen_same_rd)
          $fatal(1,"E2 case 1 missing dual issue, RAW, same-rd, or forwarding");
      end
      2: begin
        if (dut.rf.rf[3] !== 7 || dut.rf.rf[4] !== 8 ||
            dut.rf.rf[5] !== 25 || dut.dm.RAM[24] !== 25 ||
            dut.dm.RAM[25] !== 8 || dut.dm.RAM[26] !== 25)
          $fatal(1,"E2 case 2 resource or data incorrect");
        if (!seen_resource || !seen_mem0 || !seen_mem1)
          $fatal(1,"E2 case 2 missing memory conflict or both lane selections");
      end
      3: begin
        if (dut.rf.rf[3] !== 3 || dut.rf.rf[4] !== 4 ||
            dut.rf.rf[5] !== 5 || dut.rf.rf[6] !== 6 ||
            dut.rf.rf[7] !== 60 || dut.dm.RAM[25] !== 6 ||
            dut.dm.RAM[27] !== 32'bx || dut.dm.RAM[28] !== 32'bx ||
            dut.dm.RAM[29] !== 32'bx)
          $fatal(1,"E2 case 3 branch/jump or flush incorrect");
        if (!seen_taken0 || !seen_taken1 || !seen_not_taken0 ||
            !seen_not_taken1 || !seen_resource)
          $fatal(1,"E2 case 3 missing taken/not-taken branch by lane");
      end
      4: begin
        if (dut.rf.rf[3] !== 25 || dut.rf.rf[4] !== 26 ||
            dut.dm.RAM[24] !== 25 || dut.dm.RAM[25] !== 26)
          $fatal(1,"E2 case 4 load-use result incorrect");
        if (!seen_stall || !seen_resource)
          $fatal(1,"E2 case 4 missing zero-issue stall or memory split");
      end
      default: $fatal(1,"Unknown CASE");
    endcase
    if (retired_seen != expected_count)
      $fatal(1,"E2 case %0d retired %0d PCs, expected %0d",
        case_num,retired_seen,expected_count);
    $display("PASS E2 case %0d: cycles_to_store=%0d double=%0d stalls=%0d splits=%0d",
      case_num,dut.cycle_count,
      dut.double_issue_count,dut.stall_count,dut.split_count);
    $finish;
  end
endmodule
