module hazardunit(
    input Valid_D, UsesRs1_D, UsesRs2_D,
    input [4:0] Rs1_D, Rs2_D,
    input Valid_E, input [4:0] Rs1_E, Rs2_E, Rd_E,
    input RegWrite_E, input [1:0] ResultSrc_E,
    input Valid_M, input [4:0] Rd_M, input RegWrite_M,
    input [1:0] ResultSrc_M,
    input Valid_W, input [4:0] Rd_W, input RegWrite_W,
    output Stall_D,
    output [1:0] ForwardAE, ForwardBE
);
  assign Stall_D = Valid_D && Valid_E && RegWrite_E &&
                   (ResultSrc_E == 2'b01) && (Rd_E != 0) &&
                   ((UsesRs1_D && Rs1_D == Rd_E) ||
                    (UsesRs2_D && Rs2_D == Rd_E));

  // MEM wins over WB: it is the younger and therefore newer producer.
  wire CanForward_M = Valid_M && RegWrite_M &&
                      (ResultSrc_M != 2'b01) && (Rd_M != 0);
  wire CanForward_W = Valid_W && RegWrite_W && (Rd_W != 0);
  assign ForwardAE = (Rs1_E != 0 && CanForward_M && Rs1_E == Rd_M) ? 2'b10 :
                     (Rs1_E != 0 && CanForward_W && Rs1_E == Rd_W) ? 2'b01 : 2'b00;
  assign ForwardBE = (Rs2_E != 0 && CanForward_M && Rs2_E == Rd_M) ? 2'b10 :
                     (Rs2_E != 0 && CanForward_W && Rs2_E == Rd_W) ? 2'b01 : 2'b00;
endmodule
