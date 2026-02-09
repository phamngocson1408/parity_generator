# INFO Sheet - Parameters Detailed Meaning (English)

## Detailed Explanation of Each Parameter's Meaning

---

## 1. No
**Meaning:** Sequential row number / index
- This is the **row number** in the table
- Auto-increments from 1, 2, 3, ...
- Used to **reference and locate** which row needs modification
- Does not affect processing, just for reference only

**Default Value:** Auto-generated (1, 2, 3, ...)

---

## 2. VERSION
**Meaning:** Version identifier of the design or configuration
- Tracks the **design version** (e.g., 1.0, 2.1, 3.0)
- Helps **maintain design history** and evolution
- When major changes occur, increment version to track what changed
- **Not mandatory** - typically left empty or filled with project version

**Default Value:** Empty string ("")

---

## 3. HSR ID
**Meaning:** Hardware Safety Record ID - unique identifier for safety documentation
- **HSR (Hardware Safety Record)** is official safety documentation
- This ID is a **unique code** to reference in official safety documents
- Example: `HSR-001`, `BOS-AXI-001` - used to **track compliance** with safety standards
- Important for **safety audits** - ensures design meets safety requirements
- **Not mandatory** - only needed when safety certification is required

**Default Value:** Empty string ("")

---

## 4. SM ID
**Meaning:** Safety Module ID - identifier within safety module hierarchy
- **SM (Safety Module)** is a functional block in the safety architecture
- This ID is used to **classify modules** in the safety hierarchy
- Example: `SM-001`, `MOD-AXI-001` - helps organize safety modules by level
- When multiple safety modules exist, use SM ID to **group them together**
- **Not mandatory** - only used when managing multiple safety modules

**Default Value:** Empty string ("")

---

## 5. IP NAME ⭐ (REQUIRED)
**Meaning:** Module/IP name for parity generation
- **IP NAME is the Verilog module name to generate parity for**
- Example: `BOS_AXICRYPT` - this is the module name in Verilog file
- **Must match exactly** with module name in code: `module BOS_AXICRYPT (...)`
- If misspelled, script cannot find the module to generate parity
- Script searches for the file containing this module name via filelist

**Default Value:** N/A (Required - no default)

---

## 6. CLOCK ⭐ (REQUIRED)
**Meaning:** Clock signal name used by the IP
- **CLOCK is the main clock signal** of the system
- Example: `ACLK`, `CLK`, `sys_clk` - port name of clock in module
- Used to **synchronize parity generation logic** with main clock
- When data changes, parity must be calculated **on this clock signal**
- Must be an **input port** of the module and **must exist** in Verilog

**Default Value:** N/A (Required - no default)

---

## 7. RESET ⭐ (REQUIRED)
**Meaning:** Reset signal name used by the IP
- **RESET is the initialization signal** of the system
- Example: `RESETN_ACLK`, `RST_N`, `async_resetn` - port name of reset in module
- When reset is asserted, all parity logic is **initialized to default state**
- Can be **active-high** (`RESET`) or **active-low** (`RESETN`)
- Must be an **input port** of the module

**Default Value:** N/A (Required - no default)

---

## 8. SIGNAL PORT NAME ⭐ (REQUIRED)
**Meaning:** Data port/signal to be protected with parity
- **SIGNAL PORT NAME is the data port that needs parity protection**
- Example: `AXICRYPT_AXI_MI0_WDATA` - 256-bit AXI write data port
- This is the **critical port requiring error detection**
- Each row in INFO file represents **a different signal** needing parity
- Must match **exact port name** in Verilog module

**Default Value:** N/A (Required - no default)

---

## 9. GROUP
**Meaning:** Grouping identifier for batch filtering
- **GROUP is a label to group signals** of the **same type or tier**
- Example: `GROUP_A` - all signals in this group can be processed together
- Used when **running script with** `-group GROUP_A` option to **process only that group**
- Helps **divide workload** when there are many signals (process one group at a time)
- **Not mandatory** - if not used, use `-group ALL` option

**Default Value:** Empty string ("") - treated as no group

---

## 10. DRIVE/RECEIVE ⭐ (REQUIRED)
**Meaning:** Direction of data flow - who is driving the signal
- **DRIVE/RECEIVE specifies the data direction:**
  - **DRIVE** = this module **outputs the data** (output) → errors originate from this module
  - **RECEIVE** = this module **receives the data** (input) → errors come from outside
- Example:
  - `AXICRYPT_AXI_MI0_WDATA` = DRIVE (module sends data)
  - `AXICRYPT_AXI_SI0_WDATA` = RECEIVE (module receives data)
- **Determines error type:**
  - DRIVE → detects errors from sender - **single-bit error detection**
  - RECEIVE → detects transmission errors - **communication error detection**

**Default Value:** N/A (Required - no default)

---

## 11. SIGNAL VALID NAME ⭐ (REQUIRED)
**Meaning:** Handshake signal indicating when data is valid
- **SIGNAL VALID NAME is the signal indicating data validity**
- Example: `AXICRYPT_AXI_MI0_WVALID` - when this signal is 1, WDATA is valid
- In **AXI protocol**, there is a **handshake rule:**
  - Master sends data + `*VALID` = 1
  - Slave ready + `*READY` = 1
  - When both = 1, **data is transferred**
- Parity module will **capture parity at the same cycle as VALID**
- **Must exist** in module Verilog

**Default Value:** N/A (Required - no default)

---

## 12. PARITY PORT NAME ⭐ (REQUIRED)
**Meaning:** Name of parity input port (for receiving parity bits)
- **PARITY PORT NAME is the port where parity bits will be received**
- Example: `AXICRYPT_AXI_MI0_WDATA_PARITY` - this port receives parity bits of WDATA
- This is a **new INPUT port added to the module**
- Script will:
  1. **Create this port** in module with width = `PARITY SOURCE BIT WIDTH`
  2. **Connect** to external signal (or from parity generator module)
- **Naming convention:** `{SIGNAL_NAME}_PARITY`

**Default Value:** N/A (Required - no default)

---

## 13. IP FILE LIST ⭐ (REQUIRED)
**Meaning:** Filelist path containing all Verilog source files of the IP
- **IP FILE LIST is the path to the `.f` file listing all Verilog files**
- Example: `$AXICRYPT_HOME/RTL/filelist.f` - this file lists each Verilog file
- **Filelist in `.f` format** typically has structure:
  ```
  ${AXICRYPT_HOME}/RTL/BOS_AXICRYPT.v
  ${AXICRYPT_HOME}/RTL/AES/AXICRYPT_AES.v
  ${AXICRYPT_HOME}/RTL/COMMON/ATU.v
  +incdir+${AXICRYPT_HOME}/RTL/
  ```
- Script **reads this filelist** to find all files, then **locates the module containing IP NAME**
- **Supports environment variables** like `${AXICRYPT_HOME}` or `$AXICRYPT_HOME`

**Default Value:** N/A (Required - no default)

---

## 14. ERROR PORT
**Meaning:** Output port name for error detection signal
- **ERROR PORT is the OUTPUT port that signals parity error detection**
- Example: `ERR_AXICRYPT_AXI_MI0_BUS_PARITY` - when this port = 1, parity error detected
- **Only used for critical signals** (critical buses) that need immediate error notification
- Leave empty if error reporting not needed (only logging)
- Script will **create this output port** in module to report errors

**Default Value:** Empty string ("") - no error port created

---

## 15. ERROR DOUBLE
**Meaning:** Flag for double-bit error detection capability
- **ERROR DOUBLE indicates whether** **2-bit error detection** is supported
- Values:
  - **YES** = parity module can detect **2-bit errors** (requires Hamming code)
  - **NO** = only detects **1-bit errors** (simple parity)
- **Typically set to NO** for most applications (simple parity sufficient)
- **Set to YES** only when `ERROR PORT` exists for 2-bit error reporting

**Default Value:** "YES" (when ERROR PORT is empty) or "NO" (when ERROR PORT exists)

---

## 16. BIT WIDTH ⭐ (REQUIRED)
**Meaning:** Width of the data signal in bits
- **BIT WIDTH is the width** (number of bits) **of data requiring protection**
- Example:
  - `AXICRYPT_AXI_MI0_ARADDR` = 36 bits (address)
  - `AXICRYPT_AXI_MI0_WDATA` = 256 bits (data)
- Must **match exactly** with port width in Verilog
- Used to **calculate number of parity bits** needed

**Default Value:** N/A (Required - no default)

---

## 17. PARITY SOURCE BIT WIDTH ⭐ (REQUIRED)
**Meaning:** Width of parity bits (number of parity bits needed)
- **PARITY SOURCE BIT WIDTH is the number of parity bits needed to protect data**
- **Formula:** `ceil(log2(BIT_WIDTH))` for single parity
- Example:
  - BIT WIDTH = 36 → Parity width = 6 bits (2^6 = 64 > 36)
  - BIT WIDTH = 256 → Parity width = 8 bits (2^8 = 256)
  - But in practice with Hamming code → width may be larger
- Script uses this to **create INPUT port with this width**

**Default Value:** N/A (Required - no default)

---

## 18. EVEN ODD ⭐ (REQUIRED)
**Meaning:** Parity scheme - EVEN or ODD parity
- **EVEN ODD specifies the parity type to use:**
  - **EVEN** = number of 1 bits in data + parity bit = EVEN number
  - **ODD** = number of 1 bits in data + parity bit = ODD number
- Example:
  - Data: `1011` (3 bits are 1)
  - EVEN parity: add 1 → `10111` (4 ones = even)
  - ODD parity: add 0 → `10110` (3 ones = odd)
- **EVEN parity is more common** in safety (easier for error detection)
- Script uses this to **generate parity comparison logic**

**Default Value:** N/A (Required - no default)

---

## 19. COMPARATOR INPUT WIDTH
**Meaning:** Width of comparator input (for Hamming code implementation)
- **COMPARATOR INPUT WIDTH is the input width of comparison circuit**
- Used for **Hamming code error correction** implementation
- Example: `32` bits - split data into 32-bit chunks for independent comparison
- **Typically set to 32** for simplicity
- **Not mandatory** - if not using Hamming code, set to 0 or 32

**Default Value:** 32 (when not specified)

---

## 20. COMPARATOR DEPTH
**Meaning:** Depth of comparator pipeline (for timing optimization)
- **COMPARATOR DEPTH is the pipeline depth** (number of stages)
- Values:
  - **0** = Combinational logic (result available in 1 clock cycle)
  - **> 0** = Pipelined logic (result takes multiple cycles but higher frequency)
- Used to **optimize timing** during synthesis
- **Typically set to 0** for simplicity

**Default Value:** 0 (combinational logic)

---

## 21. MD5 & Script Version
**Meaning:** Auto-generated MD5 hash + script version for integrity validation
- **MD5 & Script Version is a unique identifier** of this INFO row
- **MD5** = 128-bit hash computed from row content (excluding MD5 column itself)
- Script performs:
  1. **Calculate MD5** from all content
  2. **Compare** old MD5 vs new MD5
  3. If **different** → warning (someone edited INFO file)
- **Script version** = script version used (e.g., v3.0.0)
- **Do not edit manually** - script auto-generates this
- Used to **detect unauthorized changes** in INFO file

**Default Value:** Auto-generated by script

---

## 22. NOTE
**Meaning:** Optional custom notes or documentation
- **NOTE is a free-form field** for additional information
- Example:
  - `AXI master port`
  - `Critical safety signal`
  - `3rd party vendor spec revision 2.1`
  - `Needs timing margin for parity`
- Used to **store context** or special requirements
- **Completely optional** - does not affect processing

**Default Value:** Empty string ("")

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ INFO Row (1 signal needing parity)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [IP NAME] = BOS_AXICRYPT                                  │
│ [SIGNAL PORT NAME] = AXICRYPT_AXI_MI0_WDATA (256 bits)    │
│ [BIT WIDTH] = 256                                         │
│ [PARITY SOURCE BIT WIDTH] = 128 (parity bits)            │
│ [DRIVE/RECEIVE] = DRIVE (module outputs)                 │
│ [SIGNAL VALID NAME] = AXICRYPT_AXI_MI0_WVALID           │
│ [PARITY PORT NAME] = AXICRYPT_AXI_MI0_WDATA_PARITY      │
│ [EVEN ODD] = EVEN                                        │
│ [CLOCK] = ACLK                                           │
│ [RESET] = RESETN_ACLK                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Script will:                                                │
│                                                             │
│ 1. Find file containing BOS_AXICRYPT (via IP FILE LIST)   │
│ 2. Create INPUT port: AXICRYPT_AXI_MI0_WDATA_PARITY (128b)│
│ 3. Create logic:                                           │
│    - Capture WDATA when WVALID = 1 (DRIVE)               │
│    - Compare parity (EVEN)                               │
│    - Output error port (if specified)                    │
│ 4. Synchronize with ACLK, reset with RESETN_ACLK        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Output:                                                     │
│                                                             │
│ - BOS_AXICRYPT_NEW.v (module with added parity ports)    │
│ - BOS_AXICRYPT_PARITY_NEW.v (parity generator module)    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Required vs Optional Summary

### ✅ Required Parameters (11) - No Default Values
1. IP NAME - Must be specified
2. CLOCK - Must be specified  
3. RESET - Must be specified
4. SIGNAL PORT NAME - Must be specified
5. DRIVE/RECEIVE - Must be specified
6. SIGNAL VALID NAME - Must be specified
7. PARITY PORT NAME - Must be specified
8. IP FILE LIST - Must be specified
9. BIT WIDTH - Must be specified
10. PARITY SOURCE BIT WIDTH - Must be specified
11. EVEN ODD - Must be specified

### ❌ Optional Parameters (9) - Have Default Values
1. No - Auto-generated (1, 2, 3, ...)
2. VERSION - Default: "" (empty)
3. HSR ID - Default: "" (empty)
4. SM ID - Default: "" (empty)
5. GROUP - Default: "" (no group)
6. ERROR PORT - Default: "" (no error port)
7. ERROR DOUBLE - Default: "YES" (when ERROR PORT empty) or "NO" (when ERROR PORT exists)
8. COMPARATOR INPUT WIDTH - Default: 32
9. COMPARATOR DEPTH - Default: 0 (combinational)
10. NOTE - Default: "" (empty)

### 🔄 Auto-Generated (1)
1. MD5 & Script Version - Auto-generated by script

---

## Default Values Quick Reference

| Parameter | Required | Default Value | Notes |
|-----------|----------|---------------|-------|
| No | ❌ | Auto (1,2,3...) | Sequential numbering |
| VERSION | ❌ | "" | Empty string |
| HSR ID | ❌ | "" | Empty string |
| SM ID | ❌ | "" | Empty string |
| IP NAME | ✅ | N/A | Must specify |
| CLOCK | ✅ | N/A | Must specify |
| RESET | ✅ | N/A | Must specify |
| SIGNAL PORT NAME | ✅ | N/A | Must specify |
| GROUP | ❌ | "" | No group filtering |
| DRIVE/RECEIVE | ✅ | N/A | Must specify |
| SIGNAL VALID NAME | ✅ | N/A | Must specify |
| PARITY PORT NAME | ✅ | N/A | Must specify |
| IP FILE LIST | ✅ | N/A | Must specify |
| ERROR PORT | ❌ | "" | No error reporting |
| ERROR DOUBLE | ❌ | "YES" (if ERROR PORT empty)<br>"NO" (if ERROR PORT exists) | Depends on ERROR PORT |
| BIT WIDTH | ✅ | N/A | Must specify |
| PARITY SOURCE BIT WIDTH | ✅ | N/A | Must specify |
| EVEN ODD | ✅ | N/A | Must specify |
| COMPARATOR INPUT WIDTH | ❌ | 32 | For Hamming code |
| COMPARATOR DEPTH | ❌ | 0 | Combinational logic |
| MD5 & Script Version | 🔄 | Auto-generated | Integrity check |
| NOTE | ❌ | "" | Empty string |

---

**Last Updated:** February 9, 2026 | **Version:** 3.0.1 | **Language:** English | **Added:** Default Values
