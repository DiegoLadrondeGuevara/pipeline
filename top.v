module top(
    input         clk, reset, 
    output [31:0] WriteData, DataAdr, 
    output        MemWrite
);

  wire [31:0] PC, Instr, ReadData; 

  // Instancia del procesador Pipelined (Segmentado)
  riscvpipelined rvpipelined(
    .clk(clk), 
    .reset(reset), 
    .PC(PC), 
    .Instr(Instr), 
    .MemWrite(MemWrite), // Trae la señal MemWrite de la etapa MEM (MemWrite_M)
    .DataAdr(DataAdr),   // Trae la dirección calculada de la etapa MEM (ALUResult_M)
    .WriteData(WriteData),// Trae los datos a escribir de la etapa MEM (WriteData_M)
    .ReadData(ReadData)
  ); 

  // Memoria de Instrucciones (Etapa Fetch)
  imem imem(
    .a(PC), 
    .rd(Instr)
  ); 

  // Memoria de Datos (Etapa Memory)
  dmem dmem(
    .clk(clk), 
    .we(MemWrite), 
    .a(DataAdr), 
    .wd(WriteData), 
    .rd(ReadData)
  ); 

endmodule