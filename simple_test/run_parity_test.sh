#!/bin/bash
# Test runner for SIMPLE_TOP parity testbench

echo "========================================================================"
echo "         SIMPLE_TOP PARITY GENERATION & TESTING                        "
echo "========================================================================"
echo ""

WORKSPACE="/home/pnson/Workspace/Parity_Generator"
SIMPLE_TEST="$WORKSPACE/simple_test"

# Change to simple_test directory
cd "$SIMPLE_TEST"

# Compile Verilog
echo "1️⃣  Compiling Verilog files..."
iverilog -o parity_test.vvp \
    -I. \
    SIMPLE_TOP.v \
    SIMPLE_TOP_PARITY_TB.v

if [ $? -ne 0 ]; then
    echo "   ❌ Compilation failed!"
    exit 1
fi

echo "   ✅ Compilation successful"
echo ""

# Run simulation
echo "2️⃣  Running simulation..."
echo "========================================================================"
vvp parity_test.vvp

if [ $? -ne 0 ]; then
    echo "========================================================================"
    echo "   ❌ Simulation failed!"
    exit 1
fi

echo "========================================================================"
echo ""
echo "   ✅ Simulation completed successfully!"
echo ""

# Display test results
if grep -q "ALL TESTS PASSED" parity_test.vvp 2>/dev/null; then
    echo "✅ PARITY TESTBENCH VERIFICATION: PASSED"
else
    echo "⚠️  Check simulation output above for details"
fi

echo ""
