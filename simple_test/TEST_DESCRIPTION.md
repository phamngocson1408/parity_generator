# SIMPLE_TOP_TB - Testbench Description

## Overview
Comprehensive testbench for **SIMPLE_TOP** module with embedded parity generation and verification capability. The testbench validates both functional behavior and parity error detection.

---

## Test Architecture

### Parity Mode: RECEIVER
- **RECEIVE Ports**: `WADDR_PARITY`, `WDATA_PARITY`, `RADDR_PARITY`
  - Testbench sends data + parity value
  - Module receives both and compares
  - Error signals indicate parity mismatch
  
- **DRIVE Port**: `RDATA_PARITY`
  - Module generates parity for read data output
  - Testbench monitors for correctness

### Fault Injection
- `FIERR_WADDR_PARITY`: Single fault injection - flips parity on WADDR channel
- `ENERR_WADDR_PARITY`: Error detection enable - activates error signaling

---

## Individual Test Descriptions

### **Test 1: Write Address Channel with Parity (5 transactions)**
- **Purpose**: Verify WADDR channel accepts data with correct parity
- **Actions**:
  1. Generate 5 different 32-bit addresses (DEADBEEF + i)
  2. Calculate even parity for each address
  3. Send both data and parity to module
  4. Verify WADDR_READY asserted
- **Expected**: All transactions accepted, parity values correct
- **Validates**: WADDR port functionality with RECEIVE parity

---

### **Test 2: Write Data Channel with Parity (5 transactions)**
- **Purpose**: Verify WDATA channel accepts data with correct parity
- **Actions**:
  1. Generate 5 different 64-bit data values (CAFEBABEDEADBEEF + i)
  2. Calculate even parity for each data word
  3. Send both data and parity to module
  4. Verify WDATA_READY asserted
- **Expected**: All transactions accepted, parity values correct
- **Validates**: WDATA port functionality with RECEIVE parity

---

### **Test 3: Read Address Channel with Parity (5 transactions)**
- **Purpose**: Verify RADDR channel accepts address with correct parity
- **Actions**:
  1. Generate 5 different 32-bit addresses (BEEFCAFE + i)
  2. Calculate even parity for each address
  3. Send both address and parity to module
  4. Verify RADDR_READY asserted
  5. Wait for echoed read data on RDATA channel
- **Expected**: All transactions accepted, data echoed correctly
- **Validates**: RADDR port functionality + read data echo logic

---

### **Test 4: Back-to-Back Transactions with Parity (3 transactions)**
- **Purpose**: Verify module handles simultaneous WADDR + WDATA transactions
- **Actions**:
  1. Assert both WADDR_VALID and WDATA_VALID simultaneously
  2. Provide correct parity for both channels
  3. Send 3 back-to-back transactions
- **Expected**: Both channels remain ready, parities accepted
- **Validates**: Channel independence, no cross-channel interference

---

### **Test 5: Parity Value Correctness (2 transactions)**
- **Purpose**: Verify parity calculation correctness for edge cases
- **Actions**:
  1. **Case A**: Send all-zeros (0x00000000)
     - Expected parity: 0 (even number of 1s = 0)
  2. **Case B**: Send all-ones (0xFFFFFFFF)  
     - Expected parity: 0 (32 ones = even, XOR = 0)
- **Expected**: Module accepts both, parity calculations correct
- **Validates**: Parity algorithm correctness (even parity = XOR of all bits)

---

### **Test 6: Parity Input Verification - RECEIVE Ports (2 transactions)**
- **Purpose**: Verify RECEIVE parity input ports function correctly
- **Actions**:
  1. Send WADDR transaction with calculated parity
  2. Send WDATA transaction with calculated parity
  3. Verify both channels accept the transactions
- **Expected**: Both transactions pass, channels remain ready
- **Validates**: Parity input ports properly connected and processed

---

### **Test 7: RDATA Parity Output - DRIVE Port (1 transaction)**
- **Purpose**: Verify RDATA parity is generated correctly (DRIVE mode)
- **Actions**:
  1. Send RADDR read request with address (0xAABBCCDD) and parity
  2. Wait for RDATA output to appear
  3. Check if RDATA_VALID asserted
  4. Verify RDATA_PARITY matches calculated value
- **Expected**: RDATA valid within 3 cycles, parity output correct
- **Validates**: RDATA parity generation (module calculates parity for output)

---

### **Test 8: Error Signal Monitoring (2 fault injection tests)**

#### **Test 8a: Normal Operation (FIERR = 0)**
- **Purpose**: Baseline - verify no error with correct parity
- **Actions**:
  1. Set FIERR_WADDR_PARITY = 0 (no fault injection)
  2. Send WADDR transaction (0xDEADBEEF) with correct parity
  3. Monitor error signals (ERR_WADDR_PARITY, ERR_WADDR_PARITY_B)
- **Expected**: Error signals remain LOW (no error detected)
- **Validates**: Correct parity passes verification

#### **Test 8b: Fault Injection (FIERR = 1)**
- **Purpose**: Verify error detection when parity is corrupted
- **Actions**:
  1. Set FIERR_WADDR_PARITY = 1 (enable fault injection)
  2. Send WADDR transaction (0xCAFEBABE) with correct parity
  3. Monitor error signals for detection
- **Expected**: Module injects fault and detects parity error
- **Validates**: Error detection capability (ERR_WADDR_PARITY asserts)

---

## Port Connectivity Reference

### Data Channels (Original SIMPLE_TOP)
| Port | Direction | Width | Purpose |
|------|-----------|-------|---------|
| WADDR_DATA | Input | 32-bit | Write address |
| WDATA_DATA | Input | 64-bit | Write data |
| RADDR_DATA | Input | 32-bit | Read address |
| RDATA_DATA | Output | 64-bit | Read data (echoed) |

### Parity Ports (RECEIVE - Testbench provides)
| Port | Direction | Width | Purpose |
|------|-----------|-------|---------|
| WADDR_PARITY | Input | 1-bit | Write address parity (testbench) |
| WDATA_PARITY | Input | 1-bit | Write data parity (testbench) |
| RADDR_PARITY | Input | 1-bit | Read address parity (testbench) |

### Parity Ports (DRIVE - Module generates)
| Port | Direction | Width | Purpose |
|------|-----------|-------|---------|
| RDATA_PARITY | Output | 1-bit | Read data parity (module calculates) |

### Control & Error Signals
| Port | Direction | Width | Purpose |
|------|-----------|-------|---------|
| FIERR_WADDR_PARITY | Input | 1-bit | Fault injection enable (for WADDR) |
| ENERR_WADDR_PARITY | Input | 1-bit | Error detection enable |
| ERR_WADDR_PARITY | Output | 1-bit | Error flag (parity mismatch detected) |
| ERR_WADDR_PARITY_B | Output | 1-bit | Error flag inverted (redundancy) |

---

## Test Results Summary

### Counters Tracked
- `test_count`: Total number of test transactions
- `pass_count`: Functional tests that passed
- `fail_count`: Functional tests that failed
- `parity_pass`: Parity-related tests that passed
- `parity_fail`: Parity-related tests that failed
- `injection_pass`: Fault injection tests that passed
- `injection_fail`: Fault injection tests that failed

### Expected Results
```
✓✓✓ ALL TESTS PASSED! ✓✓✓

Functional Tests: 20 total
  Passed: 20 ✓
  Failed: 0 ✗

Parity Tests: 15 total
  Passed: 15 ✓
  Failed: 0 ✗

Fault Injection Tests: 6 total
  Passed: 6 ✓
  Failed: 0 ✗
```

---

## Key Testing Insights

1. **RECEIVE Parity**: Testbench must calculate and drive parity before asserting VALID
2. **Even Parity**: XOR of all data bits should equal 0 for valid parity
3. **DRIVE Parity**: Module generates RDATA_PARITY automatically, no input needed
4. **Error Detection**: Works in conjunction with fault injection (FIERR_*) signals
5. **Redundancy**: Error signal has inverted output (ERR_*_B) for error detection robustness

---

## Simulation Runtime
- Clock period: 10ns (100MHz)
- Total test time: ~1.6μs
- Total transactions tested: 28 (5+5+5+3+2+2+1+0)
- Fault injection scenarios: 2 (with/without FIERR)
