# VS Code Debug/Run Configuration Fix

## Issues Fixed

### Problem
- **Ctrl+F5** (Run Without Debugging) was failing
- **Reason:** launch.json was using `debugpy` type but debugpy was not installed in `.venv312`

### Solution Implemented

1. **Updated `launch.json`**
   - Changed debug type from `debugpy` to `python` (built-in Python runner)
   - No additional dependencies needed
   - Proper Python path: `.venv312/bin/python3`
   - Added 2 debug configurations:
     - Generate Parity: BOS_AXICRYPT (SAFETY.PARITY)
     - Generate Parity: SIMPLE_TOP (SAFETY.PARITY)

2. **Updated `keybindings.json`**
   - **F5** → Runs task (fast execution)
   - **Ctrl+F5** → Runs debug configuration (with Python REPL support)

## How to Use

### Run with F5
```
Press F5 → Runs task "Generate Parity: BOS_AXICRYPT (SAFETY.PARITY)"
```
✓ Fast execution
✓ No debugging overhead
✓ stdout/stderr in terminal

### Debug with Ctrl+F5
```
Press Ctrl+F5 → Runs debug configuration without debugging
```
✓ Can set breakpoints if needed
✓ Can inspect variables
✓ Full Python debugging features available

### Manual Debug (F5 with Debugging)
- Press F5 if you want to attach debugger
- Can set breakpoints
- Can step through code

## Configuration Details

**Python Path:** `.venv312/bin/python3`

**Default Arguments (BOS_AXICRYPT):**
```
-info [INFO]_BOS_AXICRYPT.safety.xlsx
-type SAFETY.PARITY
-group ALL
```

**Available Configurations:**
1. Generate Parity: BOS_AXICRYPT (SAFETY.PARITY) - **Primary**
2. Generate Parity: SIMPLE_TOP (SAFETY.PARITY) - Switch in VS Code

## To Switch Configuration

1. Press **F1** → Search "Debug: Select and Start Debugging"
2. Choose desired configuration
3. Press **F5** or **Ctrl+F5**

Or manually select from the Debug menu on the left sidebar.

---

**Both F5 and Ctrl+F5 should now work without errors!** ✓
