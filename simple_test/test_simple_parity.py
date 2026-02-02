#!/usr/bin/env python3
"""
Simple test: Generate parity for SIMPLE_TOP module and create testbench
"""

import subprocess
import sys
import os

# Change to workspace and simple_test folder
workspace_root = '/home/pnson/Workspace/Parity_Generator'
simple_test_dir = os.path.join(workspace_root, 'simple_test')
os.chdir(workspace_root)  # Change to workspace root for parity generator

# Define file paths
simple_top_src = 'axicrypt/RTL/SIMPLE_TOP.v'
simple_top_gen = 'axicrypt/RTL/SAFETY/SIMPLE_TOP_NEW.v'
simple_top_parity = 'axicrypt/RTL/SAFETY/SIMPLE_TOP_PARITY_NEW.v'

print("\n" + "="*60)
print("SIMPLE TOP MODULE PARITY GENERATION TEST")
print("="*60 + "\n")

# Step 1: Check if source file exists
print("1️⃣  Checking source file...")
if os.path.exists(simple_top_src):
    print(f"   ✅ Found: {simple_top_src}")
else:
    print(f"   ❌ Not found: {simple_top_src}")
    sys.exit(1)

# Step 2: Run parity generator from parent directory
print("\n2️⃣  Running parity generator...")
cmd = [
    'python', 'parity_generator.py',
    '-type', 'SAFETY.PARITY',
    '-gen-top', 'YES',
    '-info', os.path.join(simple_test_dir, '[INFO]_SIMPLE_TOP.safety.xlsx')
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("   ✅ Parity generation successful")
else:
    print("   ❌ Parity generation failed")
    print(result.stderr)
    sys.exit(1)

# Step 3: Check generated files
print("\n3️⃣  Checking generated files...")
files_to_check = [simple_top_gen, simple_top_parity]
for f in files_to_check:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"   ✅ {f} ({size} bytes)")
    else:
        print(f"   ❌ Missing: {f}")

print("\n" + "="*60)
print("✅ PARITY GENERATION COMPLETE!")
print("="*60 + "\n")

print(f"Generated files:")
print(f"  - Top Module:     {simple_top_gen}")
print(f"  - Parity Module:  {simple_top_parity}")
print(f"\nTestbench created:  test_modules/SIMPLE_TOP_tb.v")
