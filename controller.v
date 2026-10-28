module controller(
    input  [6:0] op,
    input  [2:0] funct3,
    input        funct7b5,
    // Eliminamos la entrada Zero porque la decisión de salto se evalúa en EX
    output [1:0] ResultSrc, 
    output MemWrite,
    output Branch, Jump,    // Ahora se entregan Branch y Jump al Datapath
    output ALUSrc,
    output RegWrite, 
    output [1:0] ImmSrc, 
    output [2:0] ALUControl
);

  wire [1:0] ALUOp; 

  // Decodificador Principal
  maindec md(
    .op(op), 
    .ResultSrc(ResultSrc), 
    .MemWrite(MemWrite), 
    .Branch(Branch),
    .ALUSrc(ALUSrc), 
    .RegWrite(RegWrite), 
    .Jump(Jump), 
    .ImmSrc(ImmSrc), 
    .ALUOp(ALUOp)
  ); 

  // Decodificador de ALU
  aludec ad(
    .opb5(op[5]), 
    .funct3(funct3), 
    .funct7b5(funct7b5), 
    .ALUOp(ALUOp), 
    .ALUControl(ALUControl)
  ); 

  // Nota: PCSrc ya no se calcula aquí, sino en la etapa EX del datapath
  // asignando: assign PCSrc_E = (Branch_E & Zero_E) | Jump_E;

endmodule