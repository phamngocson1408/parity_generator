# SIMPLE_TOP Simulation Setup Summary

## Project Structure

```
simple_test/
├── SIMPLE_TOP.v                    # Original baseline module (NO parity)
├── SIMPLE_TOP_TB.v                 # Original testbench
├── filelist.f                      # File list (root level)
│
├── RTL/
│   ├── SIMPLE_TOP.v                # Baseline module copy
│   ├── filelist.f                  # File list for generator
│   └── SAFETY/
│       ├── SIMPLE_TOP_NEW.v        # Generated module WITH parity ports
│       └── SIMPLE_TOP_PARITY_NEW.v # Generated parity module
│
└── SIM/                             # NEW Simulation Directory
    ├── filelist.f                   # References to generated modules
    ├── SIMPLE_TOP_TB.v              # Testbench copy
    ├── run_vcs.sh                   # VCS GUI simulation script (interactive)
    ├── run_vcs_batch.sh             # VCS batch simulation script (non-interactive)
    ├── README.md                    # Simulation setup documentation
    └── work/                        # Created during simulation
        ├── simv                     # VCS executable
        ├── sim.log                  # Simulation results log
        └── csrc/                    # VCS generated C source
```

## Workflow Summary

### 1. Original Module (SIMPLE_TOP.v)
- **Location**: `simple_test/SIMPLE_TOP.v` and `simple_test/RTL/SIMPLE_TOP.v`
- **Description**: Baseline module without parity functionality
- **Ports**: Standard AXI-like interface (WADDR, WDATA, RADDR, RDATA channels)

### 2. Parity Generation (parity_generator.py)
- **Input**: SIMPLE_TOP.v + [INFO]_SIMPLE_TOP.safety.xlsx
- **Process**: Analyzes INFO file and generates parity modules
- **Output Location**: `simple_test/RTL/SAFETY/`
  - `SIMPLE_TOP_NEW.v` - Enhanced module with parity ports added
  - `SIMPLE_TOP_PARITY_NEW.v` - Standalone parity generator module

### 3. Simulation Setup (SIM folder)
- **Location**: `simple_test/SIM/`
- **Contains**:
  - `SIMPLE_TOP_TB.v` - Comprehensive testbench
  - `filelist.f` - References to generated modules
  - `run_vcs.sh` - Interactive VCS simulation
  - `run_vcs_batch.sh` - Batch VCS simulation
  - `README.md` - Detailed documentation

## How to Run Simulation

### Option 1: Interactive VCS GUI
```bash
cd /home/pnson/Workspace/Parity_Generator/simple_test/SIM
./run_vcs.sh
```
- Opens VCS with DVE waveform viewer
- Allows interactive debugging and signal inspection
- Requires display/GUI capability

### Option 2: Batch Mode (Headless)
```bash
cd /home/pnson/Workspace/Parity_Generator/simple_test/SIM
./run_vcs_batch.sh
```
- Runs simulation non-interactively
- Outputs results to `work/sim.log`
- Suitable for CI/CD pipelines

## Testbench Features

The `SIMPLE_TOP_TB.v` testbench tests:

### Test Coverage
1. **Write Address Channel** - WADDR_VALID/WADDR_DATA transactions
2. **Write Data Channel** - WDATA_VALID/WDATA_DATA transactions
3. **Read Address Channel** - RADDR_VALID/RADDR_DATA with RDATA echo verification
4. **Sequential Transactions** - Back-to-back write→read operations
5. **Back-to-Back Transactions** - Multiple consecutive operations

### Test Parameters
- **Clock Frequency**: 100MHz (10ns period)
- **Parity Type**: Even parity (XOR all bits)
- **Number of Tests**: ~18 total (covers multiple scenarios)
- **Transactions**: Write address/data, read requests, sequential operations

## Generated Modules

### SIMPLE_TOP_NEW.v
**Purpose**: Enhanced version with parity support
**New Ports**:
- `FIERR_WADDR_PARITY` (input) - Fault injection for testing
- `RDATA_PARITY` (input) - Read data parity input
- `WADDR_PARITY` (output) - Generated write address parity
- `WDATA_PARITY` (output) - Generated write data parity
- `RADDR_PARITY` (output) - Generated read address parity

**Contains**: Embedded instance of SIMPLE_TOP_IP_PARITY_GEN for parity generation

### SIMPLE_TOP_PARITY_NEW.v
**Module Name**: SIMPLE_TOP_IP_PARITY_GEN
**Purpose**: Standalone parity generator
**Functions**:
- Calculates even parity for all data channels
- Compares received vs. calculated parity for error detection
- Supports fault injection for testing

## Configuration Files

### filelist.f (in SIM folder)
```
../RTL/SAFETY/SIMPLE_TOP_NEW.v
../RTL/SAFETY/SIMPLE_TOP_PARITY_NEW.v
```
References the generated RTL modules for compilation.

### [INFO]_SIMPLE_TOP.safety.xlsx
Excel configuration file with:
- **4 Rows** (one per parity channel)
- **Channels**: WADDR_DATA (32-bit), WDATA_DATA (64-bit), RADDR_DATA (32-bit), RDATA_DATA (64-bit)
- **Parity**: EVEN parity for all channels
- **File Reference**: Points to SIMPLE_TOP.v source location

## Quick Start

1. **Prepare**:
   ```bash
   cd /home/pnson/Workspace/Parity_Generator/simple_test/SIM
   ```

2. **Run Simulation** (choose one):
   ```bash
   # Interactive mode (with GUI)
   ./run_vcs.sh
   
   # Batch mode (headless)
   ./run_vcs_batch.sh
   ```

3. **Check Results**:
   ```bash
   cat work/sim.log  # View detailed results
   ```

## Expected Test Output

```
========================================================
  SIMPLE_TOP_WITH_PARITY - Test Results
========================================================
Total Tests: 18
  Passed: 18 ✓
  Failed: 0 ✗

✓ ALL TESTS PASSED!
========================================================
```

## Verification Points

Each test verifies:
- ✓ Transaction ready signal (READY = 1)
- ✓ Correct parity generation (XOR of all data bits)
- ✓ Proper data echo (for read operations)
- ✓ Signal timing and handshake protocol
- ✓ Status counter increments for valid transactions

## Requirements

- **VCS**: Synopsys VCS simulator (with -sverilog support)
- **DVE** (optional): For waveform viewing in GUI mode
- **Bash**: For running simulation scripts
- **Display** (GUI mode): X11 or equivalent

## File Locations Reference

| File | Location |
|------|----------|
| Baseline Module | `/simple_test/RTL/SIMPLE_TOP.v` |
| Generated Module (with parity) | `/simple_test/RTL/SAFETY/SIMPLE_TOP_NEW.v` |
| Parity Generator Module | `/simple_test/RTL/SAFETY/SIMPLE_TOP_PARITY_NEW.v` |
| Testbench | `/simple_test/SIM/SIMPLE_TOP_TB.v` |
| Filelist | `/simple_test/SIM/filelist.f` |
| VCS GUI Script | `/simple_test/SIM/run_vcs.sh` |
| VCS Batch Script | `/simple_test/SIM/run_vcs_batch.sh` |
| Simulation Log | `/simple_test/SIM/work/sim.log` |

## Notes

- All paths in filelist.f are relative to the SIM directory
- The parity generator script was run with the INFO file to create SIMPLE_TOP_NEW.v
- The testbench is self-checking with automatic PASS/FAIL reporting
- Both VCS scripts create a `work` directory for temporary files
- GUI mode requires VCS to be installed with DVE support
