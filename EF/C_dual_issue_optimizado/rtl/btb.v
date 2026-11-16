// Direct-mapped Branch Target Buffer. Two read ports match the two IF slots;
// a single resolved control instruction updates it in EX. A two-bit counter
// suppresses taken predictions for repeatedly not-taken conditional branches.
module btb #(
    parameter INDEX_BITS = 4,
    parameter ENTRIES = (1 << INDEX_BITS)
)(
    input clk, reset,
    input [31:0] pc0, pc1,
    output hit0, hit1, predict0, predict1,
    output [31:0] target0, target1,
    input resolve_valid, resolve_taken, resolve_jump,
    input [31:0] resolve_pc, resolve_target
);
  reg valid [0:ENTRIES-1];
  reg [31:0] tag [0:ENTRIES-1], target [0:ENTRIES-1];
  reg [1:0] counter [0:ENTRIES-1];
  wire [INDEX_BITS-1:0] index0 = pc0[INDEX_BITS+1:2];
  wire [INDEX_BITS-1:0] index1 = pc1[INDEX_BITS+1:2];
  wire [INDEX_BITS-1:0] update_index = resolve_pc[INDEX_BITS+1:2];
  wire update_hit = valid[update_index] && tag[update_index] == resolve_pc;
  assign hit0 = valid[index0] && tag[index0] == pc0;
  assign hit1 = valid[index1] && tag[index1] == pc1;
  assign predict0 = hit0 && counter[index0][1];
  assign predict1 = hit1 && counter[index1][1];
  assign target0 = target[index0];
  assign target1 = target[index1];

  integer i;
  always @(posedge clk or posedge reset) begin
    if (reset) begin
      for (i=0; i<ENTRIES; i=i+1) begin
        valid[i] <= 0;
        tag[i] <= 0;
        target[i] <= 0;
        counter[i] <= 0;
      end
    end else if (resolve_valid) begin
      if (update_hit) begin
        if (resolve_taken) begin
          target[update_index] <= resolve_target;
          if (resolve_jump) counter[update_index] <= 2'b11;
          else if (counter[update_index] != 2'b11)
            counter[update_index] <= counter[update_index] + 2'b01;
        end else if (counter[update_index] != 2'b00) begin
          counter[update_index] <= counter[update_index] - 2'b01;
        end
      end else if (resolve_taken) begin
        valid[update_index] <= 1;
        tag[update_index] <= resolve_pc;
        target[update_index] <= resolve_target;
        counter[update_index] <= resolve_jump ? 2'b11 : 2'b10;
      end
    end
  end
endmodule
