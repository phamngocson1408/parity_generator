#!/bin/bash
# Run SIMPLE_TOP testbench with iverilog

cd /home/pnson/Workspace/Parity_Generator

echo "======================================================================"
echo "SIMPLE_TOP TESTBENCH SIMULATION"
echo "======================================================================"
echo ""

# Check if iverilog is available
if ! command -v iverilog &> /dev/null; then
    echo "⚠️  iverilog not found. Installing..."
    sudo apt-get update && sudo apt-get install -y iverilog
fi

# Compile
echo "1️⃣  Compiling Verilog..."
iverilog -o simple_top_sim \
    axicrypt/RTL/SIMPLE_TOP.v \
    test_modules/SIMPLE_TOP_tb.v

if [ $? -eq 0 ]; then
    echo "   ✅ Compilation successful"
else
    echo "   ❌ Compilation failed"
    exit 1
fi

# Simulate
echo ""
echo "2️⃣  Running simulation..."
vvp simple_top_sim

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✅ TESTBENCH EXECUTION COMPLETE"
    echo "======================================================================"
else
    echo "   ❌ Simulation failed"
    exit 1
fi
