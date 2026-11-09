module dmem(input clk, we,
            input [2:0] funct3,
            input [31:0] a, wd,
            output reg [31:0] rd);
  // Byte addressing with a single 32-bit memory port. Existing word tests
  // can still inspect RAM[address/4] directly.
  reg [31:0] RAM[0:255];
  wire [31:0] word = RAM[a[31:2]];
  wire [4:0] shift = {a[1:0], 3'b000};
  wire [31:0] shifted = word >> shift;
  always @* begin
    case (funct3)
      3'b000: rd = {{24{shifted[7]}}, shifted[7:0]}; // LB
      3'b001: rd = {{16{shifted[15]}}, shifted[15:0]}; // LH
      3'b010: rd = word; // LW
      3'b100: rd = {24'b0, shifted[7:0]}; // LBU
      3'b101: rd = {16'b0, shifted[15:0]}; // LHU
      default: rd = 32'bx;
    endcase
  end
  always @(posedge clk) if (we) begin
    case (funct3)
      3'b000: RAM[a[31:2]] <= (word & ~(32'hff << shift)) |
                                ((wd & 32'hff) << shift); // SB
      3'b001: RAM[a[31:2]] <= (word & ~(32'hffff << shift)) |
                                ((wd & 32'hffff) << shift); // SH
      3'b010: RAM[a[31:2]] <= wd; // SW
      default: begin end
    endcase
  end
endmodule
