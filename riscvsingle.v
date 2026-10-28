module riscvpipelined(
    input         clk, reset,
    output [31:0] PC,
    input  [31:0] Instr,
    output        MemWrite,
    output [31:0] DataAdr, 
    output [31:0] WriteData,
    input  [31:0] ReadData
);

  wire       ALUSrc, RegWrite, Jump, Branch; 
  wire [1:0] ResultSrc, ImmSrc; 
  wire [2:0] ALUControl; 
  wire [31:0] Instr_D; // Instrucción que está en la etapa Decode

  // La unidad de control recibe los campos de la instrucción en etapa DECODE (Instr_D)
  controller c(
    .op(Instr_D[6:0]), 
    .funct3(Instr_D[14:12]), 
    .funct7b5(Instr_D[30]), 
    .ResultSrc(ResultSrc), 
    .MemWrite(MemWrite), 
    .ALUSrc(ALUSrc), 
    .RegWrite(RegWrite), 
    .Jump(Jump),
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
    .RegWrite(RegWrite),
    .ImmSrc(ImmSrc), 
    .ALUControl(ALUControl),
    .Branch(Branch),
    .Jump(Jump),
    .PC(PC), 
    .Instr(Instr),
    .Instr_D(Instr_D),       // Salida de IF/ID entregada al controller
    .ALUResult(DataAdr),     // Salida de la etapa MEM para dmem
    .WriteData(WriteData),   // Salida de la etapa MEM para dmem
    .ReadData(ReadData)
  ); 

endmodule