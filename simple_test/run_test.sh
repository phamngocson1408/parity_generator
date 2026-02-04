#!/bin/bash
# Testbench Compilation and Simulation Script for SIMPLE_TOP_NEW

echo "=========================================================================="
echo "  SIMPLE_TOP_NEW with Parity - Testbench Runner"
echo "=========================================================================="
echo ""

TEST_DIR="/home/pnson/Workspace/Parity_Generator/simple_test"
SAFETY_DIR="$TEST_DIR/RTL/SAFETY"
BUILD_DIR="$TEST_DIR/build"

# Create build directory
mkdir -p "$BUILD_DIR"

echo "📁 Directories:"
echo "  Test dir: $TEST_DIR"
echo "  SAFETY dir: $SAFETY_DIR"
echo "  Build dir: $BUILD_DIR"
echo ""

# Check if required files exist
echo "✓ Checking files..."
if [ ! -f "$SAFETY_DIR/SIMPLE_TOP_NEW.v" ]; then
    echo "❌ ERROR: SIMPLE_TOP_NEW.v not found!"
    exit 1
fi
echo "  ✓ SIMPLE_TOP_NEW.v found"

if [ ! -f "$SAFETY_DIR/SIMPLE_TOP_PARITY_NEW.v" ]; then
    echo "❌ ERROR: SIMPLE_TOP_PARITY_NEW.v not found!"
    exit 1
fi
echo "  ✓ SIMPLE_TOP_PARITY_NEW.v found"

if [ ! -f "$TEST_DIR/SIMPLE_TOP_NEW_TB.v" ]; then
    echo "❌ ERROR: SIMPLE_TOP_NEW_TB.v not found!"
    exit 1
fi
echo "  ✓ SIMPLE_TOP_NEW_TB.v found"
echo ""

# Compile with iverilog
echo "1️⃣  Compiling Verilog files with iverilog..."
cd "$BUILD_DIR"

# Create stub modules for missing dependencies
cat > stubs.v << 'STUB_EOF'
// Stub modules for dependencies

module BOS_SOC_SYNCHSR #(parameter DW=1) (
    input I_CLK,
    input I_RESETN,
    input [DW-1:0] I_D,
    output reg [DW-1:0] O_Q
);
    always @(posedge I_CLK) begin
        if (!I_RESETN)
            O_Q <= 0;
        else
            O_Q <= I_D;
    end
endmodule

module DCLS_COMPARATOR_TEMPLATE #(parameter DATA_WIDTH=1, MAX_INPUT_WIDTH=64, NUM_OR_STAGES=0) (
    input CLK,
    input RESETN,
    input [DATA_WIDTH-1:0] DATA_IN_A,
    input [DATA_WIDTH-1:0] DATA_IN_B,
    input ENERR_DCLS,
    input FIERR_DCLS,
    output ERR_DCLS,
    output ERR_DCLS_B
);
    assign ERR_DCLS = (DATA_IN_A != DATA_IN_B);
    assign ERR_DCLS_B = (DATA_IN_A != DATA_IN_B);
endmodule
STUB_EOF

iverilog -g2009 -o sim.vvp \
    stubs.v \
    "$SAFETY_DIR/SIMPLE_TOP_NEW.v" \
    "$SAFETY_DIR/SIMPLE_TOP_PARITY_NEW.v" \
    "$TEST_DIR/SIMPLE_TOP_NEW_TB.v" \
    2>&1

if [ $? -ne 0 ]; then
    echo "   ❌ Compilation FAILED!"
    exit 1
fi
echo "   ✅ Compilation successful"
echo ""

# Run simulation
echo "2️⃣  Running simulation with vvp..."
echo "=========================================================================="
vvp sim.vvp

if [ $? -ne 0 ]; then
    echo "=========================================================================="
    echo "   ❌ Simulation FAILED!"
    exit 1
fi

echo "=========================================================================="
echo ""
echo "   ✅ Simulation completed successfully!"
echo ""
echo "✅ TESTBENCH EXECUTION COMPLETE"
echo "=========================================================================="
echo ""
