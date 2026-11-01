module riscvpipelined(
    input         clk, reset,
    output [31:0] PC,
    input  [31:0] Instr,
    output        MemWrite,
    output [31:0] DataAdr, 
    output [31:0] WriteData,
    output [2:0] MemFunct3,
    input  [31:0] ReadData
);

  wire       ALUSrc, RegWrite, Jump, JumpReg, Branch, MemWrite_D;
  wire [1:0] ResultSrc, SrcASel;
  wire [2:0] ImmSrc;
  wire [3:0] ALUControl;
  wire [31:0] Instr_D; // Instrucción que está en la etapa Decode

  // La unidad de control recibe los campos de la instrucción en etapa DECODE (Instr_D)
  controller c(
    .op(Instr_D[6:0]), 
    .funct3(Instr_D[14:12]), 
    .funct7b5(Instr_D[30]), 
    .ResultSrc(ResultSrc), 
    .SrcASel(SrcASel),
    .MemWrite(MemWrite_D),
    .ALUSrc(ALUSrc), 
    .RegWrite(RegWrite), 
    .Jump(Jump),
    .JumpReg(JumpReg),
    .Branch(Branch),
    .ImmSrc(ImmSrc), 
    .ALUControl(ALUControl)
  ); 
  
  // El datapath procesa datos y propaga las señales de control por las 5 etapas
  datapath dp(
    .clk(clk), 
    .reset(reset), 
    .ResultSrc(ResultSrc), 
    .ALUSrc(ALUSrc), 
    .SrcASel(SrcASel),
    .RegWrite(RegWrite),
    .MemWrite_D(MemWrite_D),
    .ImmSrc(ImmSrc), 
    .MemFunct3_D(Instr_D[14:12]),
    .ALUControl(ALUControl),
    .Branch(Branch),
    .Jump(Jump),
    .JumpReg(JumpReg),
    .PC(PC), 
    .Instr(Instr),
    .Instr_D(Instr_D),       // Salida de IF/ID entregada al controller
    .MemWrite(MemWrite),
    .MemFunct3_M(MemFunct3),
    .ALUResult(DataAdr),     // Salida de la etapa MEM para dmem
    .WriteData(WriteData),   // Salida de la etapa MEM para dmem
    .ReadData(ReadData)
  ); 

endmodule
