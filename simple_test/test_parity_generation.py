#!/usr/bin/env python3
"""
Test suite for Parity Generation
Validates:
1. Parity module syntax and structure
2. Top module parity ports and instance
3. Fault injection ports connectivity
4. No duplicate ports
"""

import re
import sys


class ParityGenerationTest:
    def __init__(self):
        self.parity_file = 'axicrypt/RTL/SAFETY/BOS_AXICRYPT_PARITY_NEW.v'
        self.top_file = 'axicrypt/RTL/SAFETY/BOS_AXICRYPT_NEW.v'
        self.ori_file = 'axicrypt/RTL/BOS_AXICRYPT.v'
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def test(self, name, condition, message=""):
        """Print test result"""
        if condition:
            print(f"✅ PASS: {name}")
            self.passed += 1
        else:
            print(f"❌ FAIL: {name}")
            if message:
                print(f"   {message}")
            self.failed += 1

    def warn(self, name, message):
        """Print warning"""
        print(f"⚠️  WARN: {name}")
        print(f"   {message}")
        self.warnings += 1

    def extract_ports(self, content, module_name):
        """Extract input and output ports from module"""
        match = re.search(rf'module {module_name}\s*\((.*?)\);', content, re.DOTALL)
        if not match:
            return None, None, None

        port_decl = match.group(1)
        inputs = re.findall(r'input\s+(?:wire\s+)?(?:\[.*?\]\s+)?(\w+)', port_decl)
        outputs = re.findall(r'output\s+(?:wire\s+)?(?:\[.*?\]\s+)?(\w+)', port_decl)

        # Remove keywords
        inputs = [p for p in inputs if p not in ['wire', 'reg', 'parameter']]
        outputs = [p for p in outputs if p not in ['wire', 'reg', 'parameter']]

        return inputs, outputs, port_decl

    def test_parity_module(self):
        """Test 1: Parity Module Structure"""
        print("\n" + "="*60)
        print("TEST 1: PARITY MODULE STRUCTURE")
        print("="*60)

        try:
            with open(self.parity_file, 'r') as f:
                content = f.read()
        except:
            self.test("Parity module file exists", False, f"Cannot read {self.parity_file}")
            return

        # Test 1.1: Module declaration
        has_module = 'module BOS_AXICRYPT_IP_PARITY_GEN' in content
        self.test("Parity module declared with correct name", has_module)

        # Test 1.2: Extract ports
        inputs, outputs, _ = self.extract_ports(content, 'BOS_AXICRYPT_IP_PARITY_GEN')
        self.test("Parity module inputs extracted", inputs is not None and len(inputs) > 0)
        self.test("Parity module outputs extracted", outputs is not None and len(outputs) > 0)

        if inputs and outputs:
            print(f"   Found {len(inputs)} input ports and {len(outputs)} output ports")

        # Test 1.3: Check required ports
        required_inputs = ['ACLK']
        for port in required_inputs:
            has_port = any(port in inp or 'I_RESETN' in inp for inp in inputs)
            self.test(f"Parity module has {port} or I_RESETN", has_port)

        required_outputs = ['ERR_AXICRYPT_AXI_MI0_BUS_PARITY', 'ERR_AXICRYPT_AXI_MI0_BUS_PARITY_B']
        for port in required_outputs:
            has_port = port in outputs
            self.test(f"Parity module has output {port}", has_port)

        # Test 1.4: Check for FIERR port (fault injection)
        fierr_ports = [p for p in inputs if 'FIERR' in p]
        self.test("Parity module has FIERR (fault injection) ports", len(fierr_ports) > 0)
        if fierr_ports:
            print(f"   Found {len(fierr_ports)} FIERR ports: {fierr_ports}")

        # Test 1.5: No duplicate ports
        all_ports = inputs + outputs
        duplicates = [p for p in set(all_ports) if all_ports.count(p) > 1]
        self.test("Parity module has no duplicate ports", len(duplicates) == 0)
        if duplicates:
            print(f"   Duplicates: {duplicates}")

    def test_top_module(self):
        """Test 2: Top Module Integration"""
        print("\n" + "="*60)
        print("TEST 2: TOP MODULE INTEGRATION")
        print("="*60)

        try:
            with open(self.top_file, 'r') as f:
                top_content = f.read()
        except:
            self.test("Top module file exists", False, f"Cannot read {self.top_file}")
            return

        # Test 2.1: Parity instance exists
        has_instance = 'u_bos_axicrypt_ip_parity_gen' in top_content
        self.test("Parity instance declared in top module", has_instance)

        # Test 2.2: Extract top module ports
        top_inputs, top_outputs, _ = self.extract_ports(top_content, 'BOS_AXICRYPT')
        self.test("Top module inputs extracted", top_inputs is not None and len(top_inputs) > 0)
        self.test("Top module outputs extracted", top_outputs is not None and len(top_outputs) > 0)

        if top_inputs and top_outputs:
            print(f"   Found {len(top_inputs)} input ports and {len(top_outputs)} output ports")

        # Test 2.3: Check parity ports in top module
        parity_ports = ['ENERR_AXICRYPT_AXI_MI0_BUS_PARITY', 'FIERR_AXICRYPT_AXI_MI0_BUS_PARITY',
                        'ERR_AXICRYPT_AXI_MI0_BUS_PARITY', 'AXICRYPT_AXI_MI0_ARADDR_PARITY']
        
        for port in parity_ports:
            has_port = port in top_inputs + top_outputs
            self.test(f"Top module has parity port {port}", has_port)

        # Test 2.4: No duplicate ports
        all_top_ports = top_inputs + top_outputs
        duplicates = [p for p in set(all_top_ports) if all_top_ports.count(p) > 1]
        self.test("Top module has no duplicate ports", len(duplicates) == 0)
        if duplicates:
            print(f"   Duplicates: {duplicates}")

    def test_fault_injection(self):
        """Test 3: Fault Injection Connectivity"""
        print("\n" + "="*60)
        print("TEST 3: FAULT INJECTION CONNECTIVITY")
        print("="*60)

        try:
            with open(self.parity_file, 'r') as f:
                parity_content = f.read()
            with open(self.top_file, 'r') as f:
                top_content = f.read()
        except:
            self.test("Files readable", False)
            return

        # Test 3.1: Extract FIERR ports from parity module
        parity_inputs, _, _ = self.extract_ports(parity_content, 'BOS_AXICRYPT_IP_PARITY_GEN')
        fierr_parity = [p for p in parity_inputs if 'FIERR' in p]
        self.test("Parity module has FIERR inputs", len(fierr_parity) > 0)
        if fierr_parity:
            print(f"   FIERR ports in parity module: {fierr_parity}")

        # Test 3.2: Extract FIERR ports from top module
        top_inputs, _, _ = self.extract_ports(top_content, 'BOS_AXICRYPT')
        fierr_top = [p for p in top_inputs if 'FIERR' in p]
        self.test("Top module has FIERR inputs", len(fierr_top) > 0)
        if fierr_top:
            print(f"   FIERR ports in top module: {fierr_top}")

        # Test 3.3: Check instance port mapping for FIERR
        instance_match = re.search(r'u_bos_axicrypt_ip_parity_gen\s*\((.*?)\);', top_content, re.DOTALL)
        if instance_match:
            instance_decl = instance_match.group(1)
            for fierr_port in fierr_parity:
                # Check if FIERR port is connected in instance
                pattern = rf'\.{fierr_port}\s*\('
                has_connection = re.search(pattern, instance_decl)
                self.test(f"Instance connects FIERR port {fierr_port}", has_connection is not None)
        else:
            self.warn("Parity instance not found", "Cannot verify instance connections")

        # Test 3.4: FIERR naming convention (should be FIERR_*_PARITY)
        for port in fierr_parity:
            correct_name = 'FIERR' in port and 'PARITY' in port
            self.test(f"FIERR port {port} follows naming convention", correct_name)

    def test_port_preservation(self):
        """Test 4: Port Preservation from Original Module"""
        print("\n" + "="*60)
        print("TEST 4: PORT PRESERVATION")
        print("="*60)

        try:
            with open(self.ori_file, 'r') as f:
                ori_content = f.read()
            with open(self.top_file, 'r') as f:
                top_content = f.read()
        except:
            self.test("Files readable", False)
            return

        ori_inputs, ori_outputs, _ = self.extract_ports(ori_content, 'BOS_AXICRYPT')
        top_inputs, top_outputs, _ = self.extract_ports(top_content, 'BOS_AXICRYPT')

        # Test 4.1: Non-parity ports preserved
        non_parity_ports = [p for p in ori_inputs + ori_outputs if 'PARITY' not in p and 'FIERR_' not in p or ('FIERR_' in p and 'PARITY' not in p)]
        
        preserved = 0
        for port in non_parity_ports:
            if port in top_inputs + top_outputs:
                preserved += 1

        self.test(f"Non-parity ports preserved ({preserved}/{len(non_parity_ports)})", 
                 preserved == len(non_parity_ports))

        # Test 4.2: Key data ports present
        key_ports = ['AXICRYPT_AXI_MI0_ARADDR', 'AXICRYPT_AXI_MI0_AWADDR', 'AXICRYPT_AXI_SI0_RDATA']
        for port in key_ports:
            has_port = port in ori_inputs + ori_outputs and port in top_inputs + top_outputs
            self.test(f"Key data port {port} preserved", has_port)

        # Test 4.3: Non-parity error ports preserved
        error_ports = [p for p in ori_inputs + ori_outputs if 'ERR' in p and 'PARITY' not in p]
        for port in error_ports[:5]:  # Check first 5
            has_port = port in top_inputs + top_outputs
            self.test(f"Error port {port} preserved", has_port)

    def test_instance_connections(self):
        """Test 5: Instance Port Connections"""
        print("\n" + "="*60)
        print("TEST 5: INSTANCE PORT CONNECTIONS")
        print("="*60)

        try:
            with open(self.top_file, 'r') as f:
                top_content = f.read()
            with open(self.parity_file, 'r') as f:
                parity_content = f.read()
        except:
            self.test("Files readable", False)
            return

        # Extract parity module ports
        parity_inputs, parity_outputs, _ = self.extract_ports(parity_content, 'BOS_AXICRYPT_IP_PARITY_GEN')

        # Extract instance declaration
        instance_match = re.search(r'u_bos_axicrypt_ip_parity_gen\s*\((.*?)\);', top_content, re.DOTALL)
        if not instance_match:
            self.test("Parity instance found", False)
            return

        instance_decl = instance_match.group(1)

        # Test 5.1: All parity ports are connected
        if parity_inputs and parity_outputs:
            all_parity_ports = parity_inputs + parity_outputs
            connected = 0
            for port in all_parity_ports:
                if f'.{port}' in instance_decl:
                    connected += 1
            
            self.test(f"Instance connects all parity ports ({connected}/{len(all_parity_ports)})",
                     connected == len(all_parity_ports))

        # Test 5.2: Clock/reset port mapping (I_CLK -> ACLK, I_RESETN -> RESETN_ACLK)
        has_clk_map = '.I_CLK (ACLK)' in instance_decl or '.I_CLK(ACLK)' in instance_decl
        self.test("Clock port mapped correctly (I_CLK -> ACLK)", has_clk_map or 'I_CLK' not in instance_decl)

        has_reset_map = '.I_RESETN (RESETN_ACLK)' in instance_decl or '.I_RESETN(RESETN_ACLK)' in instance_decl
        self.test("Reset port mapped correctly (I_RESETN -> RESETN_ACLK)", has_reset_map or 'I_RESETN' not in instance_decl)

    def run_all_tests(self):
        """Run all tests"""
        print("\n")
        print("█" * 60)
        print("█" + " " * 58 + "█")
        print("█" + "  PARITY GENERATION TEST SUITE".center(58) + "█")
        print("█" + " " * 58 + "█")
        print("█" * 60)

        self.test_parity_module()
        self.test_top_module()
        self.test_fault_injection()
        self.test_port_preservation()
        self.test_instance_connections()

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print("="*60)

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n❌ {self.failed} TEST(S) FAILED!")
            return 1


if __name__ == "__main__":
    tester = ParityGenerationTest()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
