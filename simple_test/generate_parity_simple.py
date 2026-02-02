#!/usr/bin/env python3
"""
Generate parity for SIMPLE_TOP module directly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, '/home/pnson/Workspace/Parity_Generator')

# Move to parent directory
os.chdir('/home/pnson/Workspace/Parity_Generator')

# Import parity generator components
from DCLS_generator.ClassExtractINFO.ExtractINFO import ExtractINFO
from DCLS_generator.GenerateVerilog.GenerateParity.GenerateParity import GenerateParity

def generate_parity():
    """Generate parity modules and top module"""
    
    info_path = 'simple_test/[INFO]_SIMPLE_TOP.safety.xlsx'
    sheet_name = 'SAFETY.PARITY'
    
    print("\n" + "="*60)
    print("PARITY GENERATION FOR SIMPLE_TOP")
    print("="*60 + "\n")
    
    # Step 1: Extract INFO
    print("1️⃣  Extracting INFO from Excel file...")
    try:
        info_extractor = ExtractINFO(info_path, sheet_name)
        info_dict_list = info_extractor._read_info_multi()
        print(f"   ✅ Found {len(info_dict_list)} signal configurations\n")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 2: Generate parity for each signal
    print("2️⃣  Generating parity module and top module...")
    try:
        gen_parity = GenerateParity(info_dict_list)
        
        # Generate parity module
        parity_module_name = f"{info_dict_list[0]['IP NAME']}_PARITY_NEW"
        parity_module_verilog = gen_parity.generate_parity_module()
        
        # Generate top module with parity ports
        top_module_name = f"{info_dict_list[0]['IP NAME']}_NEW"
        top_module_verilog = gen_parity.generate_top_module()
        
        # Save parity module
        parity_output = f"axicrypt/RTL/SAFETY/SIMPLE_TOP_PARITY_NEW.v"
        os.makedirs(os.path.dirname(parity_output), exist_ok=True)
        with open(parity_output, 'w') as f:
            f.write(parity_module_verilog)
        print(f"   ✅ Saved parity module: {parity_output}")
        
        # Save top module
        top_output = f"axicrypt/RTL/SAFETY/SIMPLE_TOP_NEW.v"
        with open(top_output, 'w') as f:
            f.write(top_module_verilog)
        print(f"   ✅ Saved top module: {top_output}")
        
        # Also copy to simple_test folder
        top_simple_test = 'simple_test/SIMPLE_TOP_NEW.v'
        parity_simple_test = 'simple_test/SIMPLE_TOP_PARITY_NEW.v'
        
        with open(top_simple_test, 'w') as f:
            f.write(top_module_verilog)
        print(f"   ✅ Copied to: {top_simple_test}")
        
        with open(parity_simple_test, 'w') as f:
            f.write(parity_module_verilog)
        print(f"   ✅ Copied to: {parity_simple_test}\n")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = generate_parity()
    
    if success:
        print("✅ PARITY GENERATION COMPLETE!")
        print("\nGenerated files:")
        print("  - SIMPLE_TOP_NEW.v (top module with parity ports)")
        print("  - SIMPLE_TOP_PARITY_NEW.v (parity comparator module)")
    else:
        print("❌ PARITY GENERATION FAILED!")
        sys.exit(1)
