module imem #(
    parameter DEPTH = 256,
    parameter DEFAULT_FILE = "tests/e1_1.mem"
)(
    input [31:0] a, a2,
    output [31:0] rd, rd2
);
  reg [31:0] RAM[0:DEPTH-1];
  reg [1023:0] program_file;
  integer i;
  initial begin
    for (i = 0; i < DEPTH; i = i + 1) RAM[i] = 32'h00000013; // NOP
    program_file = DEFAULT_FILE;
    if ($value$plusargs("PROGRAM=%s", program_file)) begin end
    $readmemh(program_file, RAM);
  end
  assign rd = (a[31:2] < DEPTH) ? RAM[a[31:2]] : 32'h00000013;
  assign rd2 = (a2[31:2] < DEPTH) ? RAM[a2[31:2]] : 32'h00000013;
endmodule
