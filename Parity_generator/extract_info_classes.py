import re
import pandas as pd
from Parity_generator.common_utilities import bcolors


# ============================================================================
# Base Class: ExtractINFO
# ============================================================================
class ExtractINFO:
    def __init__(self, INFO_path: str, sheet_name=""):
        self.INFO_path = INFO_path
        self.sheet_name = sheet_name

    def _read_info(self):
        info_df = pd.read_excel(self.INFO_path, header=None)
        info_df.dropna(how='all', axis=0, inplace=True)  # Remove empty rows
        # info_df.dropna(how='all', axis=1, inplace=True)  # Remove empty columns - commented out to keep all columns from header

        # Find the actual header row by looking for the first row with 'No' in the first column
        header_row_idx = None
        for idx, row in info_df.iterrows():
            if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() == 'No':
                header_row_idx = idx
                break
        
        if header_row_idx is None:
            # Fallback: use the first non-empty row
            for idx, row in info_df.iterrows():
                if not row.isna().all():
                    header_row_idx = idx
                    break
        
        if header_row_idx is not None:
            info_df = info_df.loc[header_row_idx:].reset_index(drop=True)
        
        info_df.columns = info_df.iloc[0]  # Set the first row as header
        info_df.columns = info_df.columns.fillna('')  # Fill NaN in header with empty string
        info_df = info_df.iloc[1:]
        info_df = info_df.fillna('')
        info_df = info_df.astype(str)

        info_dict = info_df.to_dict(orient='records')[0]

        return info_dict

    def _read_info_multi(self):
        if self.sheet_name:
            info_df = pd.read_excel(self.INFO_path, sheet_name=self.sheet_name, header=None)
        else:
            info_df = pd.read_excel(self.INFO_path, header=None)
        info_df.dropna(how='all', axis=0, inplace=True)  # Remove empty rows
        # info_df.dropna(how='all', axis=1, inplace=True)  # Remove empty columns - commented out to keep all columns from header

        # Find the actual header row by looking for the first row with 'No' in the first column
        header_row_idx = None
        for idx, row in info_df.iterrows():
            if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() == 'No':
                header_row_idx = idx
                break
        
        if header_row_idx is None:
            # Fallback: use the first non-empty row
            for idx, row in info_df.iterrows():
                if not row.isna().all():
                    header_row_idx = idx
                    break
        
        if header_row_idx is not None:
            info_df = info_df.loc[header_row_idx:].reset_index(drop=True)
        
        info_df.columns = info_df.iloc[0]  # Set the first row as header
        info_df.columns = info_df.columns.fillna('')  # Fill NaN in header with empty string
        info_df = info_df.iloc[1:]
        info_df = info_df.fillna('')
        info_df = info_df.astype(str)

        info_dict_list = [row.to_dict() for index, row in info_df.iterrows()]
        return info_dict_list


# ============================================================================
# Extended Class: ExtractINFO_Parity (extends ExtractINFO)
# ============================================================================
class ExtractINFO_Parity(ExtractINFO):
    def __init__(self, info_dict):
        self.info_dict = info_dict

    def _is_even(self):
        parity_type = self.info_dict["EVEN ODD"].strip().lower()
        if parity_type == "even" or parity_type == "":
            is_even = True
        elif parity_type == "odd":
            is_even = False
        else:
            raise ValueError(f"Unsupport Parity Type {self.info_dict['EVEN ODD']}.")
        return is_even

    def _is_error_double(self) -> bool:
        dup_err = self.info_dict["ERROR DOUBLE"].strip().lower()
        if dup_err == "yes" or dup_err == "":
            is_err_dup = True
        elif dup_err == "no":
            is_err_dup = False
        else:
            raise ValueError(f"Unsupport Duplication Type {dup_err}.")
        return is_err_dup

    def _extract_fault_injection(self) -> list:
        fault_list = []
        fault_str = self.info_dict["FAULT INJECTION"]
        if fault_str:
            fault_str.replace(" ", "").replace("\n", "")
            fault_str_split = fault_str.split("@")
            valid_signal = fault_str_split[1]
            fault_signal = fault_str_split[0].replace("{", "").replace("}", "").split(",")
            fault_list = [valid_signal, fault_signal]
        return fault_list

    def _extract_dimension(self):
        bit_width = int(self.info_dict["BIT WIDTH"].strip())
        bit_width_parity = int(self.info_dict["PARITY SOURCE BIT WIDTH"].strip())
        return bit_width, bit_width_parity


# ============================================================================
# Helper Function for ExtractINFO_Parity_Bus
# ============================================================================
def generate_verilog_assign(signal_list: list, total_size: int, signal_name: str, control_signal: str, result_signal: str):
    parsed_signals = []

    # Parse each signal and extract the range and control bit
    for signal in signal_list:
        if '@' in signal:
            signal_part, control_part = signal.split('@')
        else:
            raise ValueError("Wrong fierr declaration format")
            signal_part = signal
            control_part = None

        if control_part and '[' in control_part:
            control_bit = control_part.split('[')[-1].rstrip(']')
        else:
            control_bit = None

        if '[' in signal_part and ']' in signal_part:
            bit_range = signal_part.split('[')[-1].rstrip(']')
            if ':' in bit_range:
                msb, lsb = map(int, bit_range.split(':'))
            else:
                msb = int(bit_range)
                lsb = msb
        else:
            msb = total_size - 1
            lsb = 0

        parsed_signals.append((msb, lsb, control_bit))

    # Sort the parsed signals by MSB in descending order
    parsed_signals.sort(reverse=True, key=lambda x: x[0])

    assign_str = f"{result_signal} = {{"
    current_bit = total_size - 1

    for msb, lsb, control_bit in parsed_signals:
        # Add the part before the current match
        if current_bit > msb:
            assign_str += f"{signal_name}[{current_bit}:{msb + 1}], "

        # Add the flipped signal part
        if msb == lsb:
            if control_bit is not None:
                assign_str += f"{signal_name}[{msb}] ^ {{$bits({signal_name}[{msb}]){{{control_signal}[{control_bit}]}}}}, "
            else:
                assign_str += f"{signal_name}[{msb}] ^ {{$bits({signal_name}[{msb}]){{{control_signal}}}}}, "
        else:
            print("Hmm, I forgot what case this is...")
            if control_bit is not None:
                assign_str += f"{signal_name}[{msb}:{lsb}] ^ {{$bits({signal_name}[{msb}:{lsb}]){{{control_signal}[{control_bit}]}}}}, "
            else:
                assign_str += f"{signal_name}[{msb}:{lsb}] ^ {{$bits({signal_name}[{msb}]){{{control_signal}}}}}, "

        # Update the current bit
        current_bit = lsb - 1

    # Add the remaining part after the last matched signal
    if current_bit >= 0:
        assign_str += f"{signal_name}[{current_bit}:0] "

    # Close the assignment
    assign_str = assign_str.strip()[:-1] + "};"
    # assign_str += "};"

    return assign_str


# ============================================================================
# Extended Class: ExtractINFO_Parity_Bus (extends ExtractINFO_Parity)
# ============================================================================
class ExtractINFO_Parity_Bus(ExtractINFO_Parity):
    def __init__(self, info_dict):
        self.info_dict = info_dict

    def _extract_fault_injection(self) -> list:
        fault_list = []
        # FAULT INJECTION column removed - always apply FI for RECEIVE ports by default
        sig_port = self.info_dict["SIGNAL PORT NAME"].strip()
        mode = self._extract_drive_receive()
        
        # FIERR (Fault Injection Error) ports are ONLY for RECEIVE signals WITH ERROR PORT
        # For consolidated comparator: only the signal with ERROR PORT gets FIERR input
        # Signals without ERROR PORT will share ERROR PORT and FIERR from first signal
        if mode == "RECEIVE":
            err_port = self.info_dict.get("ERROR PORT", "")
            # Only create FIERR port if this signal has an ERROR PORT
            if err_port and str(err_port).strip().upper() != "NAN":
                # Automatically generate port name: FIERR_<SIGNAL PORT NAME>
                # FIERR port is always 1 bit
                control_port = f"FIERR_{sig_port}"
                par_port = self.info_dict["PARITY PORT NAME"].strip()
                # Format: [[control_port, [target_bit]]]
                fault_list = [[control_port, [f"{par_port}[0]"]]]
        # For DRIVE mode, no FIERR port needed - return empty list
                
        return fault_list

    def _process_fault_injection(self) -> str:
        # FAULT INJECTION column removed - always apply FI for RECEIVE ports by default
        sig_port = self.info_dict["SIGNAL PORT NAME"].strip()
        par_port = self.info_dict["PARITY PORT NAME"].strip()
        mode = self._extract_drive_receive()
        
        control_signal = f"r_FIERR_{sig_port}"
        if mode == "RECEIVE":
            # In RECEIVE mode, DCLS_COMPARATOR_TEMPLATE handles parity comparison directly
            # No need for r_<par_port> intermediate register
            return ""
        else:
            total_size = super()._extract_dimension()[0]
            target = sig_port

            # Use generate_verilog_assign with bit 0 flip by default
            signal_list = [f"{target}[0]@ignore"] 
            result_signal = f"r_{target}"

            return generate_verilog_assign(signal_list, total_size, target, control_signal, result_signal)

    # IP
    def _extract_filelist_list_ip(self) -> list:
        filelist_str = self.info_dict["IP FILE LIST"]
        assert filelist_str, f"filelist was not specified. {self.info_dict}"
        filelist_list = filelist_str.replace(" ", "").replace("\n", "")
        return filelist_list

    def _extract_ip_name(self):
        ip_name = self.info_dict["IP NAME"].strip()
        return ip_name

    def _extract_ip_clock_reset(self):
        clk = self.info_dict["CLOCK"].strip()
        rst = self.info_dict["RESET"].strip()
        return clk, rst

    def _extract_parity_signals_ip(self):
        ip_port = self.info_dict["SIGNAL PORT NAME"].strip()
        ip_par_port = self.info_dict["PARITY PORT NAME"].strip()
        return ip_port, ip_par_port

    def _extract_comparator_input_width(self):
        width = self.info_dict.get("COMPARATOR INPUT WIDTH", "32").strip()
        if width == "":
            width = "32"
        return int(width)

    def _extract_comparator_depth(self):
        depth = self.info_dict.get("COMPARATOR DEPTH", "0").strip()
        if depth == "":
            depth = "0"
        return int(depth)

    def _extract_error_port_ip(self):
        # ip_err_port decide the direction of the parity check
        # 0: IP->BUS, output IP parity
        # 1: BUS->IP, input IP parity
        ip_err_port = self.info_dict["ERROR PORT"].strip()
        ip_err_dup  = self.info_dict["ERROR DOUBLE"].strip()
        if ip_err_dup.lower() == "yes":
            ip_err_dup = True
        elif ip_err_dup == "":
            ip_err_dup = True
            # print("Error doubling is not specified. Default is 'YES'.")
        elif ip_err_dup.lower() == "no":
            ip_err_dup = False
        else:
            raise ValueError(f"Un-recognized doubling mode {ip_err_dup}.")
        return ip_err_port, ip_err_dup

    def _extract_drive_receive(self):
        drive_receive = self.info_dict["DRIVE/RECEIVE"].strip().upper()
        if drive_receive == "DRIVE":
            return "DRIVE"
        elif drive_receive == "RECEIVE":
            return "RECEIVE"
        else:
            raise ValueError(f"Invalid DRIVE/RECEIVE value: {drive_receive}. Must be 'DRIVE' or 'RECEIVE'.")

    def _extract_signal_valid_name(self):
        """Extract SIGNAL VALID NAME from INFO file. Returns empty string if not specified."""
        signal_valid_name = self.info_dict.get("SIGNAL VALID NAME", "").strip()
        return signal_valid_name
