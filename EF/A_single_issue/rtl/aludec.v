module aludec(input opb5,
              input [2:0] funct3,
              input funct7b5,
              input [1:0] ALUOp,
              output reg [3:0] ALUControl);
  always @* begin
    if (ALUOp == 2'b01) ALUControl = 4'd1;
    else if (ALUOp != 2'b10) ALUControl = 4'd0;
    else case (funct3)
      3'b000: ALUControl = (opb5 && funct7b5) ? 4'd1 : 4'd0;
      3'b001: ALUControl = 4'd6;
      3'b010: ALUControl = 4'd5;
      3'b011: ALUControl = 4'd8;
      3'b100: ALUControl = 4'd4;
      3'b101: ALUControl = funct7b5 ? 4'd9 : 4'd7;
      3'b110: ALUControl = 4'd3;
      3'b111: ALUControl = 4'd2;
      default: ALUControl = 4'd0;
    endcase
  end
endmodule
