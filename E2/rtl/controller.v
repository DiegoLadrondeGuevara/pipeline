module controller(input [6:0] op,
                  input [2:0] funct3,
                  input funct7b5,
                  output [1:0] ResultSrc, SrcASel,
                  output MemWrite, Branch, Jump, JumpReg,
                  output ALUSrc, RegWrite,
                  output [2:0] ImmSrc,
                  output [3:0] ALUControl);
  wire [1:0] ALUOp;
  maindec md(.op(op), .ResultSrc(ResultSrc), .SrcASel(SrcASel),
             .MemWrite(MemWrite), .Branch(Branch), .Jump(Jump),
             .JumpReg(JumpReg), .ALUSrc(ALUSrc), .RegWrite(RegWrite),
             .ImmSrc(ImmSrc), .ALUOp(ALUOp));
  aludec ad(.opb5(op[5]), .funct3(funct3), .funct7b5(funct7b5),
            .ALUOp(ALUOp), .ALUControl(ALUControl));
endmodule
