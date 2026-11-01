// E1 preview of the second lane. Fetches and decodes an aligned pair and
// carries both sets of operands/control into EX. No Issue Unit, WB, shared
// memory scheduling, or branch handling yet: this is NOT a functional B core.
module dualissue_prelim(
    input clk, reset, hold, flush,
    input [31:0] redirect_pc,
    output [31:0] PC0_F, PC1_F, Instr0_D, Instr1_D,
    output [31:0] PC0_E, PC1_E, ALUResult0_E, ALUResult1_E,
    output Valid0_E, Valid1_E
);
  reg [31:0] pc_reg;
  reg [31:0] instr0_d_reg, instr1_d_reg, pc0_d_reg, pc1_d_reg;
  reg valid0_d_reg, valid1_d_reg;
  assign PC0_F = pc_reg;
  assign PC1_F = pc_reg + 32'd4;
  assign Instr0_D = instr0_d_reg;
  assign Instr1_D = instr1_d_reg;
  wire [31:0] instr0_f, instr1_f;
  imem fetch_mem(.a(PC0_F), .a2(PC1_F), .rd(instr0_f), .rd2(instr1_f));

  wire [1:0] result0_d, result1_d;
  wire [2:0] imm0_src_d, imm1_src_d;
  wire [3:0] alu0_ctrl_d, alu1_ctrl_d;
  wire mem0_d, mem1_d, branch0_d, branch1_d, jump0_d, jump1_d;
  wire alu0_src_d, alu1_src_d, write0_d, write1_d;
  controller decode0(.op(Instr0_D[6:0]), .funct3(Instr0_D[14:12]),
    .funct7b5(Instr0_D[30]), .ResultSrc(result0_d), .MemWrite(mem0_d),
    .Branch(branch0_d), .Jump(jump0_d), .ALUSrc(alu0_src_d),
    .RegWrite(write0_d), .ImmSrc(imm0_src_d), .ALUControl(alu0_ctrl_d));
  controller decode1(.op(Instr1_D[6:0]), .funct3(Instr1_D[14:12]),
    .funct7b5(Instr1_D[30]), .ResultSrc(result1_d), .MemWrite(mem1_d),
    .Branch(branch1_d), .Jump(jump1_d), .ALUSrc(alu1_src_d),
    .RegWrite(write1_d), .ImmSrc(imm1_src_d), .ALUControl(alu1_ctrl_d));

  wire [31:0] ra0_d, rb0_d, ra1_d, rb1_d, imm0_d, imm1_d;
  regfile_dual rf(.clk(clk), .we0(1'b0), .we1(1'b0),
    .ra0(Instr0_D[19:15]), .rb0(Instr0_D[24:20]),
    .ra1(Instr1_D[19:15]), .rb1(Instr1_D[24:20]),
    .wa0(5'b0), .wa1(5'b0), .wd0(32'b0), .wd1(32'b0),
    .rd0a(ra0_d), .rd0b(rb0_d), .rd1a(ra1_d), .rd1b(rb1_d));
  extend imm0(.instr(Instr0_D[31:7]), .immsrc(imm0_src_d), .immext(imm0_d));
  extend imm1(.instr(Instr1_D[31:7]), .immsrc(imm1_src_d), .immext(imm1_d));

  reg [31:0] pc0_e_reg, pc1_e_reg, ra0_e, rb0_e, ra1_e, rb1_e, imm0_e, imm1_e;
  reg [3:0] alu0_ctrl_e, alu1_ctrl_e;
  reg alu0_src_e, alu1_src_e, valid0_e_reg, valid1_e_reg;
  assign PC0_E = pc0_e_reg;
  assign PC1_E = pc1_e_reg;
  assign Valid0_E = valid0_e_reg;
  assign Valid1_E = valid1_e_reg;
  wire zero0, zero1;
  alu lane0_alu(.a(ra0_e), .b(alu0_src_e ? imm0_e : rb0_e),
    .alucontrol(alu0_ctrl_e), .result(ALUResult0_E), .zero(zero0));
  alu lane1_alu(.a(ra1_e), .b(alu1_src_e ? imm1_e : rb1_e),
    .alucontrol(alu1_ctrl_e), .result(ALUResult1_E), .zero(zero1));

  always @(posedge clk or posedge reset) begin
    if (reset) begin
      pc_reg <= 0;
      instr0_d_reg <= 32'h00000013; instr1_d_reg <= 32'h00000013;
      pc0_d_reg <= 0; pc1_d_reg <= 0;
      valid0_d_reg <= 0; valid1_d_reg <= 0;
      pc0_e_reg <= 0; pc1_e_reg <= 0;
      ra0_e <= 0; rb0_e <= 0; ra1_e <= 0; rb1_e <= 0;
      imm0_e <= 0; imm1_e <= 0; alu0_ctrl_e <= 0; alu1_ctrl_e <= 0;
      alu0_src_e <= 0; alu1_src_e <= 0;
      valid0_e_reg <= 0; valid1_e_reg <= 0;
    end else if (flush) begin
      pc_reg <= redirect_pc;
      instr0_d_reg <= 32'h00000013; instr1_d_reg <= 32'h00000013;
      pc0_d_reg <= 0; pc1_d_reg <= 0;
      valid0_d_reg <= 0; valid1_d_reg <= 0;
      valid0_e_reg <= 0; valid1_e_reg <= 0;
    end else begin
      if (!hold) begin
        pc_reg <= pc_reg + 32'd8;
        instr0_d_reg <= instr0_f; instr1_d_reg <= instr1_f;
        pc0_d_reg <= PC0_F; pc1_d_reg <= PC1_F;
        valid0_d_reg <= 1; valid1_d_reg <= 1;
      end
      // A held pair waits in ID; EX receives a bubble.
      valid0_e_reg <= valid0_d_reg && !hold;
      valid1_e_reg <= valid1_d_reg && !hold;
      if (!hold) begin
        pc0_e_reg <= pc0_d_reg; pc1_e_reg <= pc1_d_reg;
        ra0_e <= ra0_d; rb0_e <= rb0_d; ra1_e <= ra1_d; rb1_e <= rb1_d;
        imm0_e <= imm0_d; imm1_e <= imm1_d;
        alu0_ctrl_e <= alu0_ctrl_d; alu1_ctrl_e <= alu1_ctrl_d;
        alu0_src_e <= alu0_src_d; alu1_src_e <= alu1_src_d;
      end
    end
  end
endmodule
