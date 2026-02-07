# Parity Generator - Quick Reference

## Fastest way to run parity generation

### Bash Script (Linux/macOS)
```bash
./run_parity_generator.sh -info "[INFO]_BOS_AXICRYPT.safety.xlsx"
```

### Direct Python (Always works)
```bash
python parity_generator.py -info "[INFO]_BOS_AXICRYPT.safety.xlsx"
```

---

## Common Use Cases

**Generate parity for simple_test:**
```bash
./run_parity_generator.sh -info "simple_test/[INFO]_SIMPLE_TOP.safety.xlsx"
```

**Generate parity for specific groups only:**
```bash
./run_parity_generator.sh -info "[INFO]_BOS_AXICRYPT.safety.xlsx" -group "GROUP_A,GROUP_B"
```

**Custom instance name:**
```bash
./run_parity_generator.sh -info "[INFO]_BOS_AXICRYPT.safety.xlsx" -inst MY_PARITY_INST
```

**Skip top module generation:**
```bash
./run_parity_generator.sh -info "[INFO]_BOS_AXICRYPT.safety.xlsx" -gen-top NO
```

---

## All Options

```
-info <path>      : Path to INFO Excel file (REQUIRED)
-inst <name>      : Parity instance name (default: BOS_BUS_PARITY_AXI_M)
-type <type>      : Parity scheme type (default: SAFETY.PARITY)
-group <names>    : Groups to process: "GROUP_A,GROUP_B" or "ALL" (default: ALL)
-gen-top <yes|no> : Generate top wrapper (default: YES)
-h                : Show help
```

---

## Generated Files

After running, you'll find generated files in:
- `simple_test/RTL/SAFETY/` - For simple_test module
- `axicrypt/RTL/SAFETY/` - For axicrypt module

New files created:
- `SIMPLE_TOP_NEW.v` - Modified top module with parity
- `SIMPLE_TOP_PARITY_NEW.v` - Generated parity module

---

## Help & Examples

**Show full help:**
```bash
./run_parity_generator.sh -h
python run_parity_generator.py -h
```

**See detailed documentation:**
```
cat SCRIPT_README.md
```
