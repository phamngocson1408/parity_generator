# Parity Generator Runner Script

Convenient bash script for running parity generation without manually typing Python commands:

## Quick Start

### Using Bash Script (Linux/macOS)

```bash
# Basic usage
./run_parity_generator.sh -info "[INFO]_BOS_AXICRYPT.safety.xlsx"

# With group filtering
./run_parity_generator.sh -info "simple_test/[INFO]_SIMPLE_TOP.safety.xlsx" -group "GROUP_A,GROUP_B"

# With custom instance name
./run_parity_generator.sh -info "[INFO]_BOS_AXICRYPT.safety.xlsx" -inst MY_CUSTOM_PARITY -gen-top NO

# Show help
./run_parity_generator.sh -h
```

## Command Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-info` | path | (required) | Path to INFO Excel file |
| `-inst` | string | BOS_BUS_PARITY_AXI_M | Parity instance name |
| `-type` | string | SAFETY.PARITY | Parity scheme type |
| `-group` | string | ALL | GROUP filter: comma-separated names or 'ALL' for all groups |
| `-gen-top` | yes/no | YES | Generate top wrapper module |
| `-h, --help` | - | - | Show help message |

## Features

### Bash Script (`run_parity_generator.sh`)
- ✓ Automatic Python environment detection (.venv312 or .venv)
- ✓ Colored output for better readability
- ✓ Configuration summary before execution
- ✓ Success/failure status indication
- ✓ Simple and lightweight

## Examples

### Example 1: Basic parity generation
```bash
./run_parity_generator.sh -info "[INFO]_BOS_AXICRYPT.safety.xlsx"
```

### Example 2: Filter specific groups only
```bash
./run_parity_generator.sh -info "simple_test/[INFO]_SIMPLE_TOP.safety.xlsx" \
    -group "GROUP_A"
```

### Example 3: Skip top module generation
```bash
./run_parity_generator.sh -info "[INFO]_BOS_AXICRYPT.safety.xlsx" -gen-top NO
```

### Example 4: Direct Python usage
```bash
python parity_generator.py -info "[INFO]_BOS_AXICRYPT.safety.xlsx"
# You can run parity_generator.py directly without the wrapper script
```

## Output

After successful generation, you will see:
- ✓ INFO file updated with MD5 and Script Version
- Generated parity modules in `simple_test/RTL/SAFETY/` or `axicrypt/RTL/SAFETY/`
- Modified top-level modules with parity instances

## Troubleshooting

### "Python environment not found"
Ensure you have a virtual environment set up:
```bash
# Using venv312
python3.12 -m venv .venv312
source .venv312/bin/activate

# Install dependencies (if needed)
pip install openpyxl pandas
```

### "INFO file not found"
Verify the file path is correct and relative to the parity_generator directory:
- `[INFO]_BOS_AXICRYPT.safety.xlsx` (in root)
- `simple_test/[INFO]_SIMPLE_TOP.safety.xlsx` (in subdirectory)

### Errors during generation
Check the error messages carefully - they usually indicate:
- Missing dependencies
- Invalid INFO file format
- Verilog file reading issues

## Direct Python Usage

You can also run parity_generator.py directly:
```bash
python parity_generator.py -info "[INFO]_BOS_AXICRYPT.safety.xlsx"
```

The runner script provides a convenient wrapper with automatic environment detection and colored output.
