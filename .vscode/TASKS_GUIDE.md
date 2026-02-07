# VS Code Tasks Guide - Parity Generator

## Available Tasks

This workspace includes several pre-configured tasks for generating parity modules.

### Tasks List:

1. **Generate Parity: BOS_AXICRYPT (SAFETY.PARITY)** - Default task
   - Generates SAFETY.PARITY modules for BOS_AXICRYPT from INFO file
   - **Shortcut:** `F5` or `Ctrl+Shift+B`

2. **Generate Parity: SIMPLE_TOP (SAFETY.PARITY)**
   - Generates SAFETY.PARITY modules for SIMPLE_TOP
   - **Access:** Ctrl+Shift+B → Select this task

3. **Generate Parity: BOS_AXICRYPT (SIGNAL PARITY)**
   - Generates SAFETY.SIGNAL PARITY modules
   - **Access:** Ctrl+Shift+B → Select this task

4. **Generate Parity: BOS_AXICRYPT (REGISTER PARITY)**
   - Generates SAFETY.REGISTER PARITY modules
   - **Access:** Ctrl+Shift+B → Select this task

## How to Run

### Method 1: Press F5
- Press `F5` key to run the default task (BOS_AXICRYPT SAFETY.PARITY)

### Method 2: Use Task Menu
- Press `Ctrl+Shift+B` (Run Build Task)
- A menu will appear with all available tasks
- Select the desired task

### Method 3: Use Command Palette
- Press `Ctrl+Shift+P` to open Command Palette
- Search for "Tasks: Run Task"
- Select the desired parity generation task

## Output

Generated files will be placed in:
- `axicrypt/RTL/SAFETY/` - for SAFETY.PARITY modules
- `DCLS_generator/module_parity/` - for SIGNAL/REGISTER parity modules

All generated modules will include MD5 hash and Script Version headers:
```verilog
// MD5@INFO : {hash_value}
// Version@Script : 3.0.0
module {module_name} (
```

## Modifying Tasks

To run different INFO files or parity types:
1. Edit `.vscode/tasks.json`
2. Modify the `args` section with desired parameters
3. Save and re-run the task

### Available Parameters:
- `-info [FILE]` - INFO file path
- `-type [TYPE]` - Parity scheme type:
  - `SAFETY.PARITY` - Bus parity
  - `SAFETY.SIGNAL PARITY` - Signal parity
  - `SAFETY.REGISTER PARITY` - Register parity
- `-group [GROUPS]` - GROUP filter (comma-separated or 'ALL')
- `-gen-top [YES|NO]` - Generate top wrapper module
