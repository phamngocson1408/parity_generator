# Parity Generator Script - User Guide

## Overview

**Parity Generator** is a Python script that automatically generates parity protection logic for Verilog modules. The script helps with:

- ✅ **Automatic parity bit generation** for data signals
- ✅ **Error detection logic addition** to Verilog modules
- ✅ **Parity comparator module creation** for safety verification
- ✅ **EVEN/ODD parity scheme support**
- ✅ **Fault injection capabilities** for testing

The script reads information from an **Excel INFO file** and automatically generates:
- Modified Verilog modules with parity ports
- Parity generator modules
- Top-level instantiations

---

## Download INFO Template

**Download template file:**
- Download `[INFO]_BOS_IP_TEMPLATE.safety.xlsx` to your `$IP_HOME/DOC/` directory
- Template contains sample configuration for all parameters

**Update parameters:**
- Open the `"SAFETY.PARITY"` sheet in the Excel file
- Update parameters according to your module specifications
- Refer to `INFO_PARAMETERS_MEANING_ENGLISH.md` for detailed parameter information

---

## Navigate to Script Location

```bash
cd /Infra/Tools/SRAP/safety_parity_generator/Latest/
# or
cd /home/pnson/Workspace/Parity_Generator/
```

---

## Load Python Environment

```bash
# With module system (if available)
module load python/3.9.18

# Or activate virtual environment
source .venv39/bin/activate  # Linux/Mac
# or
.venv39\Scripts\activate     # Windows
```

---

## Basic Command

```bash
python3 parity_generator.py -info <INFO_FILE_PATH> [options]
```

**Full command with all arguments explained:**

```bash
python3 parity_generator.py \
  -info [INFO]_IP_NAME.safety.xlsx \
  -group ALL \
  -gen-top YES \
  -output-dir /auto/detect/ \
  [-find]
```

### Arguments Explanation:

#### `-info <INFO_FILE_PATH>` (Required)
- **Purpose**: Specifies the path to the Excel INFO file containing all parity configuration parameters
- **Format**: Excel file (.xlsx) with "SAFETY.PARITY" sheet
- **Example**: `[INFO]_IP_NAME.safety.xlsx`
- **Importance**: This is the only required argument - script cannot run without configuration data

#### `-group <GROUP_NAME>` (Optional)
- **Purpose**: Filters processing to only signals belonging to specified group(s)
- **Default**: `ALL` (process all groups)
- **Format**: Single group name or comma-separated list
- **Examples**: 
  - `-group CRITICAL` (process only CRITICAL group)
  - `-group "GROUP_A,GROUP_B"` (process GROUP_A and GROUP_B)
- **Use Case**: Allows incremental processing of large designs

#### `-gen-top <YES/NO>` (Optional)
- **Purpose**: Controls whether to generate top-level wrapper module with instantiations
- **Default**: `YES` (generate top wrapper)
- **Options**: 
  - `YES`: Generate complete top module with IP and parity instantiations
  - `NO`: Generate only IP and parity modules, skip top wrapper
- **Use Case**: Set to NO for manual integration into existing top modules

#### `-output-dir <PATH>` (Optional)
- **Purpose**: Specifies custom output directory for generated files
- **Default**: Auto-detected from IP FILE LIST paths (usually SAFETY/ folder)
- **Format**: Absolute or relative path
- **Example**: `-output-dir /project/output/safety/`
- **Use Case**: Override default output location for specific project structures

#### `-find` (Optional Flag)
- **Purpose**: Debug mode - only locate and validate IP files without generating parity logic
- **Default**: Not set (normal generation mode)
- **Use Case**: Validate file paths and module names before full generation
- **Output**: Lists found files and modules, reports any missing files

---

## Key Usage Points

### Input
- **Provide Excel INFO file** (`.xlsx`) containing parity configuration via `-info` parameter
- File must contain `"SAFETY.PARITY"` sheet

### Sheet
- Script reads from `"SAFETY.PARITY"` sheet by default
- Sheet contains all configuration parameters

### Row Selection
- **Default**: Process all rows in the sheet
- **Group filtering**: Use `-group <GROUP_NAME>` to process specific groups
- **Multiple groups**: `-group "GROUP_A,GROUP_B"`

### Output
- **Generated parity modules** are automatically saved to `SAFETY/` folder relative to target module location
- **Modified IP modules** with `_NEW.v` suffix
- **Parity generators** with `_PARITY_NEW.v` suffix

### MD5 Tracking
- After generation, **MD5 hash** and **script version** (v3.0.1) are automatically written to the `"MD5 & Script Version"` column in the INFO file
- Used to detect changes and maintain integrity

### Optional Output Directory
- Use `-output-dir <PATH>` to specify custom output location for generated files
- Default: Auto-detect from IP FILE LIST paths

---

## Example Commands

```bash
# Load Python environment
module load python/3.9.18
cd /Infra/Tools/SRAP/safety_parity_generator/Latest/

# Generate parity for all signals (default)
python3 parity_generator.py -info [INFO]_IP_NAME.safety.xlsx

# Generate parity for specific group
python3 parity_generator.py -info [INFO]_IP_NAME.safety.xlsx -group CRITICAL

# Generate parity for multiple groups
python3 parity_generator.py -info [INFO]_IP_NAME.safety.xlsx -group "GROUP_A,GROUP_B"

# Generate with custom output directory
python3 parity_generator.py -info [INFO]_IP_NAME.safety.xlsx -output-dir /custom/path/

# Find IP files without generating (debug mode)
python3 parity_generator.py -info [INFO]_IP_NAME.safety.xlsx -find

# Generate without top wrapper module
python3 parity_generator.py -info [INFO]_IP_NAME.safety.xlsx -gen-top NO
```

---

## System Requirements

### Python Environment
- **Python 3.9+** (recommended)
- **pandas** and **openpyxl** libraries
- **Virtual environment** (recommended)

### Files Required
- **INFO Excel file** (`.xlsx`) containing configuration parameters
- **Verilog source files** (`.v`) of IP requiring parity protection
- **Filelist** (`.f`) containing list of all Verilog files

### Operating System
- **Linux** (primary support)
- **Windows/MacOS** (experimental)

---

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd Parity_Generator
```

### 2. Setup Python Environment
```bash
# Create virtual environment
python3 -m venv .venv39

# Activate environment
source .venv39/bin/activate  # Linux/Mac
# or
.venv39\Scripts\activate     # Windows

# Install dependencies
pip install pandas openpyxl
```

### 3. Verify Installation
```bash
python parity_generator.py --help
```

---

## Directory Structure

```
Parity_Generator/
├── parity_generator.py          # Main script
├── INFO_PARAMETERS_*.md         # Documentation files
├── USER_GUIDE.md               # User guide
├── Parity_generator/           # Core modules
│   ├── extract_info_classes.py # INFO file parsing
│   ├── generate_bus_parity.py  # Parity logic generation
│   ├── module_parser_utilities.py
│   └── ...
├── axicrypt/                   # Example IP
│   └── RTL/
│       ├── IP_NAME.v
│       └── filelist.f
└── simple_test/               # Test cases
```

---

## Usage

### Basic Syntax

```bash
python3 parity_generator.py -info <INFO_FILE_PATH> [options]
```

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `-info` | **Path to INFO Excel file** - Excel file containing all parity configuration parameters | `[INFO]_IP_NAME.safety.xlsx` |

### Optional Parameters

| Option | Default | Description |
|--------|---------|-------------|
| `-group` | `ALL` | **Group filter** - Process only signals belonging to specified group(s). Use comma-separated values for multiple groups | `GROUP_A,GROUP_B` |
| `-gen-top` | `YES` | **Generate top wrapper** - Whether to generate top-level wrapper module with instantiations | `NO` |
| `-find` | N/A | **Find mode** - Only locate and validate IP files without generating parity logic (debug mode) | (flag only) |
| `-output-dir` | Auto | **Custom output directory** - Specify custom path for generated files instead of auto-detected SAFETY/ folder | `/custom/path/` |

### Sheet Information
- **Default Sheet**: `"SAFETY.PARITY"`
- **Row Processing**: Process all rows or filter by GROUP
- **MD5 Tracking**: Auto-update MD5 hash and script version (v3.0.1) after generation

---

## INFO Excel File Format

### Required Columns (Required Columns)

| Column | Description | Example |
|--------|-------------|---------|
| IP NAME | **Verilog module name** - Exact name of the module to generate parity for | `IP_NAME` |
| SIGNAL PORT NAME | **Data port to protect** - Name of the data signal requiring parity protection | `AXICRYPT_AXI_MI0_WDATA` |
| BIT WIDTH | **Data width in bits** - Width of the data signal (must match Verilog declaration) | `256` |
| PARITY SOURCE BIT WIDTH | **Parity bits width** - Number of parity bits needed (must divide evenly into BIT WIDTH) | `8` |
| DRIVE/RECEIVE | **Data direction** - Whether module drives ("DRIVE") or receives ("RECEIVE") the data | `DRIVE` or `RECEIVE` |
| EVEN ODD | **Parity scheme** - Type of parity to use ("EVEN" or "ODD") | `EVEN` |
| CLOCK | **Clock signal name** - Name of the clock signal for synchronization | `ACLK` |
| RESET | **Reset signal name** - Name of the reset signal for initialization | `RESETN_ACLK` |
| SIGNAL VALID NAME | **Valid handshake signal** - Signal indicating when data is valid | `AXICRYPT_AXI_MI0_WVALID` |
| PARITY PORT NAME | **Parity input port name** - Name of the port where parity bits will be received | `AXICRYPT_AXI_MI0_WDATA_PARITY` |
| IP FILE LIST | **Path to .f filelist** - Path to filelist containing all Verilog source files | `$AXICRYPT_HOME/RTL/filelist.f` |

### Optional Columns (Optional Columns)

| Column | Default | Description |
|--------|---------|-------------|
| GROUP | `""` | **Group identifier** - Label to group signals for batch processing | `GROUP_A` |
| ERROR PORT | `""` | **Error output port name** - Port for immediate error reporting | `ERR_PARITY` |
| ERROR DOUBLE | `"YES"` | **Double-bit error detection** - Whether to detect 2-bit errors (Hamming code) | `"NO"` |
| COMPARATOR INPUT WIDTH | `32` | **Comparator input width** - Input width for comparison circuit | `64` |
| COMPARATOR DEPTH | `0` | **Pipeline depth** - Number of pipeline stages for timing optimization | `1` |
| VERSION | `""` | **Design version** - Version identifier for design tracking | `1.0` |
| HSR ID | `""` | **Safety record ID** - Unique identifier for safety documentation | `HSR-001` |
| SM ID | `""` | **Safety module ID** - Identifier within safety module hierarchy | `SM-001` |
| NOTE | `""` | **Custom notes** - Free-form field for additional information | `Critical signal` |

---

## Usage Examples

### 1. Basic Usage - Generate All Parity (Default Settings)

```bash
python3 parity_generator.py -info [INFO]_IP_NAME.safety.xlsx
```

**What it does:**
- Processes all signals in the INFO file
- Generates top wrapper module
- Uses auto-detected output directory
- Includes all groups

### 2. Generate Specific Group Only

```bash
python3 parity_generator.py \
  -info [INFO]_IP_NAME.safety.xlsx \
  -group CRITICAL
```

**What it does:**
- Only processes signals with GROUP = "CRITICAL"
- Generates top wrapper
- Useful for incremental development

### 3. Generate Multiple Groups

```bash
python3 parity_generator.py \
  -info [INFO]_IP_NAME.safety.xlsx \
  -group "GROUP_A,GROUP_B"
```

**What it does:**
- Processes signals from GROUP_A and GROUP_B
- Comma-separated list for multiple groups

### 4. Generate with Custom Output Directory

```bash
python3 parity_generator.py \
  -info [INFO]_IP_NAME.safety.xlsx \
  -output-dir /custom/safety/output/
```

**What it does:**
- Overrides default output location
- Places all generated files in specified directory

### 5. Find IP Files Without Generating (Debug Mode)

```bash
python3 parity_generator.py \
  -info [INFO]_IP_NAME.safety.xlsx \
  -find
```

**What it does:**
- Only validates file paths and module names
- Reports missing files or modules
- No files are generated

### 6. Generate Without Top Wrapper Module

```bash
python3 parity_generator.py \
  -info [INFO]_IP_NAME.safety.xlsx \
  -gen-top NO
```

**What it does:**
- Generates IP modules and parity modules
- Skips top-level wrapper generation
- Useful for manual integration

### 7. Full Command with All Options

```bash
python3 parity_generator.py \
  -info [INFO]_IP_NAME.safety.xlsx \
  -group "CRITICAL,SAFETY" \
  -gen-top YES \
  -output-dir /project/safety_generated/
```

**What it does:**
- Processes CRITICAL and SAFETY groups
- Generates top wrapper
- Uses custom output directory

---

## Output Files Generated

### 1. Modified IP Module
- **Input**: `IP_NAME.v`
- **Output**: `IP_NAME_NEW.v`
- **Changes**:
  - Added parity input ports
  - Added error output ports (if specified)
  - Added fault injection ports (if applicable)

### 2. Parity Generator Module
- **Output**: `IP_NAME_PARITY_NEW.v`
- **Contents**:
  - Parity calculation logic
  - Error detection comparators
  - Synchronization registers

### 3. Top Wrapper Module (Optional)
- **Output**: `IP_NAME_NEW.v` (when `-gen-top YES`)
- **Contents**:
  - Instantiation of modified IP module
  - Instantiation of parity generator
  - Port connections

### 4. Backup Files
- **Original files** are backed up with `_ORIGINAL` suffix

---

## Parity Types Supported

Script generates **SAFETY.PARITY** protection by default for all signals in the INFO file:

- **Standard parity protection** for safety-critical signals
- Support for both DRIVE and RECEIVE modes
- Error detection and fault injection
- EVEN/ODD parity schemes

---

## Error Detection and Fault Injection

### Error Detection Modes

#### DRIVE Mode (Sender Protection)
- Module **generates parity** for output data
- Detects errors from **internal logic**
- Single-bit error detection

#### RECEIVE Mode (Receiver Protection)
- Module **checks parity** of input data
- Detects errors from **communication channel**
- Fault injection support

### Fault Injection (FI)
- **FIERR ports** for fault injection testing
- Only applies to **RECEIVE signals**
- Controlled by external test signals

---

## Troubleshooting

### Common Errors

#### 1. "Module not found" Error
```
Error: Cannot find module 'IP_NAME' in filelist
```
**Solution**:
- Check IP NAME spelling in INFO file
- Verify filelist (.f) contains correct paths
- Ensure environment variables are set

#### 2. "Port not found" Error
```
Error: Port 'AXICRYPT_AXI_MI0_WDATA' not found in module
```
**Solution**:
- Verify SIGNAL PORT NAME matches exactly in Verilog
- Check BIT WIDTH matches port declaration
- Ensure filelist includes all source files

#### 3. "KeyError: 'PARITY PORT NAME'" Error
```
KeyError: 'PARITY PORT NAME'
```
**Solution**:
- PARITY PORT NAME column is required
- Cannot be empty for any signal
- Must specify unique port name

#### 4. "BIT WIDTH not multiple of PARITY SOURCE BIT WIDTH" Error
```
AssertionError: BIT WIDTH should be in multiples of PARITY BIT WIDTH
```
**Solution**:
- BIT WIDTH must be divisible by PARITY SOURCE BIT WIDTH
- Adjust PARITY SOURCE BIT WIDTH value

### Debug Mode

#### Enable Verbose Output
```bash
python parity_generator.py -info <file> -v
```

#### Check INFO File Parsing
```bash
python parity_generator.py -info <file> -find
```

### Environment Variables

#### Required Variables
```bash
export AXICRYPT_HOME=/path/to/axicrypt
export PROJECT_HOME=/path/to/project
```

#### Filelist Format
```
${IP_HOME}/RTL/IP_NAME.v
${IP_HOME}/RTL/AES/IP_AES.v
+incdir+${IP_HOME}/RTL/
```

---

## Best Practices

### 1. INFO File Management
- ✅ **Validate INFO file** before running script
- ✅ **Backup original** Excel file
- ✅ **Use consistent naming** conventions
- ✅ **Document custom notes** in NOTE column

### 2. File Organization
- ✅ **Use environment variables** in filelist
- ✅ **Keep filelists updated** with source changes
- ✅ **Version control** all generated files

### 3. Safety Considerations
- ✅ **Test parity logic** thoroughly
- ✅ **Verify error detection** with fault injection
- ✅ **Document safety requirements** in HSR ID/SM ID

### 4. Performance Optimization
- ✅ **Use appropriate COMPARATOR DEPTH** for timing
- ✅ **Group related signals** with GROUP parameter
- ✅ **Minimize parity overhead** with optimal bit widths

---

## Advanced Features

### Group-based Processing
```bash
# Process only critical signals first
python parity_generator.py -info <file> -group CRITICAL

# Then process remaining signals
python parity_generator.py -info <file> -group NON_CRITICAL
```

### Custom Error Reporting
```bash
# Enable error ports for critical signals
# Set ERROR PORT column in INFO file
# Script will auto-generate error output ports
```

### Integration with Existing Design
```bash
# Generate without top wrapper for manual integration
python parity_generator.py -info <file> -gen-top NO

# Then manually instantiate in your top module
```

---

## Integration Guide for Generated Parity Modules

This section provides step-by-step instructions for integrating the generated parity protection modules into your design.

---

## Output Location

### Generated Files Location
- **Parity modules** are automatically saved to the `SAFETY/` folder relative to the target module's directory
- **Default path**: `<IP_FILELIST_DIR>/SAFETY/` (inside the RTL directory)

### Output Filename Formats
- **Modified IP Module**: `<MODULE_NAME>_NEW.v` (top wrapper if `-gen-top YES`)
- **Parity Generator Module**: `<MODULE_NAME>_PARITY_NEW.v`
- **Top Wrapper Module**: `<MODULE_NAME>_NEW.v` (same as above when `-gen-top YES`)

**Note**: The Verilog module name inside the parity generator file is `<MODULE_NAME>_IP_PARITY_GEN`, but the file is saved as `<MODULE_NAME>_PARITY_NEW.v`.

### Example Output Structure
```
project/
├── RTL/
│   ├── IP_NAME.v
│   ├── filelist.f
│   └── SAFETY/                    # Generated files location
│       ├── IP_NAME_NEW.v     # Top wrapper (if -gen-top YES) or Modified IP
│       └── IP_NAME_PARITY_NEW.v  # Parity generator
```

---

## Integration Process

### Step 1: Rename Generated Files

**Remove the `_NEW` suffix** from generated files to match your naming convention:

```bash
# Navigate to SAFETY directory
cd <IP_FILELIST_DIR>/../SAFETY/

# Rename files (remove _NEW suffix)
# When -gen-top YES: IP_NAME_NEW.v is the top wrapper
mv IP_NAME_NEW.v IP_NAME_TOP_PARITY.v
mv IP_NAME_PARITY_NEW.v IP_NAME_PARITY.v

# When -gen-top NO: only parity generator is created
# mv IP_NAME_PARITY_NEW.v IP_NAME_PARITY.v
```

**Result:**
- `IP_NAME_NEW.v` → `IP_NAME_TOP_PARITY.v` (top wrapper)
- `IP_NAME_PARITY_NEW.v` → `IP_NAME_PARITY.v` (parity generator)

### Step 2: Update Filelist

**Add the parity modules** to your design filelist (e.g., `filelist_sim.f` or `filelist.f`):

```bash
# Example filelist entries
# Original IP
${IP_HOME}/RTL/IP_NAME.v

# Generated parity protection files
${IP_HOME}/SAFETY/IP_NAME_TOP_PARITY.v  # Top wrapper (renamed from IP_NAME_NEW.v)
${IP_HOME}/SAFETY/IP_NAME_PARITY.v      # Parity generator (renamed from IP_NAME_PARITY_NEW.v)
```

**Filelist Format:**
```
# Original design files
${IP_HOME}/RTL/IP_NAME.v
${IP_HOME}/RTL/AES/IP_AES.v

# Generated parity protection files
${IP_HOME}/SAFETY/IP_NAME_PARITY_NEW.v
${IP_HOME}/SAFETY/IP_NAME_PARITY.v

# Include directories
+incdir+${AXICRYPT_HOME}/RTL/
```

### Step 3: Instantiate in Top Module

**Manually instantiate** the parity modules in your top-level wrapper module.

#### Option A: Use Generated Top Wrapper (Recommended)
If you used `-gen-top YES`, the script generates a complete top wrapper:

```verilog
// Generated top wrapper (renamed from IP_NAME_NEW.v)
module IP_NAME_TOP_PARITY (
    // All original ports plus parity ports
    input         ACLK,
    input         RESETN_ACLK,
    // ... original ports ...
    // Parity input ports
    input  [7:0]  AXICRYPT_AXI_MI0_WDATA_PARITY,
    // Error output ports (if configured)
    output        ERR_AXICRYPT_AXI_MI0_BUS_PARITY
);

// Instantiate modified IP with parity ports
IP_NAME_PARITY u_ip_name (
    .ACLK(ACLK),
    .RESETN_ACLK(RESETN_ACLK),
    // ... connect all original ports ...
    .IP_AXI_MI0_WDATA_PARITY(IP_AXI_MI0_WDATA_PARITY),
    .ERR_IP_AXI_MI0_BUS_PARITY(ERR_IP_AXI_MI0_BUS_PARITY)
);

// Instantiate parity generator
IP_NAME_IP_PARITY_GEN u_ip_name_ip_parity_gen (
    .I_CLK(ACLK),
    .I_RESETN(RESETN_ACLK),
    // ... connect data and parity signals ...
    .IP_AXI_MI0_WDATA(IP_AXI_MI0_WDATA),
    .IP_AXI_MI0_WVALID(IP_AXI_MI0_WVALID),
    .IP_AXI_MI0_WDATA_PARITY(IP_AXI_MI0_WDATA_PARITY),
    .ERR_DCLS(ERR_IP_AXI_MI0_BUS_PARITY)
);

endmodule
```

#### Option B: Manual Integration (Advanced)
If you used `-gen-top NO`, manually integrate into your existing top module:

```verilog
module IP_NAME_TOP (
    // Original ports
    input         ACLK,
    input         RESETN_ACLK,
    // ... your original ports ...

    // Add parity input ports
    input  [7:0]  IP_AXI_MI0_WDATA_PARITY,

    // Add error output ports (if configured)
    output        ERR_IP_AXI_MI0_BUS_PARITY
);

// Instantiate your original IP (now with parity ports added)
IP_NAME_PARITY u_ip_name (
    .ACLK(ACLK),
    .RESETN_ACLK(RESETN_ACLK),
    // ... connect all your original signals ...
    .IP_AXI_MI0_WDATA(IP_AXI_MI0_WDATA),
    .AXICRYPT_AXI_MI0_WVALID(AXICRYPT_AXI_MI0_WVALID),
    .AXICRYPT_AXI_MI0_WDATA_PARITY(AXICRYPT_AXI_MI0_WDATA_PARITY),
    .ERR_AXICRYPT_AXI_MI0_BUS_PARITY(ERR_AXICRYPT_AXI_MI0_BUS_PARITY)
);

// Instantiate parity generator
IP_NAME_IP_PARITY_GEN u_ip_name_ip_parity_gen (
    .I_CLK(ACLK),
    .I_RESETN(RESETN_ACLK),
    .IP_AXI_MI0_WDATA(IP_AXI_MI0_WDATA),
    .IP_AXI_MI0_WVALID(IP_AXI_MI0_WVALID),
    .IP_AXI_MI0_WDATA_PARITY(IP_AXI_MI0_WDATA_PARITY),
    .ERR_DCLS(ERR_IP_AXI_MI0_BUS_PARITY)
);

endmodule
```

### Step 4: Connect External Signals

**Connect parity and error signals** to external modules:

```verilog
// In your system top level
module SYSTEM_TOP (
    // ... other signals ...
    input  [7:0]  wdata_parity_from_external,
    output        parity_error_to_monitor
);

// Instantiate your parity-protected module
IP_NAME_TOP u_ip_name (
    .ACLK(ACLK),
    .RESETN_ACLK(RESETN_ACLK),
    // ... other connections ...
    .IP_AXI_MI0_WDATA_PARITY(wdata_parity_from_external),
    .ERR_IP_AXI_MI0_BUS_PARITY(parity_error_to_monitor)
);

endmodule
```

### Step 5: Update Testbenches

**Update your testbenches** to handle new parity ports:

```verilog
// In testbench
module TB_IP_NAME;

// ... existing testbench code ...

// Add parity signal generation
reg [7:0] tb_wdata_parity;
wire      tb_parity_error;

// Generate EVEN parity for WDATA (example)
always @(*) begin
    tb_wdata_parity = ^tb_wdata;  // XOR reduction for even parity
end

// Instantiate DUT with parity
IP_NAME_TOP DUT (
    .ACLK(tb_aclk),
    .RESETN_ACLK(tb_resetn),
    // ... other connections ...
    .IP_AXI_MI0_WDATA(tb_wdata),
    .IP_AXI_MI0_WVALID(tb_wvalid),
    .IP_AXI_MI0_WDATA_PARITY(tb_wdata_parity),
    .ERR_IP_AXI_MI0_BUS_PARITY(tb_parity_error)
);

// Monitor parity errors
always @(posedge tb_aclk) begin
    if (tb_parity_error) begin
        $display("PARITY ERROR detected at time %t", $time);
        // Handle error (log, flag, etc.)
    end
end

endmodule
```

---

## Integration Checklist

### Pre-Integration
- ✅ **Verify generated files** exist in SAFETY/ directory
- ✅ **Check file permissions** and readability
- ✅ **Validate port connections** match your interface
- ✅ **Review error handling** requirements

### Filelist Updates
- ✅ **Add parity generator** to filelist
- ✅ **Add modified IP** to filelist
- ✅ **Update include paths** if needed
- ✅ **Test filelist compilation**

### Top Module Integration
- ✅ **Add parity input ports** to top module interface
- ✅ **Add error output ports** to top module interface
- ✅ **Connect all signals** between IP and parity generator
- ✅ **Verify clock/reset connections**

### System Integration
- ✅ **Connect external parity sources** to parity inputs
- ✅ **Connect error outputs** to monitoring systems
- ✅ **Update system documentation**

### Testing
- ✅ **Update testbenches** for new ports
- ✅ **Add parity error checking** in tests
- ✅ **Verify fault injection** (if used)
- ✅ **Run regression tests**

---

## Common Integration Issues

### Issue 1: Port Mismatch
**Symptom:** Compilation errors about undefined ports
**Solution:** Ensure all ports in generated modules match your top-level interface

### Issue 2: Filelist Path Errors
**Symptom:** "Cannot find file" during compilation
**Solution:** Verify SAFETY/ directory paths in filelist are correct

### Issue 3: Signal Connection Errors
**Symptom:** "Unconnected port" warnings
**Solution:** Check all required ports are connected in instantiation

### Issue 4: Timing Issues
**Symptom:** Parity errors in simulation when none expected
**Solution:** Verify parity generation logic and signal timing

---

## Best Practices for Integration

### 1. **Version Control**
- ✅ Commit generated files to version control
- ✅ Tag releases with parity protection versions
- ✅ Document integration changes

### 2. **Documentation**
- ✅ Update design documents with parity protection
- ✅ Document error handling procedures
- ✅ Maintain integration checklists

### 3. **Testing Strategy**
- ✅ Test parity error detection thoroughly
- ✅ Include fault injection testing
- ✅ Monitor error rates in production

### 4. **Maintenance**
- ✅ Keep track of which signals have parity protection
- ✅ Plan for future parity additions
- ✅ Regular audits of parity effectiveness

---

**Integration completed successfully when:**
- ✅ Design compiles without errors
- ✅ All parity ports are properly connected
- ✅ Error detection works as expected
- ✅ Testbenches pass with parity protection

---

## Changelog

### Version 3.0.2 (February 9, 2026)
- ✅ Simplified command syntax (removed -type parameter)
- ✅ Added custom output directory support (-output-dir)
- ✅ Enhanced MD5 tracking with script version
- ✅ Improved documentation with step-by-step workflow
- ✅ Translated to English with detailed argument explanations

### Version 3.0.1 (February 9, 2026)
- ✅ Added default values documentation
- ✅ Enhanced error messages
- ✅ Improved fault injection support

### Version 3.0.0 (Previous)
- ✅ Initial release
- ✅ Basic parity generation
- ✅ Excel INFO file support

---

**Last Updated:** February 9, 2026
**Version:** 3.0.2
**Language:** English</content>
<parameter name="filePath">/home/pnson/Workspace/Parity_Generator/PARITY_GENERATOR_USAGE.md