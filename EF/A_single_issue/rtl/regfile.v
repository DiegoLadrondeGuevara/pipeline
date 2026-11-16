module regfile(
    input         clk, 
    input         we3, 
    input  [ 4:0] a1, a2, a3, 
    input  [31:0] wd3, 
    output [31:0] rd1, rd2
);

  reg [31:0] rf[31:0]; 

  // Escribir en el flanco de BAJADA (negedge) del reloj
  // Esto permite que la etapa WB escriba en la primera mitad del ciclo 
  // y la etapa ID lea el valor actualizado en la segunda mitad.
  always @(negedge clk) begin 
    if (we3 && (a3 != 5'b0)) begin
      rf[a3] <= wd3; 
    end
  end
  
  // Lectura combinacional de las dos salidas
  // El registro x0 siempre devuelve 0
  assign rd1 = (a1 != 5'b0) ? rf[a1] : 32'b0; 
  assign rd2 = (a2 != 5'b0) ? rf[a2] : 32'b0; 

endmodule