module testbench;
  reg          clk;
  reg          reset;
  wire [31:0]  WriteData;
  wire [31:0]  DataAdr;
  wire         MemWrite;
  
  // Instancia del dispositivo a probar (Top)
  top dut(
    .clk(clk), 
    .reset(reset), 
    .WriteData(WriteData), 
    .DataAdr(DataAdr), 
    .MemWrite(MemWrite)
  );

  // Generador de reloj (Periodo = 10ns)
  always begin
    clk = 1; #5; 
    clk = 0; #5;
  end

  // Inicialización del test sincronizado
  initial begin
    reset = 1;
    // Mantener reset durante 2 ciclos completos de reloj y liberarlo en el flanco
    repeat (2) @(posedge clk);
    #1; // Pequeño margen para salir de reset limpiamente
    reset = 0;
  end

  // Verificación de resultados (Revisión en negedge clk)
  always @(negedge clk) begin
    if (MemWrite) begin
      // Verifica si la instrucción 'sw' escribió el valor esperado (25) en la dirección (100)
      if (DataAdr === 100 && WriteData === 25) begin
        $display("Simulation succeeded");
        $finish;
      end else if (DataAdr !== 96) begin
        $display("Simulation failed: DataAdr = %d, WriteData = %d", DataAdr, WriteData);
        $finish;
      end
    end
  end

endmodule