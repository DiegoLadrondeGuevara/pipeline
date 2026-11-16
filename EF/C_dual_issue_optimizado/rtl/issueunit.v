// In-order issue. Slot 0 is older; slot 1 may only issue with slot 0.
module issueunit(
    input valid0, valid1,
    input [4:0] rs10, rs20, rd0, rs11, rs21,
    input uses10, uses20, uses11, uses21,
    input writes0, mem0, control0, mem1, control1,
    input load_e0, load_e1,
    input [4:0] rd_e0, rd_e1,
    output issue0, issue1,
    output stall_load, split_raw, split_resource
);
  wire old_wait = valid0 &&
      ((load_e0 && rd_e0 != 0 &&
        ((uses10 && rs10 == rd_e0) || (uses20 && rs20 == rd_e0))) ||
       (load_e1 && rd_e1 != 0 &&
        ((uses10 && rs10 == rd_e1) || (uses20 && rs20 == rd_e1))));
  wire young_wait = valid1 &&
      ((load_e0 && rd_e0 != 0 &&
        ((uses11 && rs11 == rd_e0) || (uses21 && rs21 == rd_e0))) ||
       (load_e1 && rd_e1 != 0 &&
        ((uses11 && rs11 == rd_e1) || (uses21 && rs21 == rd_e1))));
  assign split_raw = valid0 && valid1 && writes0 && rd0 != 0 &&
      ((uses11 && rs11 == rd0) || (uses21 && rs21 == rd0));
  assign split_resource = valid0 && valid1 &&
      ((mem0 && mem1) || (control0 && control1));
  assign issue0 = valid0 && !old_wait;
  assign issue1 = issue0 && valid1 && !young_wait &&
      !split_raw && !split_resource;
  assign stall_load = old_wait || (issue0 && young_wait);
endmodule
