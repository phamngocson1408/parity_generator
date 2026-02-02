# SIMPLE_TOP Parity Testbench Documentation

## 📋 Overview

This testbench (`SIMPLE_TOP_PARITY_TB.v`) provides comprehensive testing of parity generation, detection, and fault injection capabilities for the SIMPLE_TOP module. It simulates real-world scenarios including correct parity, parity errors, and burst transactions.

## 🎯 Test Cases

### ✅ Test 1: WADDR Transaction (Correct Parity)
- **Purpose**: Verify write address parity calculation and acceptance
- **Input Data**: 0x12345678
- **Calculated Parity**: 1 (Even parity)
- **Expected Result**: Module accepts transaction, ERR_WADDR_PARITY = 0
- **Status**: ✅ PASSED

### ✅ Test 2: WDATA Transaction (Correct Parity)
- **Purpose**: Verify write data parity with 64-bit width
- **Input Data**: 0x0123456789ABCDEF
- **Calculated Parity**: 0 (Even parity)
- **Expected Result**: Module accepts transaction, ERR_WDATA_PARITY = 0
- **Status**: ✅ PASSED

### ✅ Test 3: RADDR Transaction (Correct Parity)
- **Purpose**: Verify read address parity calculation
- **Input Data**: 0xDEADBEEF
- **Calculated Parity**: 0 (Even parity)
- **Expected Result**: Module accepts transaction, ERR_RADDR_PARITY = 0
- **Status**: ✅ PASSED

### ✅ Test 4: RDATA Response (Correct Parity)
- **Purpose**: Verify read data parity verification
- **Echo Data**: Read address echoed as 64-bit (0x00000000DEADBEEF)
- **Calculated Parity**: 0 (Even parity)
- **Expected Result**: No parity error, ERR_RDATA_PARITY = 0
- **Status**: ✅ PASSED

### ✅ Test 5: Fault Injection (WRONG Parity)
- **Purpose**: Verify error detection with intentional parity corruption
- **Input Data**: 0xCAFEBABE
- **Correct Parity**: 0 (Even)
- **Injected Parity**: 1 (WRONG - Odd)
- **Expected Result**: Parity mismatch detected, ERR_WADDR_PARITY = 1
- **Status**: ✅ PASSED

### ✅ Test 6: Burst Mode (Multiple Transactions)
- **Purpose**: Verify sustained parity generation across multiple back-to-back transactions
- **Transactions**:
  1. Addr=0x10000000, Parity=1
  2. Addr=0x10000100, Parity=0
  3. Addr=0x10000200, Parity=0
  4. Addr=0x10000300, Parity=1
- **Expected Result**: All 4 transactions processed correctly with proper parity
- **Status**: ✅ PASSED

## 📊 Parity Calculation

The testbench uses even parity (XOR of all bits):

```verilog
function automatic logic calculate_parity_32bit(input [31:0] data);
    logic parity = 1'b0;
    for (i = 0; i < 32; i++) 
        parity ^= data[i];
endfunction

function automatic logic calculate_parity_64bit(input [63:0] data);
    logic parity = 1'b0;
    for (i = 0; i < 64; i++) 
        parity ^= data[i];
endfunction
```

**Even Parity Rule**: Parity bit = 1 if number of 1-bits is odd, 0 if even

## 🔍 Signal Monitoring

The testbench monitors all transactions in real-time:

```
[T=105000ns] WADDR Transaction: 0x12345678, Parity=1, Ready=1
[T=135000ns] WDATA Transaction: 0x0123456789abcdef, Parity=0, Ready=1
[T=165000ns] RADDR Transaction: 0xdeadbeef, Parity=0, Ready=1
[T=245000ns] WADDR Transaction: 0xcafebabe, Parity=1 (ERROR INJECTED), Ready=1
```

## 📈 Test Results

```
╔══════════════════════════════════════════════════════════════╗
║                      TEST SUMMARY                           ║
╠══════════════════════════════════════════════════════════════╣
║  Total Tests:       6
║  Passed:            6 ✅
║  Failed:            0 ❌
║  Success Rate:      100%
╚══════════════════════════════════════════════════════════════╝
```

## 🚀 How to Run

### Option 1: Run Bash Script
```bash
cd simple_test/
bash run_parity_test.sh
```

### Option 2: Manual Compilation & Simulation
```bash
cd simple_test/

# Compile
iverilog -o parity_test.vvp SIMPLE_TOP.v SIMPLE_TOP_PARITY_TB.v

# Simulate
vvp parity_test.vvp
```

## 📝 File Structure

```
simple_test/
├── SIMPLE_TOP.v                  # Module under test
├── SIMPLE_TOP_PARITY_TB.v       # Comprehensive testbench (this file)
├── run_parity_test.sh           # Test runner script
├── [INFO]_SIMPLE_TOP.safety.xlsx # Parity configuration
└── generate_parity_simple.py    # Parity generation script
```

## ⚙️ Features

### 1. **Even Parity Calculation**
- Correctly calculates even parity for 32-bit and 64-bit data
- Supports multi-bit XOR operations

### 2. **Fault Injection**
- Intentionally corrupts parity to verify error detection
- Demonstrates system capability to catch parity errors

### 3. **Transaction Monitoring**
- Real-time logging of all transactions
- Timestamp and signal value reporting
- READY/VALID handshaking verification

### 4. **Burst Mode Testing**
- Multiple back-to-back transactions
- Verifies sustained correct operation
- Tests system under load

### 5. **Comprehensive Reporting**
- Beautiful ASCII table output
- Detailed test case descriptions
- Summary statistics
- Success/failure indication

## 🔧 Parity Signals

| Signal           | Width | Direction | Description                    |
|-----------------|-------|-----------|-------------------------------|
| WADDR_PARITY    | 1     | Input     | Write address parity (32-bit) |
| ERR_WADDR_PARITY| 1     | Output    | Write address parity error    |
| WDATA_PARITY    | 1     | Input     | Write data parity (64-bit)    |
| ERR_WDATA_PARITY| 1     | Output    | Write data parity error       |
| RADDR_PARITY    | 1     | Input     | Read address parity (32-bit)  |
| ERR_RADDR_PARITY| 1     | Output    | Read address parity error     |
| RDATA_PARITY    | 1     | Input     | Read data parity (64-bit)     |
| ERR_RDATA_PARITY| 1     | Output    | Read data parity error        |

## 📊 Simulation Timing

- **Clock Period**: 10ns (100MHz)
- **Reset Duration**: 50ns (5 clock cycles)
- **Total Simulation Time**: ~460ns
- **Clock Cycles**: ~46

## ✅ Expected Output

All tests should show:
- ✅ green check marks for passed tests
- ❌ red X marks for failed tests (if any)
- Timestamped transaction logs
- 100% success rate

## 🐛 Troubleshooting

### Compilation Errors
```bash
# Ensure iverilog is installed
sudo apt-get install iverilog

# Run with verbose mode
iverilog -g2 -o parity_test.vvp SIMPLE_TOP.v SIMPLE_TOP_PARITY_TB.v
```

### Simulation Issues
```bash
# Check simulation output
vvp parity_test.vvp 2>&1 | head -50

# Enable all debug output
vvp -v parity_test.vvp
```

## 🔄 Extension Points

The testbench can be extended for:

1. **Additional Data Patterns**
   - All-zeros pattern (0x00000000)
   - All-ones pattern (0xFFFFFFFF)
   - Alternating patterns (0xAAAAAAAA, 0x55555555)

2. **Parity Error Detection**
   - Multiple bit errors
   - Specific bit error locations
   - Statistical error patterns

3. **Performance Testing**
   - Maximum transaction rate
   - Throughput measurement
   - Latency analysis

4. **Integration Testing**
   - Interface handshaking
   - Multi-transaction pipelines
   - System-level verification

## 📚 References

- **Parity**: Wikipedia - Parity bit (https://en.wikipedia.org/wiki/Parity_bit)
- **SIMPLE_TOP**: See SIMPLE_TOP.v module definition
- **Verilog**: IEEE Std 1364-2005

## 👤 Author Notes

This testbench is designed to be:
- **Comprehensive**: Covers all major test scenarios
- **Readable**: Clear output and well-commented code
- **Maintainable**: Modular design for easy extension
- **Realistic**: Simulates actual hardware operations

## 📋 Version History

| Version | Date       | Changes                          |
|---------|------------|--------------------------------|
| 1.0     | 2026-02-02 | Initial comprehensive testbench |

---

**Status**: ✅ All 6 tests passing  
**Last Run**: 2026-02-02  
**Success Rate**: 100%
