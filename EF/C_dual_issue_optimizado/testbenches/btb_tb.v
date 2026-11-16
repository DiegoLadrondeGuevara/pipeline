`timescale 1ns/1ps
module btb_tb;
  reg clk=0, reset=1;
  reg [31:0] pc0=32'h40, pc1=32'h44;
  reg resolve_valid=0, resolve_taken=0, resolve_jump=0;
  reg [31:0] resolve_pc=0, resolve_target=0;
  wire hit0, hit1, predict0, predict1;
  wire [31:0] target0, target1;
  btb dut(.clk(clk), .reset(reset), .pc0(pc0), .pc1(pc1),
    .hit0(hit0), .hit1(hit1), .predict0(predict0),
    .predict1(predict1), .target0(target0), .target1(target1),
    .resolve_valid(resolve_valid), .resolve_taken(resolve_taken),
    .resolve_jump(resolve_jump), .resolve_pc(resolve_pc),
    .resolve_target(resolve_target));
  always #5 clk=~clk;

  task resolve;
    input [31:0] pc, target;
    input taken, jump;
    begin
      @(negedge clk);
      resolve_valid=1; resolve_pc=pc; resolve_target=target;
      resolve_taken=taken; resolve_jump=jump;
      @(posedge clk); #1;
      resolve_valid=0;
    end
  endtask

  initial begin
    repeat(2) @(negedge clk);
    reset=0;
    #1;
    if (hit0 || predict0 || hit1 || predict1)
      $fatal(1,"Cold BTB must miss");
    resolve(32'h40,32'h100,1,0);
    if (!hit0 || !predict0 || target0!==32'h100)
      $fatal(1,"Taken branch not learned");
    if (hit1 || predict1) $fatal(1,"Second fetch slot false hit");
    resolve(32'h40,32'h100,0,0);
    if (!hit0 || predict0) $fatal(1,"Not-taken counter did not update");
    resolve(32'h40,32'h104,1,0);
    if (!predict0 || target0!==32'h104)
      $fatal(1,"Taken branch target/counter did not recover");
    resolve(32'h80,32'h120,1,1); // Same index, different full PC.
    if (hit0 || predict0) $fatal(1,"Aliased PC produced false BTB hit");
    pc0=32'h80; #1;
    if (!hit0 || !predict0 || target0!==32'h120)
      $fatal(1,"JAL entry not installed");
    $display("PASS BTB cold miss, target, counter, two-port and tag alias checks");
    $finish;
  end
endmodule
