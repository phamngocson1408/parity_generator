#!/usr/bin/env python3
"""
Generate parity module for SIMPLE_TOP manually without complex dependencies
"""

def generate_parity_module():
    """Generate SIMPLE_TOP_PARITY_NEW.v module"""
    
    verilog = '''/**
 * SIMPLE_TOP Parity Comparator Module
 * Generated for SAFETY.PARITY testing
 * 
 * This module generates parity bits and detects parity errors
 */

module SIMPLE_TOP_PARITY_NEW (
    // Clock and Reset
    input                       ACLK,
    input                       RESETN_ACLK,
    
    // Write Address Parity
    input [31:0]               WADDR_DATA,
    input                       WADDR_PARITY,
    output                      ERR_WADDR_PARITY,
    
    // Write Data Parity
    input [63:0]               WDATA_DATA,
    input                       WDATA_PARITY,
    output                      ERR_WDATA_PARITY,
    
    // Read Address Parity
    input [31:0]               RADDR_DATA,
    input                       RADDR_PARITY,
    output                      ERR_RADDR_PARITY,
    
    // Read Data Parity
    input [63:0]               RDATA_DATA,
    input                       RDATA_PARITY,
    output                      ERR_RDATA_PARITY,
    
    // Fault Injection (optional)
    input [3:0]                FIERR
);

    // Parity calculation functions
    function automatic logic calculate_parity_32bit(input [31:0] data);
        logic parity;
        integer i;
        begin
            parity = 1'b0;
            for (i = 0; i < 32; i = i + 1) begin
                parity = parity ^ data[i];
            end
            calculate_parity_32bit = parity;
        end
    endfunction
    
    function automatic logic calculate_parity_64bit(input [63:0] data);
        logic parity;
        integer i;
        begin
            parity = 1'b0;
            for (i = 0; i < 64; i = i + 1) begin
                parity = parity ^ data[i];
            end
            calculate_parity_64bit = parity;
        end
    endfunction
    
    // Calculated parity values
    wire [0:0] calc_waddr_parity = calculate_parity_32bit(WADDR_DATA);
    wire [0:0] calc_wdata_parity = calculate_parity_64bit(WDATA_DATA);
    wire [0:0] calc_raddr_parity = calculate_parity_32bit(RADDR_DATA);
    wire [0:0] calc_rdata_parity = calculate_parity_64bit(RDATA_DATA);
    
    // Error detection: compare calculated vs received parity
    // ERR = 1 when mismatch detected
    assign ERR_WADDR_PARITY = (calc_waddr_parity != WADDR_PARITY) ? 1'b1 : 1'b0;
    assign ERR_WDATA_PARITY = (calc_wdata_parity != WDATA_PARITY) ? 1'b1 : 1'b0;
    assign ERR_RADDR_PARITY = (calc_raddr_parity != RADDR_PARITY) ? 1'b1 : 1'b0;
    assign ERR_RDATA_PARITY = (calc_rdata_parity != RDATA_PARITY) ? 1'b1 : 1'b0;

endmodule
'''
    return verilog


def generate_top_module():
    """Generate SIMPLE_TOP_NEW.v with parity ports"""
    
    verilog = '''/**
 * Simple Top Module for Testing Parity Generation - WITH PARITY PORTS
 * Features:
 *  - Simple AXI-like bus interface
 *  - Clock and Reset
 *  - Write and Read channels
 *  - Parity signals for each channel
 *  - Error detection outputs
 */

module SIMPLE_TOP_NEW (
    input                       ACLK,
    input                       RESETN_ACLK,
    
    // Write Address Channel
    input                       WADDR_VALID,
    input [31:0]               WADDR_DATA,
    input                       WADDR_PARITY,      // NEW: Parity input
    output                      WADDR_READY,
    
    // Write Data Channel
    input                       WDATA_VALID,
    input [63:0]               WDATA_DATA,
    input                       WDATA_PARITY,      // NEW: Parity input
    output                      WDATA_READY,
    
    // Read Address Channel
    input                       RADDR_VALID,
    input [31:0]               RADDR_DATA,
    input                       RADDR_PARITY,      // NEW: Parity input
    output                      RADDR_READY,
    
    // Read Data Channel
    output                      RDATA_VALID,
    output [63:0]              RDATA_DATA,
    input                       RDATA_READY,
    input                       RDATA_PARITY,      // NEW: Parity input
    
    // Status outputs
    output [7:0]               STATUS,
    
    // Error outputs (NEW)
    output                      ERR_WADDR_PARITY,
    output                      ERR_WDATA_PARITY,
    output                      ERR_RADDR_PARITY,
    output                      ERR_RDATA_PARITY
);

    // Original logic (same as SIMPLE_TOP)
    assign WADDR_READY = 1'b1;
    assign WDATA_READY = 1'b1;
    assign RADDR_READY = 1'b1;
    
    // Status counter
    reg [7:0] status_counter;
    assign STATUS = status_counter;
    
    always @(posedge ACLK) begin
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
    
    // Read data echo
    reg [63:0] rdata_reg;
    always @(posedge ACLK) begin
        if (!RESETN_ACLK) begin
            rdata_reg <= 64'h0;
        end else if (RADDR_VALID && RADDR_READY) begin
            rdata_reg <= {32'h0, RADDR_DATA};
        end
    end
    
    reg rdata_valid_reg;
    always @(posedge ACLK) begin
        if (!RESETN_ACLK) begin
            rdata_valid_reg <= 1'b0;
        end else begin
            rdata_valid_reg <= RADDR_VALID && RADDR_READY;
        end
    end
    
    assign RDATA_VALID = rdata_valid_reg;
    assign RDATA_DATA = rdata_reg;
    
    // Parity error outputs (pass through from parity module)
    // In this simple version, we'll calculate internally
    
    // Calculate parity
    function automatic logic calc_parity_32bit(input [31:0] data);
        logic p;
        integer i;
        begin
            p = 1'b0;
            for (i = 0; i < 32; i = i + 1)
                p = p ^ data[i];
            calc_parity_32bit = p;
        end
    endfunction
    
    function automatic logic calc_parity_64bit(input [63:0] data);
        logic p;
        integer i;
        begin
            p = 1'b0;
            for (i = 0; i < 64; i = i + 1)
                p = p ^ data[i];
            calc_parity_64bit = p;
        end
    endfunction
    
    // Error detection outputs
    assign ERR_WADDR_PARITY = (calc_parity_32bit(WADDR_DATA) != WADDR_PARITY) ? 1'b1 : 1'b0;
    assign ERR_WDATA_PARITY = (calc_parity_64bit(WDATA_DATA) != WDATA_PARITY) ? 1'b1 : 1'b0;
    assign ERR_RADDR_PARITY = (calc_parity_32bit(RADDR_DATA) != RADDR_PARITY) ? 1'b1 : 1'b0;
    assign ERR_RDATA_PARITY = (calc_parity_64bit(RDATA_DATA) != RDATA_PARITY) ? 1'b1 : 1'b0;

endmodule
'''
    return verilog


if __name__ == '__main__':
    import os
    import sys
    
    # Ensure output directory exists
    output_dir = 'axicrypt/RTL/SAFETY'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate parity module
    parity_verilog = generate_parity_module()
    parity_file = f'{output_dir}/SIMPLE_TOP_PARITY_NEW.v'
    with open(parity_file, 'w') as f:
        f.write(parity_verilog)
    print(f"✅ Generated: {parity_file}")
    
    # Generate top module with parity ports
    top_verilog = generate_top_module()
    top_file = f'{output_dir}/SIMPLE_TOP_NEW.v'
    with open(top_file, 'w') as f:
        f.write(top_verilog)
    print(f"✅ Generated: {top_file}")
    
    # Copy to simple_test folder
    import shutil
    shutil.copy(parity_file, 'simple_test/SIMPLE_TOP_PARITY_NEW.v')
    shutil.copy(top_file, 'simple_test/SIMPLE_TOP_NEW.v')
    print(f"✅ Copied to simple_test/")
    
    print("\n✅ PARITY MODULE GENERATION COMPLETE!")
    print(f"\nGenerated files:")
    print(f"  - {parity_file}")
    print(f"  - {top_file}")
