/**
 * Improved Testbench for SIMPLE_TOP with Parity Support
 * 
 * Testing Strategy:
 * 
 * RECEIVE Ports (WADDR_PARITY, WDATA_PARITY, RADDR_PARITY):
 *   - Testbench sends: data + parity value
 *   - DUT compares received parity with calculated parity
 *   - Error detection rules:
 *     - ENERR=0: ERR must stay 0 (error detection disabled)
 *     - ENERR=1, FIERR=0: ERR must be 0 (correct parity sent)
 *     - ENERR=1, FIERR=1: ERR must become 1 (fault injected, parity corrupted)
 *     - Note: ERR may have 2-3 cycle delay after FIERR
 * 
 * DRIVE Port (RDATA_PARITY):
 *   - DUT generates parity for output data
 *   - When RDATA_VALID=1: Check RDATA_PARITY == calc_parity(RDATA_DATA)
 */

`timescale 1ns / 1ps

module SIMPLE_TOP_TB;

    localparam CLK_PERIOD = 10;  // 100MHz
    
    // Clock and Reset
    reg ACLK;
    reg RESETN_ACLK;
    
    // Write Address Channel
    reg WADDR_VALID;
    reg [31:0] WADDR_DATA;
    wire WADDR_READY;
    
    // Write Data Channel
    reg WDATA_VALID;
    reg [63:0] WDATA_DATA;
    wire WDATA_READY;
    
    // Read Address Channel
    reg RADDR_VALID;
    reg [31:0] RADDR_DATA;
    wire RADDR_READY;
    
    // Read Data Channel
    wire RDATA_VALID;
    wire [63:0] RDATA_DATA;
    reg RDATA_READY;
    
    // Status
    wire [7:0] STATUS;
    
    // Parity RECEIVE ports (testbench provides)
    reg [0:0] WADDR_PARITY;
    reg [0:0] WDATA_PARITY;
    reg [0:0] RADDR_PARITY;
    
    // Parity DRIVE port (DUT generates)
    wire [0:0] RDATA_PARITY;
    
    // Error signals
    wire ERR_WADDR_PARITY;
    wire ERR_WADDR_PARITY_B;
    
    // Fault injection control
    reg [0:0] FIERR_WADDR_PARITY;
    reg ENERR_WADDR_PARITY;
    
    // Test metrics
    integer test_count = 0;
    integer pass_count = 0;
    integer fail_count = 0;
    
    // Error signal history for timing analysis
    reg [7:0] err_history;
    reg [7:0] fierr_history;
    
    // Calculate parity (even parity)
    function automatic logic calc_parity_32(input [31:0] data);
        logic parity;
        integer i;
        begin
            parity = 1'b0;
            for (i = 0; i < 32; i = i + 1)
                parity = parity ^ data[i];
            calc_parity_32 = parity;
        end
    endfunction
    
    function automatic logic calc_parity_64(input [63:0] data);
        logic parity;
        integer i;
        begin
            parity = 1'b0;
            for (i = 0; i < 64; i = i + 1)
                parity = parity ^ data[i];
            calc_parity_64 = parity;
        end
    endfunction
    
    // DUT Instantiation
    SIMPLE_TOP dut (
        .ACLK(ACLK),
        .RESETN_ACLK(RESETN_ACLK),
        .WADDR_VALID(WADDR_VALID),
        .WADDR_DATA(WADDR_DATA),
        .WADDR_READY(WADDR_READY),
        .WDATA_VALID(WDATA_VALID),
        .WDATA_DATA(WDATA_DATA),
        .WDATA_READY(WDATA_READY),
        .RADDR_VALID(RADDR_VALID),
        .RADDR_DATA(RADDR_DATA),
        .RADDR_READY(RADDR_READY),
        .RDATA_VALID(RDATA_VALID),
        .RDATA_DATA(RDATA_DATA),
        .RDATA_READY(RDATA_READY),
        .STATUS(STATUS),
        .FIERR_WADDR_PARITY(FIERR_WADDR_PARITY),
        .ENERR_WADDR_PARITY(ENERR_WADDR_PARITY),
        .WADDR_PARITY(WADDR_PARITY),
        .WDATA_PARITY(WDATA_PARITY),
        .RADDR_PARITY(RADDR_PARITY),
        .RDATA_PARITY(RDATA_PARITY),
        .ERR_WADDR_PARITY(ERR_WADDR_PARITY),
        .ERR_WADDR_PARITY_B(ERR_WADDR_PARITY_B)
    );
    
    // Clock generation
    initial begin
        ACLK = 1'b0;
        forever #(CLK_PERIOD/2) ACLK = ~ACLK;
    end
    
    // Error signal monitoring
    always @(posedge ACLK) begin
        err_history <= {err_history[6:0], ERR_WADDR_PARITY};
        fierf_history <= {fierf_history[6:0], FIERR_WADDR_PARITY};
    end
    
    // Main test sequence
    initial begin
        $display("\n========================================================");
        $display("  SIMPLE_TOP - Improved Parity Testbench");
        $display("========================================================\n");
        
        // Initialize
        RESETN_ACLK = 1'b0;
        WADDR_VALID = 1'b0;
        WADDR_DATA = 32'h0;
        WDATA_VALID = 1'b0;
        WDATA_DATA = 64'h0;
        RADDR_VALID = 1'b0;
        RADDR_DATA = 32'h0;
        RDATA_READY = 1'b1;
        WADDR_PARITY = 1'b0;
        WDATA_PARITY = 1'b0;
        RADDR_PARITY = 1'b0;
        FIERR_WADDR_PARITY = 1'b0;
        ENERR_WADDR_PARITY = 1'b0;
        
        // Reset
        repeat(5) @(posedge ACLK);
        #1;
        RESETN_ACLK = 1'b1;
        repeat(5) @(posedge ACLK);
        
        $display("✓ Reset complete\n");
        
        // Test 1: RECEIVE Port - No Error Detection (ENERR=0)
        test_receive_port_no_err();
        
        // Test 2: RECEIVE Port - Correct Parity (ENERR=1, FIERR=0)
        test_receive_port_correct_parity();
        
        // Test 3: RECEIVE Port - Fault Injection (ENERR=1, FIERR=1)
        test_receive_port_fault_injection();
        
        // Test 4: DRIVE Port - RDATA Parity Verification
        test_drive_port_rdata_parity();
        
        // Print results
        $display("\n========================================================");
        $display("  FINAL RESULTS");
        $display("========================================================");
        $display("Total Tests: %0d", test_count);
        $display("  Passed: %0d ✓", pass_count);
        $display("  Failed: %0d ✗", fail_count);
        
        if (fail_count == 0)
            $display("\n✓✓✓ ALL TESTS PASSED! ✓✓✓");
        else
            $display("\n✗✗✗ SOME TESTS FAILED! ✗✗✗");
        $display("========================================================\n");
        
        $finish;
    end
    
    // ===================================================================
    // TEST 1: RECEIVE Port - Error Detection DISABLED (ENERR=0)
    // ===================================================================
    task test_receive_port_no_err();
        logic exp_parity;
        integer i;
        
        $display("--- Test 1: RECEIVE Port - ENERR=0 (Error Detection Disabled) ---");
        
        @(posedge ACLK);
        #1 ENERR_WADDR_PARITY = 1'b0;
        
        for (i = 0; i < 3; i = i + 1) begin
            test_count = test_count + 1;
            
            @(posedge ACLK);
            #1;
            WADDR_DATA = 32'hDEAD0000 + i;
            exp_parity = calc_parity_32(WADDR_DATA);
            WADDR_PARITY = exp_parity;
            WADDR_VALID = 1'b1;
            
            @(posedge ACLK);
            
            if (WADDR_READY) begin
                // Check: ERR must be 0 when ENERR=0
                if (ERR_WADDR_PARITY == 1'b0) begin
                    $display("[%0t] Test %0d PASS: ENERR=0 → ERR=0 (error detection disabled)", 
                            $time, test_count);
                    pass_count = pass_count + 1;
                end else begin
                    $display("[%0t] Test %0d FAIL: ENERR=0 but ERR=%b (should be 0)", 
                            $time, test_count, ERR_WADDR_PARITY);
                    fail_count = fail_count + 1;
                end
            end else begin
                $display("[%0t] Test %0d FAIL: WADDR_READY not asserted", $time, test_count);
                fail_count = fail_count + 1;
            end
            
            @(posedge ACLK);
            #1 WADDR_VALID = 1'b0;
            repeat(2) @(posedge ACLK);
        end
        
        $display("");
    endtask
    
    // ===================================================================
    // TEST 2: RECEIVE Port - Correct Parity (ENERR=1, FIERR=0)
    // ===================================================================
    task test_receive_port_correct_parity();
        logic exp_parity;
        integer i;
        
        $display("--- Test 2: RECEIVE Port - ENERR=1, FIERR=0 (Correct Parity) ---");
        
        @(posedge ACLK);
        #1;
        ENERR_WADDR_PARITY = 1'b1;
        FIERR_WADDR_PARITY = 1'b0;
        
        for (i = 0; i < 5; i = i + 1) begin
            test_count = test_count + 1;
            
            @(posedge ACLK);
            #1;
            WADDR_DATA = 32'hCAFE0000 + (i << 8);
            exp_parity = calc_parity_32(WADDR_DATA);
            WADDR_PARITY = exp_parity;  // Send CORRECT parity
            WADDR_VALID = 1'b1;
            
            @(posedge ACLK);
            
            if (WADDR_READY) begin
                // Check: ERR must be 0 when parity is correct
                if (ERR_WADDR_PARITY == 1'b0) begin
                    $display("[%0t] Test %0d PASS: Correct parity → ERR=0 (data=0x%08h, parity=%b)", 
                            $time, test_count, WADDR_DATA, WADDR_PARITY);
                    pass_count = pass_count + 1;
                end else begin
                    $display("[%0t] Test %0d FAIL: Correct parity but ERR=1 (should be 0)", 
                            $time, test_count);
                    fail_count = fail_count + 1;
                end
            end else begin
                $display("[%0t] Test %0d FAIL: WADDR_READY not asserted", $time, test_count);
                fail_count = fail_count + 1;
            end
            
            @(posedge ACLK);
            #1 WADDR_VALID = 1'b0;
            repeat(2) @(posedge ACLK);
        end
        
        $display("");
    endtask
    
    // ===================================================================
    // TEST 3: RECEIVE Port - Fault Injection (ENERR=1, FIERR=1)
    // ===================================================================
    task test_receive_port_fault_injection();
        logic exp_parity;
        integer i, delay_count;
        integer max_delay = 5;
        
        $display("--- Test 3: RECEIVE Port - ENERR=1, FIERR=1 (Fault Injection) ---");
        
        @(posedge ACLK);
        #1 ENERR_WADDR_PARITY = 1'b1;
        
        for (i = 0; i < 3; i = i + 1) begin
            test_count = test_count + 1;
            
            // Enable fault injection at transaction start
            @(posedge ACLK);
            #1;
            FIERR_WADDR_PARITY = 1'b1;  // INJECT FAULT
            WADDR_DATA = 32'hBEEF0000 + (i << 8);
            exp_parity = calc_parity_32(WADDR_DATA);
            WADDR_PARITY = exp_parity;  // Send CORRECT parity
            WADDR_VALID = 1'b1;
            
            @(posedge ACLK);
            #1;
            WADDR_VALID = 1'b0;
            FIERR_WADDR_PARITY = 1'b0;  // Disable fault after assertion
            
            // Wait for error signal to appear (may take 2-3 cycles)
            delay_count = 0;
            while ((ERR_WADDR_PARITY == 1'b0) && (delay_count < max_delay)) begin
                @(posedge ACLK);
                delay_count = delay_count + 1;
            end
            
            if (ERR_WADDR_PARITY == 1'b1) begin
                $display("[%0t] Test %0d PASS: Fault detected (data=0x%08h, delay=%0d cycles)", 
                        $time, test_count, WADDR_DATA, delay_count);
                pass_count = pass_count + 1;
            end else begin
                $display("[%0t] Test %0d FAIL: Fault NOT detected after %0d cycles (ERR should be 1)", 
                        $time, test_count, max_delay);
                fail_count = fail_count + 1;
            end
            
            repeat(3) @(posedge ACLK);
        end
        
        $display("");
    endtask
    
    // ===================================================================
    // TEST 4: DRIVE Port - RDATA Parity Verification
    // ===================================================================
    task test_drive_port_rdata_parity();
        logic exp_rdata_parity;
        integer i;
        
        $display("--- Test 4: DRIVE Port - RDATA_PARITY Generation ---");
        
        @(posedge ACLK);
        #1;
        ENERR_WADDR_PARITY = 1'b0;  // Disable error detection
        FIERR_WADDR_PARITY = 1'b0;
        
        for (i = 0; i < 3; i = i + 1) begin
            test_count = test_count + 1;
            
            @(posedge ACLK);
            #1;
            RADDR_DATA = 32'hABCD0000 + (i << 8);
            RADDR_PARITY = calc_parity_32(RADDR_DATA);  // Send RADDR parity
            RADDR_VALID = 1'b1;
            
            @(posedge ACLK);
            #1;
            RADDR_VALID = 1'b0;
            RADDR_PARITY = 1'b0;
            
            // Wait for RDATA to appear
            repeat(3) @(posedge ACLK);
            
            if (RDATA_VALID) begin
                // Calculate expected RDATA parity
                exp_rdata_parity = calc_parity_64(RDATA_DATA);
                
                // Check: RDATA_PARITY must match calculated parity
                if (RDATA_PARITY == exp_rdata_parity) begin
                    $display("[%0t] Test %0d PASS: RDATA_PARITY correct (data=0x%016h, parity=%b)", 
                            $time, test_count, RDATA_DATA, RDATA_PARITY);
                    pass_count = pass_count + 1;
                end else begin
                    $display("[%0t] Test %0d FAIL: RDATA_PARITY mismatch (expected %b, got %b)", 
                            $time, test_count, exp_rdata_parity, RDATA_PARITY);
                    fail_count = fail_count + 1;
                end
            end else begin
                $display("[%0t] Test %0d FAIL: RDATA_VALID not asserted", $time, test_count);
                fail_count = fail_count + 1;
            end
            
            repeat(3) @(posedge ACLK);
        end
        
        $display("");
    endtask

//====================================================
// WAVEFORM DUMP
//====================================================
initial begin
    $fsdbDumpfile("DUMP/oh");
    $fsdbDumpvars(0, SIMPLE_TOP_TB, "+all");
end

endmodule
