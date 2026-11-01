module extend(input [31:7] instr,
              input [2:0] immsrc,
              output reg [31:0] immext);
  always @* case (immsrc)
    3'd0: immext = {{20{instr[31]}}, instr[31:20]};
    3'd1: immext = {{20{instr[31]}}, instr[31:25], instr[11:7]};
    3'd2: immext = {{20{instr[31]}}, instr[7], instr[30:25], instr[11:8], 1'b0};
    3'd3: immext = {{12{instr[31]}}, instr[19:12], instr[20], instr[30:21], 1'b0};
    3'd4: immext = {instr[31:12], 12'b0};
    default: immext = 32'bx;
  endcase
endmodule
