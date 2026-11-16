// Select newest matching producer: MEM1, MEM0, WB1, WB0.
module forward_dual(
    input [4:0] rs,
    input [31:0] raw,
    input vm1, wm1, lm1, input [4:0] rm1, input [31:0] dm1,
    input vm0, wm0, lm0, input [4:0] rm0, input [31:0] dm0,
    input vw1, ww1, input [4:0] rw1, input [31:0] dw1,
    input vw0, ww0, input [4:0] rw0, input [31:0] dw0,
    output reg [31:0] value,
    output reg [2:0] select_src
);
  always @* begin
    value = (rs == 0) ? 0 : raw;
    select_src = 0;
    if (rs != 0) begin
      if (vm1 && wm1 && !lm1 && rm1 == rs) begin
        value = dm1; select_src = 4;
      end else if (vm0 && wm0 && !lm0 && rm0 == rs) begin
        value = dm0; select_src = 3;
      end else if (vw1 && ww1 && rw1 == rs) begin
        value = dw1; select_src = 2;
      end else if (vw0 && ww0 && rw0 == rs) begin
        value = dw0; select_src = 1;
      end
    end
  end
endmodule
