module DCLS_COMPARATOR_TEMPLATE #(
    parameter DATA_WIDTH = 32,
    parameter MAX_INPUT_WIDTH = 32,  // Maximum input width per equality comparator (stage 0 only)
    parameter NUM_OR_STAGES = 0      // Number of OR reduction stages (0 = no pipelining)
) (
    input CLK,
    input RESETN,

    // Data inputs from two redundant cores
    input [DATA_WIDTH-1:0] DATA_IN_A,
    input [DATA_WIDTH-1:0] DATA_IN_B,

    // Control signals
    input ENERR_DCLS,    // Enable error detection
    input FIERR_DCLS,    // Force fault injection test mode
    
    // Error outputs (redundant pair)
    output reg ERR_DCLS,   // Active high error flag
    output reg ERR_DCLS_B  // Active low error flag (inverse of ERR_DCLS)
);

    // ========== FSM States ==========
    localparam STATE_NORMAL      = 1'b0;  // Normal comparison mode
    localparam STATE_FAULT_TEST  = 1'b1;  // Fault injection test mode
    
    // ========== Internal Signals ==========
    // FSM state registers
    reg current_state, next_state;
    
    // Error flag control (next values for output registers)
    reg next_err_dcls;
    reg next_err_dcls_b;
    
    // Comparator inputs (muxed between normal data and test patterns)
    reg [DATA_WIDTH-1:0] comparator_input_a;
    reg [DATA_WIDTH-1:0] comparator_input_b;
    
    // Fault injection test control
    reg [DATA_WIDTH*2-1:0] fault_injection_mask;  // Bit mask to inject faults
    reg [$clog2(DATA_WIDTH*2)-1:0] test_bit_index, next_test_bit_index;  // Current bit being tested
    reg comparator_failed, next_comparator_failed;  // Flag indicating comparator stuck-at fault (failed to detect injected error)
    
    // Comparator output
    wire comparison_mismatch;  // 1 = data mismatch detected
    
    // Intermediate signals
    reg real_error_detected;  // Actual error in normal mode


    // ========== Instantiate Segment Comparator ==========
    // This module divides wide comparator into smaller chunks with optional pipelining
    DCLS_SEGMENT_COMPARATOR #(
        .DATA_WIDTH(DATA_WIDTH),
        .MAX_INPUT_WIDTH(MAX_INPUT_WIDTH),
        .NUM_OR_STAGES(NUM_OR_STAGES)
    ) u_segment_cmp (
        .CLK(CLK),
        .RESETN(RESETN),
        .DATA_IN_A(comparator_input_a),
        .DATA_IN_B(comparator_input_b),
        .MISMATCH(comparison_mismatch)
    );

    // ========== Input Multiplexing Logic ==========
    // In normal mode: compare actual data from cores
    // In fault test mode: inject bit flips to test comparator functionality
    always_comb begin
        if (current_state == STATE_FAULT_TEST) begin
            // Apply bit inversion mask to test comparator's ability to detect faults
            // First DATA_WIDTH bits go to channel A, next DATA_WIDTH bits to channel B
            comparator_input_a = {DATA_WIDTH{1'b0}} ^ fault_injection_mask[DATA_WIDTH-1:0];
            comparator_input_b = {DATA_WIDTH{1'b0}} ^ fault_injection_mask[DATA_WIDTH*2-1:DATA_WIDTH];
        end
        else begin
            // Normal mode: pass through actual core outputs
            comparator_input_a = DATA_IN_A;
            comparator_input_b = DATA_IN_B;
        end
    end

    // ========== Main FSM Combinational Logic ==========
    always_comb begin
        // Default: maintain current state
        next_state = current_state;
        next_err_dcls = ERR_DCLS;
        next_err_dcls_b = ERR_DCLS_B;
        next_test_bit_index = test_bit_index;
        next_comparator_failed = comparator_failed;
        real_error_detected = comparison_mismatch;
        fault_injection_mask = {DATA_WIDTH*2{1'b0}};

        // ===== Disabled Mode =====
        if (!ENERR_DCLS) begin
            // Error detection disabled: clear all error flags
            next_err_dcls = 1'b0;
            next_err_dcls_b = 1'b1;
        end
        
        // ===== Enabled Mode =====
        else begin
            case (current_state)
                
                // ----- NORMAL STATE: Standard Comparison Mode -----
                STATE_NORMAL: begin
                    if (FIERR_DCLS) begin
                        // Enter fault injection test mode
                        next_state = STATE_FAULT_TEST;
                        next_test_bit_index = 'd0;
                        next_comparator_failed = 1'b0;
                    end
                    else if (real_error_detected) begin
                        // Real mismatch detected between cores
                        next_err_dcls = 1'b1;
                        next_err_dcls_b = 1'b0;
                    end
                end
                
                // ----- FAULT_TEST STATE: Built-In Self-Test Mode -----
                STATE_FAULT_TEST: begin
                    // In test mode, ignore real comparison results
                    real_error_detected = 1'b0;
                    
                    // Continue testing
                    
                    // Check if all bits have been tested
                    if (test_bit_index == (DATA_WIDTH * 2)) begin
                        // Test complete: report results
                        if (comparator_failed) begin
                            // Comparator has stuck-at fault (failed to detect at least one injected error)
                            next_err_dcls = 1'b0;
                            next_err_dcls_b = 1'b1;
                        end
                        else begin
                            // Comparator passed BIST (detected all injected errors)
                            next_err_dcls = 1'b1;
                            next_err_dcls_b = 1'b0;
                        end
                    end
                    else begin
                        // Test current bit: inject single-bit difference
                        fault_injection_mask[test_bit_index] = 1'b1;
                        
                        if (!comparison_mismatch) begin
                            // Comparator failed to detect injected fault -> stuck-at fault exists
                            next_comparator_failed = 1'b1;
                        end
                        else begin
                            // Comparator correctly detected the injected fault
                            next_err_dcls = 1'b1;
                            next_err_dcls_b = 1'b0;
                        end
                        
                        // Move to next bit
                        next_test_bit_index = test_bit_index + 1;
                    end

                    if (FIERR_DCLS == 1'b0) begin
                        // Exit test mode
                        next_state = STATE_NORMAL;
                        //next_comparator_failed = 1'b0;
                        //next_err_dcls = 1'b0;
                        //next_err_dcls_b = 1'b1;
                    end
                end
                
            endcase
        end
    end
    
    // ========== Sequential Logic: State and Output Registers ==========
    always @(posedge CLK or negedge RESETN) begin
        if (!RESETN) begin
            current_state <= STATE_NORMAL;
            test_bit_index <= 'd0;
            comparator_failed <= 1'b0;
            ERR_DCLS <= 1'b0;
            ERR_DCLS_B <= 1'b1;
        end
        else begin
            current_state <= next_state;
            test_bit_index <= next_test_bit_index;
            comparator_failed <= next_comparator_failed;
            ERR_DCLS <= next_err_dcls;
            ERR_DCLS_B <= next_err_dcls_b;
        end
    end
endmodule


// ========== Embedded DCLS_SEGMENT_COMPARATOR Module ==========
module DCLS_SEGMENT_COMPARATOR #(
    parameter DATA_WIDTH = 1024,
    parameter MAX_INPUT_WIDTH = 32,  // Maximum input width per equality comparator (stage 0 only)
    parameter NUM_OR_STAGES = 0      // Number of OR reduction stages (0 = no pipelining)
) (
    input CLK,
    input RESETN,
    input [DATA_WIDTH-1:0] DATA_IN_A,
    input [DATA_WIDTH-1:0] DATA_IN_B,
    output reg MISMATCH
);

    // Calculate number of equality comparators
    localparam NUM_COMPARATORS = (DATA_WIDTH + MAX_INPUT_WIDTH - 1) / MAX_INPUT_WIDTH;
    localparam BITS_PER_STAGE = MAX_INPUT_WIDTH;
    
    // ========== Stage 0: Parallel Equality Comparators ==========
    wire [NUM_COMPARATORS-1:0] segment_error;
    
    generate
        genvar s;
        for (s = 0; s < NUM_COMPARATORS; s = s + 1) begin : sub_cmp
            localparam int START_BIT = s * BITS_PER_STAGE;
            localparam int END_BIT = ((s+1) * BITS_PER_STAGE > DATA_WIDTH) ? 
                                     (DATA_WIDTH - 1) : ((s+1) * BITS_PER_STAGE - 1);
            
            // Stage 0: == logic (equality comparison)
            assign segment_error[s] = (DATA_IN_A[END_BIT:START_BIT] == DATA_IN_B[END_BIT:START_BIT]) 
                                     ? 1'b0 : 1'b1;
        end
    endgenerate

    // ========== Stages 1+: OR Reduction Tree (if NUM_OR_STAGES > 0) ==========
    generate
        if (NUM_OR_STAGES == 0) begin : no_pipeline
            // No pipelining: direct OR of all segment errors
            always @(posedge CLK or negedge RESETN) begin
                if (!RESETN) begin
                    MISMATCH <= 1'b0;
                end
                else begin
                    MISMATCH <= |segment_error;
                end
            end
        end
        else begin : with_pipeline
            genvar st, g;
        
            // Calculate MAX_INPUTS_PER_GATE
            // MAX_INPUTS_PER_GATE = ceil(num_comparators^(1/num_or_stages))
            localparam int MAX_INPUTS_PER_GATE = $ceil(NUM_COMPARATORS ** (1.0 / NUM_OR_STAGES));
        
            // OR reduction stages: st = 1..NUM_OR_STAGES
            for (st = 1; st <= NUM_OR_STAGES; st = st + 1) begin : or_stages
                // IN_W of current stage = OUT_W of last stage
                localparam int IN_W  = (st == 1) ? 
                                       NUM_COMPARATORS : 
                                       or_stages[st-1].OUT_W;
        
                // INPUTS_PER_GATE calculation:
                // For stages 1..NUM_OR_STAGES-1: use MAX_INPUTS_PER_GATE (ceil of base reduction)
                // For stage NUM_OR_STAGES: use IN_W (which is OUT_W of previous stage)
                localparam int INPUTS_PER_GATE = (st < NUM_OR_STAGES)&(IN_W > MAX_INPUTS_PER_GATE) ? 
                                                 MAX_INPUTS_PER_GATE :
                                                 IN_W;
        
                // OUT_W from constraint: (OUT_W-1) * INPUTS_PER_GATE < IN_W <= OUT_W * INPUTS_PER_GATE
                // => OUT_W = ceil(IN_W / INPUTS_PER_GATE)
                localparam int OUT_W_RAW = (IN_W + INPUTS_PER_GATE - 1) / INPUTS_PER_GATE;
                localparam int OUT_W = (OUT_W_RAW == 0) ? 1 : OUT_W_RAW;
        
                // Debug: Display stage parameters during simulation
                initial begin
                    $display("[DCLS_SEGMENT_COMPARATOR] Stage %d: MAX_INPUTS=%d, IN_W=%d, INPUTS_PER_GATE=%d, OUT_W=%d", 
                             st, MAX_INPUTS_PER_GATE, IN_W, INPUTS_PER_GATE, OUT_W);
                end
        
                reg [OUT_W-1:0] stage_data;
        
                // Gates inside each stage
                for (g = 0; g < OUT_W; g = g + 1) begin : gate
                    localparam int START = g * INPUTS_PER_GATE;
        
                    // If this gate has no valid inputs (START >= IN_W) => output = 0
                    if (START >= IN_W) begin : empty_gate
                        always @(posedge CLK or negedge RESETN) begin
                            if (!RESETN) stage_data[g] <= 1'b0;
                            else         stage_data[g] <= 1'b0;
                        end
                    end
                    else begin : nonempty_gate
                        localparam int END_C = ((START + INPUTS_PER_GATE) > IN_W) ? IN_W : (START + INPUTS_PER_GATE);
                        localparam int W     = (END_C - START); // ensure W >= 1
        
                        // Stage 1 takes input from segment_error
                        if (st == 1) begin : s1
                            always @(posedge CLK or negedge RESETN) begin
                                if (!RESETN) stage_data[g] <= 1'b0;
                                else         stage_data[g] <= |segment_error[START +: W];
                            end
                        end
                        // Stage >=2 takes input from stage_data of previous stage
                        else begin : sn
                            always @(posedge CLK or negedge RESETN) begin
                                if (!RESETN) stage_data[g] <= 1'b0;
                                else         stage_data[g] <= |or_stages[st-1].stage_data[START +: W];
                            end
                        end
                    end
                end
            end
        
            // Output registered from final stage (typically 1 bit at [0])
            always @(posedge CLK or negedge RESETN) begin
                if (!RESETN) MISMATCH <= 1'b0;
                else         MISMATCH <= or_stages[NUM_OR_STAGES].stage_data[0];
            end
        end

    endgenerate

endmodule
