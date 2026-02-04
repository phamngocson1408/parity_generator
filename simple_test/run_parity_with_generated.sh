#!/bin/bash
# Test runner for SIMPLE_TOP WITH EMBEDDED PARITY

echo "=========================================================================="
echo "    SIMPLE_TOP WITH EMBEDDED PARITY - COMPREHENSIVE TEST"
echo "=========================================================================="
echo ""

SIMPLE_TEST="/home/pnson/Workspace/Parity_Generator/simple_test"

# Change to simple_test directory
cd "$SIMPLE_TEST"

echo "📦 Files in use:"
echo "  ✅ SIMPLE_TOP_NEW.v - Top module with parity ports"
echo "  ✅ SIMPLE_TOP_PARITY_NEW.v - Parity comparator module"
echo "  ✅ SIMPLE_TOP_WITH_PARITY_TB.v - Comprehensive testbench"
echo ""

# Compile Verilog
echo "1️⃣  Compiling Verilog files..."
iverilog -o parity_with_gen_test.vvp \
    SIMPLE_TOP_NEW.v \
    SIMPLE_TOP_PARITY_NEW.v \
    SIMPLE_TOP_WITH_PARITY_TB.v

if [ $? -ne 0 ]; then
    echo "   ❌ Compilation failed!"
    exit 1
fi

echo "   ✅ Compilation successful"
echo ""

# Run simulation
echo "2️⃣  Running simulation..."
echo "=========================================================================="
vvp parity_with_gen_test.vvp

if [ $? -ne 0 ]; then
    echo "=========================================================================="
    echo "   ❌ Simulation failed!"
    exit 1
fi

echo "=========================================================================="
echo ""
echo "   ✅ Simulation completed successfully!"
echo ""
echo "✅ PARITY EMBEDDED TESTBENCH - VERIFICATION COMPLETE"
echo ""
