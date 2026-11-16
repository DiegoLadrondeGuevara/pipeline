// RV32I in-order dual-issue pipeline. Slot 0 is older than slot 1.
module dualissue(input clk, reset);
  localparam NOP = 32'h00000013;

  // IF/ID sliding pair. fetch_pc is the first address not buffered in ID.
  reg [31:0] fetch_pc;
  reg [31:0] instr_d [0:1], pc_d [0:1];
  reg [31:0] pred_next_d [0:1], pred_next_e [0:1];
  reg pred_taken_d [0:1];
  reg valid_d [0:1];
  wire [31:0] fetch0, fetch1;
  imem im(.a(fetch_pc), .a2(fetch_pc + 32'd4),
          .rd(fetch0), .rd2(fetch1));
  wire btb_hit0, btb_hit1, predict0, predict1;
  wire [31:0] btb_target0, btb_target1;
  wire [31:0] fetch_next0 = predict0 ? btb_target0 : fetch_pc+32'd4;
  wire [31:0] fetch_next1 = predict1 ? btb_target1 : fetch_pc+32'd8;

  wire [4:0] rs1_d [0:1], rs2_d [0:1], rd_d [0:1];
  wire [6:0] op_d [0:1];
  wire uses1_d [0:1], uses2_d [0:1], mem_d [0:1], control_d [0:1];
  wire [1:0] result_src_d [0:1], srca_sel_d [0:1];
  wire [2:0] imm_src_d [0:1];
  wire [3:0] alu_ctrl_d [0:1];
  wire write_d [0:1], store_d [0:1], branch_d [0:1], jump_d [0:1];
  wire jumpreg_d [0:1], alusrc_d [0:1];
  wire [31:0] imm_d [0:1], ra_d [0:1], rb_d [0:1];
  wire [31:0] wb_value [0:1];

  genvar g;
  generate for (g=0; g<2; g=g+1) begin: decode
    assign rs1_d[g] = instr_d[g][19:15];
    assign rs2_d[g] = instr_d[g][24:20];
    assign rd_d[g] = instr_d[g][11:7];
    assign op_d[g] = instr_d[g][6:0];
    assign uses1_d[g] = op_d[g]==7'h33 || op_d[g]==7'h13 ||
        op_d[g]==7'h03 || op_d[g]==7'h23 || op_d[g]==7'h63 ||
        op_d[g]==7'h67;
    assign uses2_d[g] = op_d[g]==7'h33 || op_d[g]==7'h23 ||
        op_d[g]==7'h63;
    controller c(.op(op_d[g]), .funct3(instr_d[g][14:12]),
      .funct7b5(instr_d[g][30]), .ResultSrc(result_src_d[g]),
      .SrcASel(srca_sel_d[g]), .MemWrite(store_d[g]),
      .Branch(branch_d[g]), .Jump(jump_d[g]),
      .JumpReg(jumpreg_d[g]), .ALUSrc(alusrc_d[g]),
      .RegWrite(write_d[g]), .ImmSrc(imm_src_d[g]),
      .ALUControl(alu_ctrl_d[g]));
    extend ext(.instr(instr_d[g][31:7]), .immsrc(imm_src_d[g]),
      .immext(imm_d[g]));
    assign mem_d[g] = op_d[g]==7'h03 || op_d[g]==7'h23;
    assign control_d[g] = branch_d[g] || jump_d[g];
  end endgenerate

  reg [31:0] pc_e [0:1], ra_e [0:1], rb_e [0:1], imm_e [0:1];
  reg [4:0] rs1_e [0:1], rs2_e [0:1], rd_e [0:1];
  reg [3:0] alu_ctrl_e [0:1];
  reg [2:0] funct3_e [0:1];
  reg [1:0] result_src_e [0:1], srca_sel_e [0:1];
  reg valid_e [0:1], write_e [0:1], store_e [0:1];
  reg branch_e [0:1], jump_e [0:1], jumpreg_e [0:1], alusrc_e [0:1];

  reg [31:0] alu_m [0:1], store_data_m [0:1], pc4_m [0:1], pc_m [0:1];
  reg [4:0] rd_m [0:1];
  reg [2:0] funct3_m [0:1];
  reg [1:0] result_src_m [0:1];
  reg valid_m [0:1], write_m [0:1], store_m [0:1];

  reg [31:0] alu_w [0:1], load_w [0:1], pc4_w [0:1], pc_w [0:1];
  reg [4:0] rd_w [0:1];
  reg [1:0] result_src_w [0:1];
  reg valid_w [0:1], write_w [0:1];
  assign wb_value[0] = result_src_w[0]==1 ? load_w[0] :
      result_src_w[0]==2 ? pc4_w[0] : alu_w[0];
  assign wb_value[1] = result_src_w[1]==1 ? load_w[1] :
      result_src_w[1]==2 ? pc4_w[1] : alu_w[1];

  regfile_dual rf(.clk(clk),
    .we0(valid_w[0] && write_w[0] && !reset),
    .we1(valid_w[1] && write_w[1] && !reset),
    .ra0(rs1_d[0]), .rb0(rs2_d[0]),
    .ra1(rs1_d[1]), .rb1(rs2_d[1]),
    .wa0(rd_w[0]), .wa1(rd_w[1]),
    .wd0(wb_value[0]), .wd1(wb_value[1]),
    .rd0a(ra_d[0]), .rd0b(rb_d[0]),
    .rd1a(ra_d[1]), .rd1b(rb_d[1]));

  wire issue0, issue1, issue1_candidate;
  wire stall_load, split_raw, split_resource;
  issueunit iu(.valid0(valid_d[0]), .valid1(valid_d[1]),
    .rs10(rs1_d[0]), .rs20(rs2_d[0]), .rd0(rd_d[0]),
    .rs11(rs1_d[1]), .rs21(rs2_d[1]),
    .uses10(uses1_d[0]), .uses20(uses2_d[0]),
    .uses11(uses1_d[1]), .uses21(uses2_d[1]),
    .writes0(write_d[0]), .mem0(mem_d[0]),
    .control0(control_d[0]), .mem1(mem_d[1]),
    .control1(control_d[1]),
    .load_e0(valid_e[0] && result_src_e[0]==1 && write_e[0]),
    .load_e1(valid_e[1] && result_src_e[1]==1 && write_e[1]),
    .rd_e0(rd_e[0]), .rd_e1(rd_e[1]),
    .issue0(issue0), .issue1(issue1_candidate), .stall_load(stall_load),
    .split_raw(split_raw), .split_resource(split_resource));
  // Do not pair a predicted control instruction with its target in the same
  // cycle; the branch outcome is still unknown until EX.
  assign issue1 = issue1_candidate && !pred_taken_d[0];

  wire [31:0] forward_m [0:1];
  assign forward_m[0] = result_src_m[0]==2 ? pc4_m[0] : alu_m[0];
  assign forward_m[1] = result_src_m[1]==2 ? pc4_m[1] : alu_m[1];
  wire [31:0] srca_e [0:1], srcb_e [0:1], alu_result_e [0:1];
  wire [2:0] forward_a [0:1], forward_b [0:1];
  wire branch_taken_e [0:1];
  generate for (g=0; g<2; g=g+1) begin: execute
    forward_dual fa(.rs(rs1_e[g]), .raw(ra_e[g]),
      .vm1(valid_m[1]), .wm1(write_m[1]), .lm1(result_src_m[1]==1),
      .rm1(rd_m[1]), .dm1(forward_m[1]),
      .vm0(valid_m[0]), .wm0(write_m[0]), .lm0(result_src_m[0]==1),
      .rm0(rd_m[0]), .dm0(forward_m[0]),
      .vw1(valid_w[1]), .ww1(write_w[1]), .rw1(rd_w[1]),
      .dw1(wb_value[1]), .vw0(valid_w[0]), .ww0(write_w[0]),
      .rw0(rd_w[0]), .dw0(wb_value[0]),
      .value(srca_e[g]), .select_src(forward_a[g]));
    forward_dual fb(.rs(rs2_e[g]), .raw(rb_e[g]),
      .vm1(valid_m[1]), .wm1(write_m[1]), .lm1(result_src_m[1]==1),
      .rm1(rd_m[1]), .dm1(forward_m[1]),
      .vm0(valid_m[0]), .wm0(write_m[0]), .lm0(result_src_m[0]==1),
      .rm0(rd_m[0]), .dm0(forward_m[0]),
      .vw1(valid_w[1]), .ww1(write_w[1]), .rw1(rd_w[1]),
      .dw1(wb_value[1]), .vw0(valid_w[0]), .ww0(write_w[0]),
      .rw0(rd_w[0]), .dw0(wb_value[0]),
      .value(srcb_e[g]), .select_src(forward_b[g]));
    wire [31:0] alu_a = srca_sel_e[g]==1 ? pc_e[g] :
        srca_sel_e[g]==2 ? 32'd0 : srca_e[g];
    wire [31:0] alu_b = alusrc_e[g] ? imm_e[g] : srcb_e[g];
    alu a(.a(alu_a), .b(alu_b), .alucontrol(alu_ctrl_e[g]),
      .result(alu_result_e[g]), .zero());
  end endgenerate

  // Exactly one shared branch comparator and target adder. Issue prevents
  // two control operations in one pair; the older lane wins defensively.
  wire control_e0 = valid_e[0] && (branch_e[0] || jump_e[0]);
  wire control_e1 = valid_e[1] && (branch_e[1] || jump_e[1]);
  wire select_control1 = !control_e0 && control_e1;
  wire [31:0] branch_a = select_control1 ? srca_e[1] : srca_e[0];
  wire [31:0] branch_b = select_control1 ? srcb_e[1] : srcb_e[0];
  wire [2:0] branch_funct3 = select_control1 ? funct3_e[1] : funct3_e[0];
  wire [31:0] branch_pc = select_control1 ? pc_e[1] : pc_e[0];
  wire [31:0] branch_imm = select_control1 ? imm_e[1] : imm_e[0];
  wire branch_jumpreg = select_control1 ? jumpreg_e[1] : jumpreg_e[0];
  wire [31:0] branch_alu_result = select_control1 ?
      alu_result_e[1] : alu_result_e[0];
  wire shared_branch_taken =
      branch_funct3==3'b000 ? (branch_a==branch_b) :
      branch_funct3==3'b001 ? (branch_a!=branch_b) :
      branch_funct3==3'b100 ? ($signed(branch_a)<$signed(branch_b)) :
      branch_funct3==3'b101 ? ($signed(branch_a)>=$signed(branch_b)) :
      branch_funct3==3'b110 ? (branch_a<branch_b) :
      branch_funct3==3'b111 ? (branch_a>=branch_b) : 1'b0;
  wire [31:0] shared_target = branch_jumpreg ?
      (branch_alu_result & 32'hfffffffe) : branch_pc+branch_imm;
  assign branch_taken_e[0] = !select_control1 && shared_branch_taken;
  assign branch_taken_e[1] = select_control1 && shared_branch_taken;
  wire taken0 = valid_e[0] && (jump_e[0] ||
      (branch_e[0] && branch_taken_e[0]));
  wire taken1 = valid_e[1] && !taken0 && (jump_e[1] ||
      (branch_e[1] && branch_taken_e[1]));
  wire control_resolved = control_e0 || control_e1;
  wire actual_taken = taken0 || taken1;
  wire [31:0] actual_next_pc = actual_taken ?
      shared_target : branch_pc+32'd4;
  wire [31:0] predicted_next_pc = select_control1 ?
      pred_next_e[1] : pred_next_e[0];
  wire mispredict0 = control_e0 && predicted_next_pc != actual_next_pc;
  wire mispredict1 = control_e1 && predicted_next_pc != actual_next_pc;
  wire redirect = mispredict0 || mispredict1;
  wire [31:0] redirect_pc = actual_next_pc;
  btb predictor(.clk(clk), .reset(reset),
    .pc0(fetch_pc), .pc1(fetch_pc+32'd4),
    .hit0(btb_hit0), .hit1(btb_hit1),
    .predict0(predict0), .predict1(predict1),
    .target0(btb_target0), .target1(btb_target1),
    .resolve_valid(control_resolved), .resolve_taken(actual_taken),
    .resolve_jump(select_control1 ? jump_e[1] : jump_e[0]),
    .resolve_pc(branch_pc), .resolve_target(shared_target));

  // One data-memory port, selected by valid operation (either lane).
  wire mem_lane1 = !(valid_m[0] && (store_m[0] || result_src_m[0]==1)) &&
      valid_m[1] && (store_m[1] || result_src_m[1]==1);
  wire [31:0] mem_address = mem_lane1 ? alu_m[1] : alu_m[0];
  wire [31:0] mem_store_data = mem_lane1 ? store_data_m[1] : store_data_m[0];
  wire [2:0] mem_funct3 = mem_lane1 ? funct3_m[1] : funct3_m[0];
  wire mem_write = !reset && ((valid_m[0] && store_m[0]) ||
      (valid_m[1] && store_m[1]));
  wire [31:0] mem_read;
  dmem dm(.clk(clk), .we(mem_write), .a(mem_address),
    .wd(mem_store_data), .funct3(mem_funct3), .rd(mem_read));

  reg [31:0] cycle_count, retired_count, double_issue_count;
  reg [31:0] stall_count, split_count;
  reg [31:0] btb_prediction_count, btb_correct_count, btb_mispredict_count;
  integer k;
  always @(posedge clk or posedge reset) begin
    if (reset) begin
      fetch_pc <= 0;
      cycle_count <= 0; retired_count <= 0; double_issue_count <= 0;
      stall_count <= 0; split_count <= 0;
      btb_prediction_count <= 0; btb_correct_count <= 0;
      btb_mispredict_count <= 0;
      for (k=0; k<2; k=k+1) begin
        instr_d[k] <= NOP; pc_d[k] <= 0; valid_d[k] <= 0;
        pred_next_d[k] <= 0; pred_next_e[k] <= 0;
        pred_taken_d[k] <= 0;
        pc_e[k] <= 0; ra_e[k] <= 0; rb_e[k] <= 0; imm_e[k] <= 0;
        rs1_e[k] <= 0; rs2_e[k] <= 0; rd_e[k] <= 0;
        alu_ctrl_e[k] <= 0; funct3_e[k] <= 0;
        result_src_e[k] <= 0; srca_sel_e[k] <= 0;
        valid_e[k] <= 0; write_e[k] <= 0; store_e[k] <= 0;
        branch_e[k] <= 0; jump_e[k] <= 0; jumpreg_e[k] <= 0;
        alusrc_e[k] <= 0;
        alu_m[k] <= 0; store_data_m[k] <= 0; pc4_m[k] <= 0; pc_m[k] <= 0;
        rd_m[k] <= 0; funct3_m[k] <= 0; result_src_m[k] <= 0;
        valid_m[k] <= 0; write_m[k] <= 0; store_m[k] <= 0;
        alu_w[k] <= 0; load_w[k] <= 0; pc4_w[k] <= 0; pc_w[k] <= 0;
        rd_w[k] <= 0; result_src_w[k] <= 0;
        valid_w[k] <= 0; write_w[k] <= 0;
      end
    end else begin
      cycle_count <= cycle_count + 1;
      retired_count <= retired_count + valid_w[0] + valid_w[1];
      if (issue1 && !redirect) double_issue_count <= double_issue_count + 1;
      if (stall_load && !redirect) stall_count <= stall_count + 1;
      if (issue0 && !issue1 && valid_d[1] && !redirect)
        split_count <= split_count + 1;
      if (control_resolved) begin
        if (predicted_next_pc != branch_pc+32'd4)
          btb_prediction_count <= btb_prediction_count + 1;
        if (!redirect) btb_correct_count <= btb_correct_count + 1;
        else btb_mispredict_count <= btb_mispredict_count + 1;
      end

      // MEM/WB: only the selected lane can have a load.
      for (k=0; k<2; k=k+1) begin
        alu_w[k] <= alu_m[k]; pc4_w[k] <= pc4_m[k]; pc_w[k] <= pc_m[k];
        rd_w[k] <= rd_m[k];
        result_src_w[k] <= result_src_m[k];
        valid_w[k] <= valid_m[k]; write_w[k] <= write_m[k];
        load_w[k] <= mem_read;
      end

      // EX/MEM: a taken branch in the older lane kills only its younger mate.
      for (k=0; k<2; k=k+1) begin
        alu_m[k] <= alu_result_e[k]; store_data_m[k] <= srcb_e[k];
        pc4_m[k] <= pc_e[k]+32'd4; pc_m[k] <= pc_e[k]; rd_m[k] <= rd_e[k];
        funct3_m[k] <= funct3_e[k]; result_src_m[k] <= result_src_e[k];
        valid_m[k] <= valid_e[k] && !(k==1 && mispredict0);
        write_m[k] <= write_e[k] && !(k==1 && mispredict0);
        store_m[k] <= store_e[k] && !(k==1 && mispredict0);
      end

      // A redirect discards only younger work in ID. Existing older M/W survives.
      if (redirect) begin
        fetch_pc <= redirect_pc;
        for (k=0; k<2; k=k+1) begin
          instr_d[k] <= NOP; pc_d[k] <= 0; valid_d[k] <= 0;
          pred_next_d[k] <= 0; pred_taken_d[k] <= 0;
          valid_e[k] <= 0; write_e[k] <= 0; store_e[k] <= 0;
          branch_e[k] <= 0; jump_e[k] <= 0;
        end
      end else begin
        for (k=0; k<2; k=k+1) begin
          valid_e[k] <= k==0 ? issue0 : issue1;
          write_e[k] <= (k==0 ? issue0 : issue1) && write_d[k];
          store_e[k] <= (k==0 ? issue0 : issue1) && store_d[k];
          branch_e[k] <= (k==0 ? issue0 : issue1) && branch_d[k];
          jump_e[k] <= (k==0 ? issue0 : issue1) && jump_d[k];
          jumpreg_e[k] <= jumpreg_d[k]; alusrc_e[k] <= alusrc_d[k];
          pc_e[k] <= pc_d[k]; ra_e[k] <= ra_d[k]; rb_e[k] <= rb_d[k];
          imm_e[k] <= imm_d[k]; rs1_e[k] <= rs1_d[k];
          rs2_e[k] <= rs2_d[k]; rd_e[k] <= rd_d[k];
          alu_ctrl_e[k] <= alu_ctrl_d[k]; funct3_e[k] <= instr_d[k][14:12];
          result_src_e[k] <= result_src_d[k]; srca_sel_e[k] <= srca_sel_d[k];
          pred_next_e[k] <= pred_next_d[k];
        end
        if (!valid_d[0] || (issue0 && !valid_d[1])) begin
          instr_d[0] <= fetch0; instr_d[1] <= fetch1;
          pc_d[0] <= fetch_pc; pc_d[1] <= fetch_pc+32'd4;
          pred_next_d[0] <= fetch_next0;
          pred_next_d[1] <= fetch_next1;
          pred_taken_d[0] <= predict0;
          pred_taken_d[1] <= predict1;
          valid_d[0] <= 1; valid_d[1] <= !predict0;
          fetch_pc <= predict0 ? btb_target0 : fetch_next1;
        end else if (issue1) begin
          instr_d[0] <= fetch0; instr_d[1] <= fetch1;
          pc_d[0] <= fetch_pc; pc_d[1] <= fetch_pc+32'd4;
          pred_next_d[0] <= fetch_next0;
          pred_next_d[1] <= fetch_next1;
          pred_taken_d[0] <= predict0;
          pred_taken_d[1] <= predict1;
          valid_d[0] <= 1; valid_d[1] <= !predict0;
          fetch_pc <= predict0 ? btb_target0 : fetch_next1;
        end else if (issue0) begin
          instr_d[0] <= instr_d[1]; pc_d[0] <= pc_d[1];
          pred_next_d[0] <= pred_next_d[1];
          pred_taken_d[0] <= pred_taken_d[1];
          valid_d[0] <= valid_d[1];
          instr_d[1] <= fetch0; pc_d[1] <= fetch_pc; valid_d[1] <= 1;
          pred_next_d[1] <= fetch_next0;
          pred_taken_d[1] <= predict0;
          fetch_pc <= fetch_next0;
        end
      end
    end
  end
endmodule
