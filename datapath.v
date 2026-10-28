module datapath(
    input  clk, reset,
    // Señales de control recibidas de la unidad de control
    input  [1:0] ResultSrc, 
    input  ALUSrc,
    input  RegWrite,
    input  [1:0] ImmSrc, 
    input  [2:0] ALUControl,
    input  Branch, Jump,         // Entradas de control para saltos

    output Zero,
    output [31:0] PC,
    input  [31:0] Instr,
    output [31:0] Instr_D,       // Salida enviada a Decode / Controller
    output [31:0] ALUResult, WriteData, 
    input  [31:0] ReadData
);

  localparam WIDTH = 32;

  // =========================================================================
  // ETAPA 1: FETCH (IF)
  // =========================================================================
  wire [31:0] PCNext, PCPlus4_F;
  wire [31:0] PCTarget_E; // Proviene de la etapa EX
  wire        PCSrc_E;    // Evaluado en la etapa EX

  flopr #(WIDTH) pcreg(
    .clk(clk), 
    .reset(reset), 
    .d(PCNext), 
    .q(PC)
  ); 

  adder pcadd4(
    .a(PC), 
    .b(32'd4), 
    .y(PCPlus4_F)
  ); 

  mux2 #(WIDTH) pcmux(
    .d0(PCPlus4_F), 
    .d1(PCTarget_E), 
    .s(PCSrc_E), 
    .y(PCNext)
  ); 

  // -------------------------------------------------------------------------
  // PIPELINE REGISTER: IF / ID
  // -------------------------------------------------------------------------
  wire [31:0] PC_D, PCPlus4_D;

  flopr #(WIDTH) reg_if_id_instr (.clk(clk), .reset(reset), .d(Instr),     .q(Instr_D));
  flopr #(WIDTH) reg_if_id_pc    (.clk(clk), .reset(reset), .d(PC),        .q(PC_D));
  flopr #(WIDTH) reg_if_id_pc4   (.clk(clk), .reset(reset), .d(PCPlus4_F), .q(PCPlus4_D));

  // =========================================================================
  // ETAPA 2: DECODE (ID)
  // =========================================================================
  wire [31:0] RD1_D, RD2_D, ImmExt_D;
  wire [4:0]  Rd_D = Instr_D[11:7];
  
  // Conexiones que vienen desde la etapa WB para el banco de registros
  wire [31:0] Result_W;
  wire [4:0]  Rd_W;
  wire        RegWrite_W;

  regfile rf(
    .clk(clk), 
    .we3(RegWrite_W), 
    .a1(Instr_D[19:15]), 
    .a2(Instr_D[24:20]), 
    .a3(Rd_W), 
    .wd3(Result_W), 
    .rd1(RD1_D), 
    .rd2(RD2_D)
  ); 

  extend ext(
    .instr(Instr_D[31:7]), 
    .immsrc(ImmSrc), 
    .immext(ImmExt_D)
  ); 

  // -------------------------------------------------------------------------
  // PIPELINE REGISTER: ID / EX
  // -------------------------------------------------------------------------
  // Datos
  wire [31:0] RD1_E, RD2_E, ImmExt_E, PC_E, PCPlus4_E;
  wire [4:0]  Rd_E;
  // Control
  wire        RegWrite_E, ALUSrc_E, Branch_E, Jump_E;
  wire [1:0]  ResultSrc_E;
  wire [2:0]  ALUControl_E;

  flopr #(WIDTH) reg_id_ex_rd1  (.clk(clk), .reset(reset), .d(RD1_D),      .q(RD1_E));
  flopr #(WIDTH) reg_id_ex_rd2  (.clk(clk), .reset(reset), .d(RD2_D),      .q(RD2_E));
  flopr #(WIDTH) reg_id_ex_pc   (.clk(clk), .reset(reset), .d(PC_D),       .q(PC_E));
  flopr #(WIDTH) reg_id_ex_imm  (.clk(clk), .reset(reset), .d(ImmExt_D),   .q(ImmExt_E));
  flopr #(WIDTH) reg_id_ex_pc4  (.clk(clk), .reset(reset), .d(PCPlus4_D),  .q(PCPlus4_E));
  flopr #(5)     reg_id_ex_rd   (.clk(clk), .reset(reset), .d(Rd_D),       .q(Rd_E));

  // Flip-flops de control
  flopr #(1) reg_id_ex_rw  (.clk(clk), .reset(reset), .d(RegWrite),   .q(RegWrite_E));
  flopr #(2) reg_id_ex_rs  (.clk(clk), .reset(reset), .d(ResultSrc),  .q(ResultSrc_E));
  flopr #(1) reg_id_ex_as  (.clk(clk), .reset(reset), .d(ALUSrc),     .q(ALUSrc_E));
  flopr #(3) reg_id_ex_ac  (.clk(clk), .reset(reset), .d(ALUControl), .q(ALUControl_E));
  flopr #(1) reg_id_ex_br  (.clk(clk), .reset(reset), .d(Branch),     .q(Branch_E));
  flopr #(1) reg_id_ex_jp  (.clk(clk), .reset(reset), .d(Jump),       .q(Jump_E));

  // =========================================================================
  // ETAPA 3: EXECUTE (EX)
  // =========================================================================
  wire [31:0] SrcB_E, ALUResult_E;

  adder pcaddbranch(
    .a(PC_E), 
    .b(ImmExt_E), 
    .y(PCTarget_E)
  ); 

  mux2 #(WIDTH) srcbmux(
    .d0(RD2_E), 
    .d1(ImmExt_E), 
    .s(ALUSrc_E), 
    .y(SrcB_E)
  ); 

  alu alu(
    .a(RD1_E), 
    .b(SrcB_E), 
    .alucontrol(ALUControl_E), 
    .result(ALUResult_E), 
    .zero(Zero)
  ); 

  // Decisión de salto calculada en EX
  assign PCSrc_E = (Branch_E & Zero) | Jump_E;

  // -------------------------------------------------------------------------
  // PIPELINE REGISTER: EX / MEM
  // -------------------------------------------------------------------------
  // Datos
  wire [31:0] ALUResult_M, WriteData_M, PCPlus4_M;
  wire [4:0]  Rd_M;
  // Control
  wire        RegWrite_M;
  wire [1:0]  ResultSrc_M;

  flopr #(WIDTH) reg_ex_mem_alu (.clk(clk), .reset(reset), .d(ALUResult_E), .q(ALUResult_M));
  flopr #(WIDTH) reg_ex_mem_wd  (.clk(clk), .reset(reset), .d(RD2_E),       .q(WriteData_M));
  flopr #(WIDTH) reg_ex_mem_pc4 (.clk(clk), .reset(reset), .d(PCPlus4_E),   .q(PCPlus4_M));
  flopr #(5)     reg_ex_mem_rd  (.clk(clk), .reset(reset), .d(Rd_E),        .q(Rd_M));

  // Flip-flops de control
  flopr #(1) reg_ex_mem_rw (.clk(clk), .reset(reset), .d(RegWrite_E),  .q(RegWrite_M));
  flopr #(2) reg_ex_mem_rs (.clk(clk), .reset(reset), .d(ResultSrc_E), .q(ResultSrc_M));

  // Conexiones hacia la Memoria de Datos externa
  assign ALUResult = ALUResult_M;
  assign WriteData = WriteData_M;

  // -------------------------------------------------------------------------
  // PIPELINE REGISTER: MEM / WB
  // -------------------------------------------------------------------------
  // Datos
  wire [31:0] ALUResult_W, ReadData_W, PCPlus4_W;
  // Control
  wire [1:0]  ResultSrc_W;

  flopr #(WIDTH) reg_mem_wb_alu (.clk(clk), .reset(reset), .d(ALUResult_M), .q(ALUResult_W));
  flopr #(WIDTH) reg_mem_wb_rd  (.clk(clk), .reset(reset), .d(ReadData),    .q(ReadData_W));
  flopr #(WIDTH) reg_mem_wb_pc4 (.clk(clk), .reset(reset), .d(PCPlus4_M),   .q(PCPlus4_W));
  flopr #(5)     reg_mem_wb_reg (.clk(clk), .reset(reset), .d(Rd_M),        .q(Rd_W));

  // Flip-flops de control
  flopr #(1) reg_mem_wb_rw (.clk(clk), .reset(reset), .d(RegWrite_M),  .q(RegWrite_W));
  flopr #(2) reg_mem_wb_rs (.clk(clk), .reset(reset), .d(ResultSrc_M), .q(ResultSrc_W));

  // =========================================================================
  // ETAPA 5: WRITEBACK (WB)
  // =========================================================================
  mux3 #(WIDTH) resultmux(
    .d0(ALUResult_W), 
    .d1(ReadData_W), 
    .d2(PCPlus4_W), 
    .s(ResultSrc_W), 
    .y(Result_W)
  ); 

endmodule