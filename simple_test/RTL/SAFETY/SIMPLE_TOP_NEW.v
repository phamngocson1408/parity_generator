/**
 * Simple Top Module for Testing Parity Generation - ORIGINAL
 * Features:
 *  - Simple AXI-like bus interface
 *  - Clock and Reset
 *  - Write and Read channels
 *  - Status output
 */

`timescale 1ns / 1ps

module SIMPLE_TOP (

    input                       ACLK,
    input                       RESETN_ACLK,
    
    // Write Address Channel
    input                       WADDR_VALID,
    input [31:0]               WADDR_DATA,
    output                      WADDR_READY,
    
    // Write Data Channel
    input                       WDATA_VALID,
    input [63:0]               WDATA_DATA,
    output                      WDATA_READY,
    
    // Read Address Channel
    input                       RADDR_VALID,
    input [31:0]               RADDR_DATA,
    output                      RADDR_READY,
    
    // Read Data Channel
    output                      RDATA_VALID,
    output [63:0]              RDATA_DATA,
    input                       RDATA_READY,
    
    // Status outputs
    output [7:0]               STATUS,
    output  ERR_WADDR_PARITY_B ,
    input ENERR_WADDR_PARITY,
    input FIERR_WADDR_PARITY,
    input [0:0] WADDR_PARITY,
    input [0:0] WDATA_PARITY,
    input [0:0] RADDR_PARITY,
    output ERR_WADDR_PARITY,
    output [0:0] RDATA_PARITY
);


    assign WADDR_READY = 1'b1;
    assign WDATA_READY = 1'b1;
    assign RADDR_READY = 1'b1;
    
    // Status counter
    reg [7:0] status_counter;
    assign STATUS = status_counter;
    
    always @(posedge ACLK or negedge RESETN_ACLK) begin
        if (!RESETN_ACLK) begin
            status_counter <= 8'h00;
        end else begin
            if ((WADDR_VALID && WADDR_READY) || 
                (WDATA_VALID && WDATA_READY) ||
                (RADDR_VALID && RADDR_READY) ||
                (RDATA_VALID && RDATA_READY)) begin
                status_counter <= status_counter + 1;
            end
        end
    end
    
    // Read data echo logic
    reg [63:0] rdata_reg;
    always @(posedge ACLK or negedge RESETN_ACLK) begin
        if (!RESETN_ACLK) begin
            rdata_reg <= 64'h0;
        end else if (RADDR_VALID && RADDR_READY) begin
            rdata_reg <= {32'h0, RADDR_DATA};
        end
    end
    
    // Read data valid tracking
    reg rdata_valid_reg;
    always @(posedge ACLK or negedge RESETN_ACLK) begin
        if (!RESETN_ACLK) begin
            rdata_valid_reg <= 1'b0;
        end else begin
            rdata_valid_reg <= RADDR_VALID && RADDR_READY;
        end
    end
    
    // Output assignments
    assign RDATA_VALID = rdata_valid_reg;
    assign RDATA_DATA = rdata_reg;

SIMPLE_TOP_IP_PARITY_GEN u_simple_top_ip_parity_gen (
    .ACLK (ACLK),
    .RESETN_ACLK (RESETN_ACLK),
    .ENERR_WADDR_PARITY (ENERR_WADDR_PARITY),
    .ERR_WADDR_PARITY (ERR_WADDR_PARITY),
    .ERR_WADDR_PARITY_B (ERR_WADDR_PARITY_B),
    .FIERR_WADDR_PARITY (FIERR_WADDR_PARITY),
    .WADDR_DATA (WADDR_DATA),
    .WADDR_PARITY (WADDR_PARITY),
    .WADDR_VALID (WADDR_VALID),
    .WDATA_DATA (WDATA_DATA),
    .WDATA_PARITY (WDATA_PARITY),
    .WDATA_VALID (WDATA_VALID),
    .RADDR_DATA (RADDR_DATA),
    .RADDR_PARITY (RADDR_PARITY),
    .RADDR_VALID (RADDR_VALID),
    .RDATA_DATA (RDATA_DATA),
    .RDATA_PARITY (RDATA_PARITY),
    .RDATA_VALID (RDATA_VALID)
);

endmodule