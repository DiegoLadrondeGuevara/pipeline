module maindec(input [6:0] op,
               output reg [1:0] ResultSrc, SrcASel,
               output reg [2:0] ImmSrc,
               output reg MemWrite, Branch, ALUSrc, RegWrite, Jump, JumpReg,
               output reg [1:0] ALUOp);
  // SrcASel: register=0, PC=1, zero=2. ResultSrc: ALU=0, load=1, PC+4=2.
  always @* begin
    ResultSrc=0; SrcASel=0; ImmSrc=0; MemWrite=0; Branch=0;
    ALUSrc=0; RegWrite=0; Jump=0; JumpReg=0; ALUOp=0;
    case (op)
      7'b0000011: begin RegWrite=1; ALUSrc=1; ResultSrc=1; end
      7'b0100011: begin MemWrite=1; ALUSrc=1; ImmSrc=1; end
      7'b0110011: begin RegWrite=1; ALUOp=2; end
      7'b0010011: begin RegWrite=1; ALUSrc=1; ALUOp=2; end
      7'b1100011: begin Branch=1; ImmSrc=2; ALUOp=1; end
      7'b1101111: begin RegWrite=1; Jump=1; ImmSrc=3; ResultSrc=2; end
      7'b1100111: begin RegWrite=1; Jump=1; JumpReg=1; ALUSrc=1; ResultSrc=2; end
      7'b0110111: begin RegWrite=1; ALUSrc=1; SrcASel=2; ImmSrc=4; end
      7'b0010111: begin RegWrite=1; ALUSrc=1; SrcASel=1; ImmSrc=4; end
      // FENCE and SYSTEM instructions require an external environment.
      default: begin end
    endcase
  end
endmodule
