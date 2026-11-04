module dmem_dual(
    input clk,

    input we0,
    input [2:0] funct3_0,
    input [31:0] a0, wd0,
    output reg [31:0] rd0,

    input we1,
    input [2:0] funct3_1,
    input [31:0] a1, wd1,
    output reg [31:0] rd1
);

  reg [31:0] RAM[0:255];


  wire [31:0] word0 = RAM[a0[31:2]];
  wire [4:0] shift0 = {a0[1:0], 3'b000};
  wire [31:0] shifted0 = word0 >> shift0;

  always @* begin
    case (funct3_0)
      3'b000: rd0 = {{24{shifted0[7]}}, shifted0[7:0]};
      3'b001: rd0 = {{16{shifted0[15]}}, shifted0[15:0]};
      3'b010: rd0 = word0;
      3'b100: rd0 = {24'b0, shifted0[7:0]};
      3'b101: rd0 = {16'b0, shifted0[15:0]};
      default: rd0 = 32'bx;
    endcase
  end

  wire [31:0] word1 = RAM[a1[31:2]];
  wire [4:0] shift1 = {a1[1:0], 3'b000};
  wire [31:0] shifted1 = word1 >> shift1;

  always @* begin
    case (funct3_1)
      3'b000: rd1 = {{24{shifted1[7]}}, shifted1[7:0]};
      3'b001: rd1 = {{16{shifted1[15]}}, shifted1[15:0]};
      3'b010: rd1 = word1;
      3'b100: rd1 = {24'b0, shifted1[7:0]};
      3'b101: rd1 = {16'b0, shifted1[15:0]};
      default: rd1 = 32'bx;
    endcase
  end


  always @(posedge clk) begin

    if (we0) begin
      case (funct3_0)
        3'b000:
          RAM[a0[31:2]] <= (word0 & ~(32'hff << shift0)) |
                           ((wd0 & 32'hff) << shift0);

        3'b001:
          RAM[a0[31:2]] <= (word0 & ~(32'hffff << shift0)) |
                           ((wd0 & 32'hffff) << shift0);

        3'b010:
          RAM[a0[31:2]] <= wd0;

        default: begin end
      endcase
    end

    if (we1) begin
      case (funct3_1)
        3'b000:
          RAM[a1[31:2]] <= (word1 & ~(32'hff << shift1)) |
                           ((wd1 & 32'hff) << shift1);

        3'b001:
          RAM[a1[31:2]] <= (word1 & ~(32'hffff << shift1)) |
                           ((wd1 & 32'hffff) << shift1);

        3'b010:
          RAM[a1[31:2]] <= wd1;

        default: begin end
      endcase
    end

  end

endmodule
