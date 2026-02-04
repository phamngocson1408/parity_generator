#!/bin/bash
# VCS Simulation Script for SIMPLE_TOP Testbench
# Usage: ./run_vcs.sh

echo "=========================================================================="
echo "  SIMPLE_TOP VCS Simulation Script"
echo "=========================================================================="
echo ""

SIM_DIR="/home/pnson/Workspace/Parity_Generator/simple_test/SIM"
WORK_DIR="$SIM_DIR/work"

# Create work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "📁 Simulation directories:"
echo "  SIM dir: $SIM_DIR"
echo "  Work dir: $WORK_DIR"
echo ""

# Check if filelist.f exists
if [ ! -f "$SIM_DIR/filelist.f" ]; then
    echo "❌ ERROR: filelist.f not found in $SIM_DIR"
    exit 1
fi
echo "✓ filelist.f found"

echo ""

# VCS compilation and simulation
echo "1️⃣  Running VCS compilation and simulation..."
echo "=========================================================================="

vcs -sverilog \
    -f "$SIM_DIR/filelist.f" \
    -o simv \
    -debug_all \
    -timescale=1ns/1ps

if [ $? -ne 0 ]; then
    echo "=========================================================================="
    echo "   ❌ VCS Compilation FAILED!"
    exit 1
fi

echo "=========================================================================="
echo "   ✅ VCS Compilation successful"
echo ""

# Run simulation
echo "2️⃣  Running simulation..."
echo "=========================================================================="

./simv -gui &

echo "=========================================================================="
echo ""
echo "   ✅ Simulation started!"
echo ""
echo "=========================================================================="
echo ""
