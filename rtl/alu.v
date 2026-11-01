module alu(input [31:0] a, b,
           input [3:0] alucontrol,
           output reg [31:0] result,
           output zero);
  localparam ADD=4'd0, SUB=4'd1, AND_=4'd2, OR_=4'd3,
             XOR_=4'd4, SLT=4'd5, SLL=4'd6, SRL=4'd7,
             SLTU=4'd8, SRA=4'd9;
  always @* begin
    case (alucontrol)
      ADD:  result = a + b;
      SUB:  result = a - b;
      AND_: result = a & b;
      OR_:  result = a | b;
      XOR_: result = a ^ b;
      SLT:  result = ($signed(a) < $signed(b)) ? 32'd1 : 32'd0;
      SLL:  result = a << b[4:0];
      SRL:  result = a >> b[4:0];
      SLTU: result = (a < b) ? 32'd1 : 32'd0;
      SRA:  result = $signed(a) >>> b[4:0];
      default: result = 32'bx;
    endcase
  end
  assign zero = (result == 32'b0);
endmodule
