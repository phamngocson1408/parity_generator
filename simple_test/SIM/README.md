# SIMPLE_TOP Simulation Directory

This directory contains the simulation setup for SIMPLE_TOP_TB testbench using VCS.

## Directory Structure

```
SIM/
├── filelist.f                  # File list containing references to RTL modules
├── SIMPLE_TOP_TB.v             # Testbench module
├── run_vcs.sh                  # VCS GUI simulation script
├── run_vcs_batch.sh            # VCS batch (non-interactive) simulation script
├── work/                       # Working directory (created during simulation)
│   ├── simv                    # Compiled VCS executable
│   ├── sim.log                 # Simulation log file
│   └── csrc/                   # C source files
└── README.md                   # This file
```

## Files

### filelist.f
Contains references to the RTL modules needed for simulation:
- `../RTL/SAFETY/SIMPLE_TOP_NEW.v` - Generated module with parity ports
- `../RTL/SAFETY/SIMPLE_TOP_PARITY_NEW.v` - Parity generator module

### SIMPLE_TOP_TB.v
Comprehensive testbench that tests:
- Basic AXI-like interface functionality
- Write address channel
- Write data channel
- Read address channel
- Read data channel
- Status output
- Parity ports connectivity

### run_vcs.sh
Starts VCS simulation with GUI mode. Useful for interactive debugging and waveform viewing.

**Usage:**
```bash
./run_vcs.sh
```

This will:
1. Compile the RTL and testbench with VCS
2. Launch the VCS GUI with DVE waveform viewer
3. Allow you to run simulation and inspect signals interactively

### run_vcs_batch.sh
Runs VCS simulation in batch mode (non-interactive). Results are logged to `work/sim.log`.

**Usage:**
```bash
./run_vcs_batch.sh
```

This will:
1. Compile the RTL and testbench with VCS
2. Run the simulation
3. Generate log file with test results

## How to Run

### Interactive GUI Mode:
```bash
cd /home/pnson/Workspace/Parity_Generator/simple_test/SIM
./run_vcs.sh
```

### Batch Mode:
```bash
cd /home/pnson/Workspace/Parity_Generator/simple_test/SIM
./run_vcs_batch.sh
```

## Test Coverage

The testbench `SIMPLE_TOP_TB.v` includes:

1. **Test 1: Write Address Channel** - Tests WADDR_VALID/WADDR_DATA transactions
2. **Test 2: Write Data Channel** - Tests WDATA_VALID/WDATA_DATA transactions
3. **Test 3: Read Address Channel** - Tests RADDR_VALID/RADDR_DATA and validates RDATA response
4. **Test 4: Sequential Transactions** - Tests back-to-back write then read operations
5. **Test 5: Back-to-Back Transactions** - Tests multiple consecutive read requests

## Expected Output

When running the testbench, you should see:
- Clock generation starting (100MHz, 10ns period)
- Reset sequence completion
- Individual test results with PASS/FAIL status
- Final test summary with total tests, passed, and failed counts
- Parity verification results for each transaction

## Requirements

- **VCS**: Synopsys VCS simulator installed and in PATH
- **SystemVerilog Support**: VCS with -sverilog flag support

## Notes

- The simulation uses a 10ns clock period (100MHz)
- All tests use even parity
- The testbench is self-checking with automatic pass/fail reporting
- For GUI mode, DVE (Design and Verification Environment) is required

## Troubleshooting

### "vcs: command not found"
Make sure VCS is installed and in your PATH. Try:
```bash
which vcs
```

### Compilation errors
Check that both `filelist.f` points to valid files:
- `../RTL/SAFETY/SIMPLE_TOP_NEW.v`
- `../RTL/SAFETY/SIMPLE_TOP_PARITY_NEW.v`

### Module not found errors
Verify the file paths in `filelist.f` are relative to the SIM directory.

## Contact

For issues or questions about this simulation setup, refer to the main project documentation.
