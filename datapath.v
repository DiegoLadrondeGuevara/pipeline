module datapath(
    input clk, reset,
    input [1:0] ResultSrc,
    input ALUSrc, RegWrite, MemWrite_D, Branch, Jump,
    input [1:0] ImmSrc,
    input [2:0] ALUControl,
    output [31:0] PC,
    input [31:0] Instr,
    output [31:0] Instr_D,
    output MemWrite,
    output [31:0] ALUResult, WriteData,
    input [31:0] ReadData
);
  // IF and IF/ID. A taken branch has priority over a load-use stall.
  reg [31:0] PC_F, Instr_D_reg, PC_D, PCPlus4_D;
  reg Valid_D;
  wire [31:0] PCPlus4_F = PC_F + 32'd4;
  assign PC = PC_F;
  assign Instr_D = Instr_D_reg;

  // Decode and hazard inputs.
  wire [4:0] Rs1_D = Instr_D[19:15];
  wire [4:0] Rs2_D = Instr_D[24:20];
  wire [4:0] Rd_D  = Instr_D[11:7];
  wire [6:0] Op_D  = Instr_D[6:0];
  wire UsesRs1_D = (Op_D == 7'b0110011) || (Op_D == 7'b0010011) ||
                   (Op_D == 7'b0000011) || (Op_D == 7'b0100011) ||
                   (Op_D == 7'b1100011);
  wire UsesRs2_D = (Op_D == 7'b0110011) || (Op_D == 7'b0100011) ||
                   (Op_D == 7'b1100011);
  wire [31:0] RD1_D, RD2_D, ImmExt_D;
  wire [31:0] Result_W;
  reg [4:0] Rd_W;
  wire RegWrite_W;
  regfile rf(.clk(clk), .we3(RegWrite_W), .a1(Rs1_D), .a2(Rs2_D),
             .a3(Rd_W), .wd3(Result_W), .rd1(RD1_D), .rd2(RD2_D));
  extend ext(.instr(Instr_D[31:7]), .immsrc(ImmSrc), .immext(ImmExt_D));

  // ID/EX. A bubble clears every side effect and the valid bit.
  reg [31:0] RD1_E, RD2_E, ImmExt_E, PC_E, PCPlus4_E;
  reg [4:0] Rs1_E, Rs2_E, Rd_E;
  reg [2:0] ALUControl_E;
  reg [1:0] ResultSrc_E;
  reg RegWrite_E, MemWrite_E, ALUSrc_E, Branch_E, Jump_E, Valid_E;

  // EX/MEM and MEM/WB.
  reg [31:0] ALUResult_M, WriteData_M, PCPlus4_M;
  reg [4:0] Rd_M;
  reg [1:0] ResultSrc_M;
  reg RegWrite_M, MemWrite_M, Valid_M;
  reg [31:0] ALUResult_W, ReadData_W, PCPlus4_W;
  reg [1:0] ResultSrc_W;
  reg Valid_W, RegWrite_W_reg;

  wire [1:0] ForwardAE, ForwardBE;
  wire Stall_D;
  wire PCSrc_E;
  hazardunit hu(
    .Valid_D(Valid_D), .UsesRs1_D(UsesRs1_D), .UsesRs2_D(UsesRs2_D),
    .Rs1_D(Rs1_D), .Rs2_D(Rs2_D),
    .Valid_E(Valid_E), .Rs1_E(Rs1_E), .Rs2_E(Rs2_E),
    .Rd_E(Rd_E), .RegWrite_E(RegWrite_E), .ResultSrc_E(ResultSrc_E),
    .Valid_M(Valid_M), .Rd_M(Rd_M), .RegWrite_M(RegWrite_M),
    .ResultSrc_M(ResultSrc_M),
    .Valid_W(Valid_W), .Rd_W(Rd_W), .RegWrite_W(RegWrite_W),
    .Stall_D(Stall_D), .ForwardAE(ForwardAE), .ForwardBE(ForwardBE)
  );

  // A load in MEM is unavailable for EX forwarding. JAL forwards PC+4.
  wire [31:0] ForwardResult_M = (ResultSrc_M == 2'b10) ?
                                 PCPlus4_M : ALUResult_M;
  wire [31:0] SrcA_E = (ForwardAE == 2'b10) ? ForwardResult_M :
                       (ForwardAE == 2'b01) ? Result_W : RD1_E;
  wire [31:0] ForwardedB_E = (ForwardBE == 2'b10) ? ForwardResult_M :
                             (ForwardBE == 2'b01) ? Result_W : RD2_E;
  wire [31:0] SrcB_E = ALUSrc_E ? ImmExt_E : ForwardedB_E;
  wire [31:0] ALUResult_E;
  wire Zero_E;
  wire [31:0] PCTarget_E = PC_E + ImmExt_E;
  alu exec_alu(.a(SrcA_E), .b(SrcB_E), .alucontrol(ALUControl_E),
               .result(ALUResult_E), .zero(Zero_E));
  assign PCSrc_E = Valid_E && (Jump_E || (Branch_E && Zero_E));

  assign ALUResult = ALUResult_M;
  assign WriteData = WriteData_M;
  assign MemWrite = Valid_M && MemWrite_M && !reset;
  assign RegWrite_W = Valid_W && RegWrite_W_reg && !reset;
  assign Result_W = (ResultSrc_W == 2'b01) ? ReadData_W :
                    (ResultSrc_W == 2'b10) ? PCPlus4_W : ALUResult_W;

  always @(posedge clk or posedge reset) begin
    if (reset) begin
      PC_F <= 0;
      Instr_D_reg <= 32'h00000013; PC_D <= 0; PCPlus4_D <= 0; Valid_D <= 0;
      RD1_E <= 0; RD2_E <= 0; ImmExt_E <= 0; PC_E <= 0; PCPlus4_E <= 0;
      Rs1_E <= 0; Rs2_E <= 0; Rd_E <= 0; ALUControl_E <= 0;
      ResultSrc_E <= 0; RegWrite_E <= 0; MemWrite_E <= 0;
      ALUSrc_E <= 0; Branch_E <= 0; Jump_E <= 0; Valid_E <= 0;
      ALUResult_M <= 0; WriteData_M <= 0; PCPlus4_M <= 0; Rd_M <= 0;
      ResultSrc_M <= 0; RegWrite_M <= 0; MemWrite_M <= 0; Valid_M <= 0;
      ALUResult_W <= 0; ReadData_W <= 0; PCPlus4_W <= 0; Rd_W <= 0;
      ResultSrc_W <= 0; RegWrite_W_reg <= 0; Valid_W <= 0;
    end else begin
      if (PCSrc_E) PC_F <= PCTarget_E;
      else if (!Stall_D) PC_F <= PCPlus4_F;

      if (PCSrc_E) begin
        Instr_D_reg <= 32'h00000013; PC_D <= 0; PCPlus4_D <= 0; Valid_D <= 0;
      end else if (!Stall_D) begin
        Instr_D_reg <= Instr; PC_D <= PC_F;
        PCPlus4_D <= PCPlus4_F; Valid_D <= 1;
      end

      if (PCSrc_E || Stall_D) begin
        RD1_E <= 0; RD2_E <= 0; ImmExt_E <= 0; PC_E <= 0; PCPlus4_E <= 0;
        Rs1_E <= 0; Rs2_E <= 0; Rd_E <= 0; ALUControl_E <= 0;
        ResultSrc_E <= 0; RegWrite_E <= 0; MemWrite_E <= 0;
        ALUSrc_E <= 0; Branch_E <= 0; Jump_E <= 0; Valid_E <= 0;
      end else begin
        RD1_E <= RD1_D; RD2_E <= RD2_D; ImmExt_E <= ImmExt_D;
        PC_E <= PC_D; PCPlus4_E <= PCPlus4_D;
        Rs1_E <= Rs1_D; Rs2_E <= Rs2_D; Rd_E <= Rd_D;
        ALUControl_E <= ALUControl; ResultSrc_E <= ResultSrc;
        RegWrite_E <= RegWrite && Valid_D;
        MemWrite_E <= MemWrite_D && Valid_D;
        ALUSrc_E <= ALUSrc; Branch_E <= Branch && Valid_D;
        Jump_E <= Jump && Valid_D; Valid_E <= Valid_D;
      end

      ALUResult_M <= ALUResult_E;
      WriteData_M <= ForwardedB_E; // Includes store-data forwarding.
      PCPlus4_M <= PCPlus4_E; Rd_M <= Rd_E; ResultSrc_M <= ResultSrc_E;
      RegWrite_M <= RegWrite_E; MemWrite_M <= MemWrite_E; Valid_M <= Valid_E;

      ALUResult_W <= ALUResult_M; ReadData_W <= ReadData;
      PCPlus4_W <= PCPlus4_M; Rd_W <= Rd_M; ResultSrc_W <= ResultSrc_M;
      RegWrite_W_reg <= RegWrite_M; Valid_W <= Valid_M;
    end
  end
endmodule
