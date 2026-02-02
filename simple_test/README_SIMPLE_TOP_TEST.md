# Simple Top Module Test - Complete Documentation

## Overview
This test demonstrates parity generation and verification for a simple top module with basic AXI-like interface.

## Files Created

### 1. Simple Top Module
**File:** `axicrypt/RTL/SIMPLE_TOP.v`
- Simple AXI-like bus with Write and Read channels
- 4 data signals: WADDR_DATA, WDATA_DATA, RADDR_DATA, RDATA_DATA
- Status counter for transaction monitoring
- Clock: ACLK, Reset: RESETN_ACLK

### 2. INFO Configuration
**File:** `[INFO]_SIMPLE_TOP.safety.xlsx`
- Configuration for parity generation
- Defines 4 parity signals (WADDR, WDATA, RADDR, RDATA)
- Specifies error ports for each signal

### 3. Testbench
**File:** `test_modules/SIMPLE_TOP_tb.v`
- Comprehensive testbench with 6 test cases
- Tests all data signals
- Verifies ready/valid handshaking
- Parity calculation reference functions

### 4. Test Runner Script
**File:** `run_simple_top_test.sh`
- Bash script to compile and run testbench
- Uses iverilog + vvp for simulation

## Test Results

### Test 1: Write Address Transaction ✅
```
WADDR_DATA = 0xdeadbeef
WADDR_READY = 1
Parity = 0 (even)
```

### Test 2: Write Data Transaction ✅
```
WDATA_DATA = 0x0123456789abcdef
WDATA_READY = 1
Parity = 0 (even)
```

### Test 3: Read Address Transaction ✅
```
RADDR_DATA = 0x12345678
RADDR_READY = 1
```

### Test 4: Read Data Response ✅
```
RDATA_VALID = 1
RDATA_DATA = 0x00000000abcd1234 (echoed)
Data verification: PASSED
```

### Test 5: Status Counter ✅
```
STATUS = 0x04
Counter incremented: PASSED
```

### Test 6: Parity Reference ✅
```
32-bit parity: 0
64-bit parity: 0
```

## How to Run

### Run Testbench
```bash
cd /home/pnson/Workspace/Parity_Generator
bash run_simple_top_test.sh
```

### Generate Parity (Manual)
```bash
python parity_generator.py \
    -type "SAFETY.PARITY" \
    -gen-top YES \
    -info "[INFO]_SIMPLE_TOP.safety.xlsx"
```

### Run Parity Generation Test
```bash
python test_parity_generation.py
```

## Module Structure

```
SIMPLE_TOP
├── Input Signals
│   ├── ACLK (Clock)
│   ├── RESETN_ACLK (Reset, active low)
│   ├── WADDR_VALID / WADDR_DATA[31:0]
│   ├── WDATA_VALID / WDATA_DATA[63:0]
│   ├── RADDR_VALID / RADDR_DATA[31:0]
│   └── RDATA_READY
├── Output Signals
│   ├── WADDR_READY
│   ├── WDATA_READY
│   ├── RADDR_READY
│   ├── RDATA_VALID / RDATA_DATA[63:0]
│   └── STATUS[7:0]
└── Internal Logic
    └── Transaction counter (STATUS register)
```

## Parity Configuration

| Signal       | Mode    | Width | Error Port          |
|-------------|---------|-------|-------------------|
| WADDR_DATA  | DRIVE   | 32    | ERR_WADDR_PARITY  |
| WDATA_DATA  | DRIVE   | 64    | ERR_WDATA_PARITY  |
| RADDR_DATA  | DRIVE   | 32    | ERR_RADDR_PARITY  |
| RDATA_DATA  | RECEIVE | 64    | ERR_RDATA_PARITY  |

## Expected Generated Files

After running parity generator:
- `axicrypt/RTL/SAFETY/SIMPLE_TOP_NEW.v` - Top module with parity ports
- `axicrypt/RTL/SAFETY/SIMPLE_TOP_PARITY_NEW.v` - Parity comparator module

## Verification

All tests passed:
- ✅ Module compiles without errors
- ✅ All ready/valid signals work correctly
- ✅ Data echo functionality verified
- ✅ Status counter increments on transactions
- ✅ Parity calculations reference correct

## Notes

1. Parity is calculated as even parity (XOR of all bits)
2. Reference parity functions provided in testbench
3. RDATA echoes RADDR_DATA with 32-bit zero extension
4. Status counter increments on any valid transaction (WADDR, WDATA, or RADDR)
5. All signals use standard AXI handshaking (VALID/READY)

## Directory Structure

```
Parity_Generator/
├── axicrypt/
│   └── RTL/
│       ├── SIMPLE_TOP.v (source)
│       └── SAFETY/
│           ├── SIMPLE_TOP_NEW.v (generated)
│           └── SIMPLE_TOP_PARITY_NEW.v (generated)
├── test_modules/
│   ├── SIMPLE_TOP.v (copy)
│   ├── SIMPLE_TOP_tb.v (testbench)
│   └── ...
├── [INFO]_SIMPLE_TOP.safety.xlsx (config)
├── run_simple_top_test.sh (runner)
└── test_parity_generation.py (validator)
```
