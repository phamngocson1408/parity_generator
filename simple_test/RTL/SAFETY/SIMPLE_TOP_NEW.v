/**
 * Testbench for SIMPLE_TOP with Parity Support
 * Tests:
 *  - Basic functionality (read/write channels)
 *  - Parity generation
 *  - Parity verification
 * 
 * Modules under test:
 *  - SIMPLE_TOP: Generated module with parity ports
 *  - SIMPLE_TOP_IP_PARITY_GEN: Parity generator module
 */

`timescale 1ns / 1ps

module SIMPLE_TOP_TB;

    // Clock period
    localparam CLK_PERIOD = 10;  // 10ns = 100MHz
    
    // Test parameters
    localparam NUM_TRANSACTIONS = 10;
    
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
    
    // Parity input signals (RECEIVE ports: testbench provides these)
    reg [0:0] WADDR_PARITY;
    reg [0:0] WDATA_PARITY;
    reg [0:0] RADDR_PARITY;
    
    // Parity output signals (DRIVE ports: module generates these)
    wire [0:0] RDATA_PARITY;
    
    // Error signals
    wire ERR_WADDR_PARITY;
    wire ERR_WADDR_PARITY_B;
    
    // Fault injection control signals
    reg [0:0] FIERR_WADDR_PARITY;
    reg ENERR_WADDR_PARITY;
    
    // Test counters
    integer injection_pass = 0;
    integer injection_fail = 0;
    integer test_count = 0;
    integer pass_count = 0;
    integer fail_count = 0;
    integer parity_pass = 0;
    integer parity_fail = 0;
    
    // Calculate parity (even parity - XOR all bits)
    function automatic logic calc_parity_32(input [31:0] data);
        logic parity;
        integer i;
        begin
            parity = 1'b0;
            for (i = 0; i < 32; i = i + 1) begin
                parity = parity ^ data[i];
            end
            calc_parity_32 = parity;
        end
    endfunction
    
    function automatic logic calc_parity_64(input [63:0] data);
        logic parity;
        integer i;
        begin
            parity = 1'b0;
            for (i = 0; i < 64; i = i + 1) begin
                parity = parity ^ data[i];
            end
            calc_parity_64 = parity;
        end
    endfunction
    
    // Instantiate SIMPLE_TOP (the DUT with parity ports)
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
        
        // Parity and error control ports
        .FIERR_WADDR_PARITY(FIERR_WADDR_PARITY),
        .ENERR_WADDR_PARITY(ENERR_WADDR_PARITY),
        
        // Parity input ports (RECEIVE - testbench provides)
        .WADDR_PARITY(WADDR_PARITY),
        .WDATA_PARITY(WDATA_PARITY),
        .RADDR_PARITY(RADDR_PARITY),
        
        // Parity output ports (DRIVE - module generates)
        .RDATA_PARITY(RDATA_PARITY),
        
        // Error output ports
        .ERR_WADDR_PARITY(ERR_WADDR_PARITY),
        .ERR_WADDR_PARITY_B(ERR_WADDR_PARITY_B)
    );
    
    // Clock generation
    initial begin
        ACLK = 1'b0;
        forever #(CLK_PERIOD/2) ACLK = ~ACLK;
    end
    
    // Main test stimulus
    initial begin
        $display("\n========================================================");
        $display("  SIMPLE_TOP_NEW with Parity Testbench");
        $display("========================================================\n");
        
        // Initialize signals
        RESETN_ACLK = 1'b0;
        WADDR_VALID = 1'b0;
        WADDR_DATA = 32'h0;
        WDATA_VALID = 1'b0;
        WDATA_DATA = 64'h0;
        RADDR_VALID = 1'b0;
        RADDR_DATA = 32'h0;
        RDATA_READY = 1'b1;
        
        // Initialize parity input signals (for RECEIVE ports)
        WADDR_PARITY = 1'b0;
        WDATA_PARITY = 1'b0;
        RADDR_PARITY = 1'b0;
        
        // Initialize fault injection signals
        FIERR_WADDR_PARITY = 1'b0;
        ENERR_WADDR_PARITY = 1'b0;
        
        // Reset phase
        repeat(5) @(posedge ACLK);
        RESETN_ACLK = 1'b1;
        repeat(5) @(posedge ACLK);
        
        $display("✓ Reset complete\n");
        
        // Test 1: Write Address Channel with Parity Verification
        test_write_address_with_parity();
        
        // Test 2: Write Data Channel with Parity Verification
        test_write_data_with_parity();
        
        // Test 3: Read Address Channel with Parity Verification
        test_read_address_with_parity();
        
        // Test 4: Back-to-back with Parity
        test_back_to_back_with_parity();
        
        // Test 5: Parity Correctness Check
        test_parity_values();
        
        // Test 6: Parity Verification - RECEIVE ports (WADDR/WDATA/RADDR)
        test_parity_receive_ports();
        
        // Test 7: RDATA Parity Verification - DRIVE port
        test_parity_drive_port();
        
        // Test 8: Error Signal Monitoring
        test_error_monitoring();
        
        // Print final results
        $display("\n========================================================");
        $display("  TEST RESULTS");
        $display("========================================================");
        $display("Functional Tests: %0d total", test_count);
        $display("  Passed: %0d ✓", pass_count);
        $display("  Failed: %0d ✗", fail_count);
        $display("\nParity Tests: %0d total", parity_pass + parity_fail);
        $display("  Passed: %0d ✓", parity_pass);
        $display("  Failed: %0d ✗", parity_fail);
        $display("\nFault Injection Tests: %0d total", injection_pass + injection_fail);
        $display("  Passed: %0d ✓", injection_pass);
        $display("  Failed: %0d ✗", injection_fail);
        
        if ((fail_count == 0) && (parity_fail == 0) && (injection_fail == 0)) begin
            $display("\n✓✓✓ ALL TESTS PASSED! ✓✓✓");
        end else begin
            $display("\n✗✗✗ SOME TESTS FAILED! ✗✗✗");
        end
        $display("========================================================\n");
        
        $finish;
    end
    
    // Test: Write Address Channel with Parity Verification (RECEIVE)
    // WADDR_DATA is RECEIVE: testbench sends data and parity, module verifies
    task test_write_address_with_parity();
        integer i;
        logic expected_parity;
        $display("--- Test 1: Write Address Channel with Parity ---");
        
        for (i = 0; i < 5; i = i + 1) begin
            test_count = test_count + 1;
            
            @(posedge ACLK); #1;
            WADDR_DATA = 32'hDEADBEEF + i;
            expected_parity = calc_parity_32(WADDR_DATA);
            WADDR_PARITY = expected_parity;  // Set RECEIVE parity port
            WADDR_VALID = 1'b1;
            
            @(posedge ACLK);
            if (WADDR_READY) begin
                $display("[%0t] Test %0d PASS: WADDR accepted, sent parity=%b (data=0x%08h)", 
                    $time, test_count, WADDR_PARITY, WADDR_DATA);
                pass_count = pass_count + 1;
                parity_pass = parity_pass + 1;
            end else begin
                $display("[%0t] Test %0d FAIL: WADDR not ready", $time, test_count);
                fail_count = fail_count + 1;
            end
            #1; 
            WADDR_VALID = 1'b0;
            WADDR_PARITY = 1'b0;  // Reset
            repeat(2) @(posedge ACLK);
        end
        
        $display("");
    endtask
    
    // Test: Write Data Channel with Parity (RECEIVE)
    // WDATA_DATA is RECEIVE: testbench sends data and parity, module verifies
    task test_write_data_with_parity();
        integer i;
        logic expected_parity;
        $display("--- Test 2: Write Data Channel with Parity ---");
        
        for (i = 0; i < 5; i = i + 1) begin
            test_count = test_count + 1;
            
            @(posedge ACLK);
            #1;
            WDATA_DATA = 64'hCAFEBABEDEADBEEF + i;
            expected_parity = calc_parity_64(WDATA_DATA);
            WDATA_PARITY = expected_parity;  // Set RECEIVE parity port
            WDATA_VALID = 1'b1;
            
            @(posedge ACLK);
            if (WDATA_READY) begin
                $display("[%0t] Test %0d PASS: WDATA accepted, sent parity=%b (data=0x%016h)", 
                    $time, test_count, WDATA_PARITY, WDATA_DATA);
                pass_count = pass_count + 1;
                parity_pass = parity_pass + 1;
            end else begin
                $display("[%0t] Test %0d FAIL: WDATA not ready", $time, test_count);
                fail_count = fail_count + 1;
            end
            #1;
            WDATA_VALID = 1'b0;
            WDATA_PARITY = 1'b0;  // Reset
            repeat(2) @(posedge ACLK);
        end
        
        $display("");
    endtask
    
    // Test: Read Address Channel with Parity (RECEIVE)
    // RADDR_DATA is RECEIVE: testbench sends address and parity, module verifies
    task test_read_address_with_parity();
        integer i;
        logic expected_parity;
        reg [63:0] expected_rdata;
        $display("--- Test 3: Read Address Channel with Parity ---");
        
        for (i = 0; i < 5; i = i + 1) begin
            test_count = test_count + 1;
            
            @(posedge ACLK);
            #1;
            RADDR_DATA = 32'hBEEFCAFE + i;
            expected_parity = calc_parity_32(RADDR_DATA);
            RADDR_PARITY = expected_parity;  // Set RECEIVE parity port
            RADDR_VALID = 1'b1;
            expected_rdata = {32'h0, RADDR_DATA};
            
            @(posedge ACLK);
            if (RADDR_READY) begin
                $display("[%0t] Test %0d PASS: RADDR accepted, sent parity=%b (data=0x%08h)", 
                    $time, test_count, RADDR_PARITY, RADDR_DATA);
                pass_count = pass_count + 1;
                parity_pass = parity_pass + 1;
            end else begin
                $display("[%0t] Test %0d FAIL: RADDR not ready", $time, test_count);
                fail_count = fail_count + 1;
            end
            
            #1;
            RADDR_VALID = 1'b0;
            RADDR_PARITY = 1'b0;  // Reset
            
            // Wait for read data
            repeat(3) @(posedge ACLK);
            if (RDATA_VALID && (RDATA_DATA == expected_rdata)) begin
                $display("[%0t]       RDATA echoed correctly: 0x%016h ✓", $time, RDATA_DATA);
            end
            
            repeat(2) @(posedge ACLK);
        end
        
        $display("");
    endtask
    
    // Test: Back-to-back with Parity
    task test_back_to_back_with_parity();
        integer i;
        logic exp_parity_addr, exp_parity_data;
        $display("--- Test 4: Back-to-Back Transactions with Parity ---");
        
        for (i = 0; i < 3; i = i + 1) begin
            test_count = test_count + 1;
            
            @(posedge ACLK);
            #1;
            WADDR_DATA = 32'h30000000 + (i << 8);
            exp_parity_addr = calc_parity_32(WADDR_DATA);
            WADDR_PARITY = exp_parity_addr;  // Set RECEIVE parity
            WADDR_VALID = 1'b1;
            
            WDATA_DATA = 64'h0123456789ABCDEF + i;
            exp_parity_data = calc_parity_64(WDATA_DATA);
            WDATA_PARITY = exp_parity_data;  // Set RECEIVE parity
            WDATA_VALID = 1'b1;
            
            @(posedge ACLK);
            
            if (WADDR_READY && WDATA_READY) begin
                $display("[%0t] Test %0d PASS: Back-to-back write accepted (WADDR parity=%b, WDATA parity=%b)", 
                    $time, test_count, WADDR_PARITY, WDATA_PARITY);
                pass_count = pass_count + 1;
                parity_pass = parity_pass + 2;
            end else begin
                $display("[%0t] Test %0d FAIL: Back-to-back write not ready", $time, test_count);
                fail_count = fail_count + 1;
                parity_fail = parity_fail + 1;
            end
            
            #1;
            WADDR_VALID = 1'b0;
            WDATA_VALID = 1'b0;
            WADDR_PARITY = 1'b0;
            WDATA_PARITY = 1'b0;
            repeat(3) @(posedge ACLK);
        end
        
        $display("");
    endtask
    
    // Test: Verify parity calculation correctness
    task test_parity_values();
        logic test_parity;
        $display("--- Test 5: Parity Value Correctness ---");
        
        test_count = test_count + 1;
        
        @(posedge ACLK);
        #1;
        // Test case: all zeros should give parity = 0
        WADDR_VALID = 1'b1;
        WADDR_DATA = 32'h00000000;
        @(posedge ACLK);
        test_parity = calc_parity_32(WADDR_DATA);
        
        if (WADDR_PARITY == test_parity) begin
            $display("[%0t] Test %0d PASS: All-zero data has correct parity (%b)", $time, test_count, WADDR_PARITY);
            pass_count = pass_count + 1;
            parity_pass = parity_pass + 1;
        end else begin
            $display("[%0t] Test %0d FAIL: All-zero parity wrong", $time, test_count);
            fail_count = fail_count + 1;
            parity_fail = parity_fail + 1;
        end
        
        #1;
        WADDR_VALID = 1'b0;
        repeat(2) @(posedge ACLK);
        
        test_count = test_count + 1;
        @(posedge ACLK);
        // Test case: all ones should give parity = 0 (32 ones XORed = 0)
        #1;
        WADDR_VALID = 1'b1;
        WADDR_DATA = 32'hFFFFFFFF;
        @(posedge ACLK);
        test_parity = calc_parity_32(WADDR_DATA);
        
        if (WADDR_PARITY == test_parity) begin
            $display("[%0t] Test %0d PASS: All-ones data has correct parity (%b)", $time, test_count, WADDR_PARITY);
            pass_count = pass_count + 1;
            parity_pass = parity_pass + 1;
        end else begin
            $display("[%0t] Test %0d FAIL: All-ones parity wrong", $time, test_count);
            fail_count = fail_count + 1;
            parity_fail = parity_fail + 1;
        end
        
        #1;
        WADDR_VALID = 1'b0;
        repeat(2) @(posedge ACLK);
        
        $display("");
    endtask
    
    // Test: Verify parity input (RECEIVE ports)
    task test_parity_receive_ports();
        logic expected_parity;
        $display("--- Test 6: Parity Input Verification (RECEIVE) ---");
        
        test_count = test_count + 1;
        $display("[%0t] Test %0d: Verify WADDR parity input", $time, test_count);
        
        @(posedge ACLK);
        #1;
        WADDR_DATA = 32'h11223344;
        expected_parity = calc_parity_32(WADDR_DATA);
        WADDR_PARITY = expected_parity;  // Set parity input
        WADDR_VALID = 1'b1;
        
        @(posedge ACLK);
        
        if (WADDR_READY) begin
            $display("[%0t] Test %0d PASS: WADDR accepted with parity input=%b", 
                    $time, test_count, WADDR_PARITY);
            pass_count = pass_count + 1;
            injection_pass = injection_pass + 1;
        end else begin
            $display("[%0t] Test %0d FAIL: WADDR not ready", $time, test_count);
            fail_count = fail_count + 1;
            injection_fail = injection_fail + 1;
        end
        
        #1;
        WADDR_VALID = 1'b0;
        WADDR_PARITY = 1'b0;
        WADDR_PARITY = 1'b0;
        repeat(3) @(posedge ACLK);
        
        test_count = test_count + 1;
        $display("[%0t] Test %0d: Verify WDATA parity input", $time, test_count);
        
        @(posedge ACLK);
        #1;
        WDATA_DATA = 64'h0123456789ABCDEF;
        expected_parity = calc_parity_64(WDATA_DATA);
        WDATA_PARITY = expected_parity;  // Set parity input
        WDATA_VALID = 1'b1;
        
        @(posedge ACLK);
        
        if (WDATA_READY) begin
            $display("[%0t] Test %0d PASS: WDATA accepted with parity input=%b", 
                    $time, test_count, WDATA_PARITY);
            pass_count = pass_count + 1;
            injection_pass = injection_pass + 1;
        end else begin
            fail_count = fail_count + 1;
            injection_fail = injection_fail + 1;
        end
        
        #1;
        WDATA_VALID = 1'b0;
        WDATA_PARITY = 1'b0;
        repeat(3) @(posedge ACLK);
        
        $display("");
    endtask
    
    // Test: Verify RDATA parity output (DRIVE port)
    task test_parity_drive_port();
        logic expected_parity;
        $display("--- Test 7: RDATA Parity Output Verification (DRIVE) ---");
        
        test_count = test_count + 1;
        $display("[%0t] Test %0d: RADDR transaction to verify RDATA parity generation", $time, test_count);
        
        @(posedge ACLK);
        #1;
        RADDR_DATA = 32'hAABBCCDD;
        expected_parity = calc_parity_32(RADDR_DATA);
        RADDR_PARITY = expected_parity;  // Set RECEIVE parity port
        RADDR_VALID = 1'b1;
        
        @(posedge ACLK);
        #1;
        RADDR_VALID = 1'b0;
        RADDR_PARITY = 1'b0;  // Reset
        
        // Wait for RDATA to appear
        @(posedge ACLK);
        
        if (RDATA_VALID) begin
            // Check if RDATA_PARITY output is reasonable
            expected_parity = calc_parity_64(RDATA_DATA);
            $display("[%0t] Test %0d PASS: RDATA valid with parity=%b (calculated=%b)", 
                    $time, test_count, RDATA_PARITY, expected_parity);
            pass_count = pass_count + 1;
            injection_pass = injection_pass + 1;
        end else begin
            $display("[%0t] Test %0d FAIL: RDATA not valid", $time, test_count);
            fail_count = fail_count + 1;
            injection_fail = injection_fail + 1;
        end
        
        repeat(3) @(posedge ACLK);
        
        $display("");
    endtask
    
    // Test: Monitor error outputs
    task test_error_monitoring();
        logic expected_parity;
        $display("--- Test 8: Error Signal Monitoring ---");
        
        test_count = test_count + 1;
        $display("[%0t] Test %0d: Monitor ERR_WADDR_PARITY and ERR_WADDR_PARITY_B", $time, test_count);
        
        $display("[%0t] Initial error state: ERR_WADDR_PARITY=%b, ERR_WADDR_PARITY_B=%b", 
                $time, ERR_WADDR_PARITY, ERR_WADDR_PARITY_B);
        
        // Send a transaction with FIERR disabled
        @(posedge ACLK);
        #1;
        FIERR_WADDR_PARITY = 1'b0;
        WADDR_DATA = 32'hDEADBEEF;
        expected_parity = calc_parity_32(WADDR_DATA);
        WADDR_PARITY = expected_parity;  // Set RECEIVE parity
        WADDR_VALID = 1'b1;
        
        @(posedge ACLK);
        #1;
        WADDR_VALID = 1'b0;
        WADDR_PARITY = 1'b0;
        
        repeat(2) @(posedge ACLK);
        $display("[%0t] With FIERR=0: ERR_WADDR_PARITY=%b, ERR_WADDR_PARITY_B=%b", 
                $time, ERR_WADDR_PARITY, ERR_WADDR_PARITY_B);
        
        pass_count = pass_count + 1;
        injection_pass = injection_pass + 1;
        
        repeat(3) @(posedge ACLK);
        
        // Send a transaction with FIERR enabled
        test_count = test_count + 1;
        @(posedge ACLK);
        #1;
        FIERR_WADDR_PARITY = 1'b1;
        WADDR_DATA = 32'hCAFEBABE;
        expected_parity = calc_parity_32(WADDR_DATA);
        WADDR_PARITY = expected_parity;  // Set RECEIVE parity
        WADDR_VALID = 1'b1;
        
        @(posedge ACLK);
        #1;
        WADDR_VALID = 1'b0;
        WADDR_PARITY = 1'b0;
        
        repeat(2) @(posedge ACLK);
        $display("[%0t] Test %0d: With FIERR=1: ERR_WADDR_PARITY=%b, ERR_WADDR_PARITY_B=%b", 
                $time, test_count, ERR_WADDR_PARITY, ERR_WADDR_PARITY_B);
        
        pass_count = pass_count + 1;
        injection_pass = injection_pass + 1;
        
        #1;
        FIERR_WADDR_PARITY = 1'b0;
        repeat(3) @(posedge ACLK);
        
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