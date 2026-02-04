#!/bin/bash
# VCS Batch Simulation Script for SIMPLE_TOP Testbench
# Usage: ./run_vcs_batch.sh

echo "=========================================================================="
echo "  SIMPLE_TOP VCS Batch Simulation"
echo "=========================================================================="
echo ""

SIM_DIR="/home/pnson/Workspace/Parity_Generator/simple_test/SIM"
WORK_DIR="$SIM_DIR/work"
LOG_FILE="$WORK_DIR/sim.log"

# Create work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "📁 Simulation directories:"
echo "  SIM dir: $SIM_DIR"
echo "  Work dir: $WORK_DIR"
echo "  Log file: $LOG_FILE"
echo ""

# Check if filelist.f exists
if [ ! -f "$SIM_DIR/filelist.f" ]; then
    echo "❌ ERROR: filelist.f not found in $SIM_DIR"
    exit 1
fi
echo "✓ filelist.f found"

echo ""

# VCS compilation
echo "1️⃣  Running VCS compilation..."
echo "=========================================================================="

vcs -sverilog \
    -f "$SIM_DIR/filelist.f" \
    -o simv \
    -timescale=1ns/1ps \
    2>&1 | tee "$LOG_FILE"

if [ $? -ne 0 ]; then
    echo "=========================================================================="
    echo "   ❌ VCS Compilation FAILED!"
    exit 1
fi

echo "=========================================================================="
echo "   ✅ VCS Compilation successful"
echo ""

# Run simulation
echo "2️⃣  Running batch simulation..."
echo "=========================================================================="

./simv 2>&1 | tee -a "$LOG_FILE"

echo "=========================================================================="
echo ""
echo "   ✅ Simulation completed!"
echo ""
echo "   📄 Log file: $LOG_FILE"
echo ""
echo "=========================================================================="
echo ""
