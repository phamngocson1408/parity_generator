import re
from DCLS_generator.common.prettycode import bcolors
from DCLS_generator.ClassExtractINFO.ExtractINFO import ExtractINFO


class ExtractINFO_DCLS(ExtractINFO):
    def __init__(self, info_dict):
        self.info_dict = info_dict
        self._template_error_check()

    def _extract_gate_list(self):
        gate_str = self.info_dict["INPUT VALID"] + "," + self.info_dict["OUTPUT VALID"]

        gate_dict = {}
        gated_list = []
        cond_position = find_at(gate_str)
        for pos in cond_position:
            gated_signal = find_balanced_braces_backward(gate_str, pos)
            gated_signal = gated_signal[1:-1].replace(" ", "").split(",")
            gated_list += gated_signal
            valid_signal = find_balanced_braces_forward(gate_str, pos)
            valid_signal = valid_signal[1:-1]
            if valid_signal in gate_dict:
                gate_dict[valid_signal].extend(gated_signal)
            else:
                gate_dict[valid_signal] = gated_signal

        gate_dict_d1 = {}
        gated_list_d1 = []
        cond_position = find_at_at(gate_str)
        for pos in cond_position:
            gated_signal = find_balanced_braces_backward(gate_str, pos)
            gated_signal = gated_signal[1:-1].replace(" ", "").split(",")
            gated_list_d1 += gated_signal
            valid_signal = find_balanced_braces_forward(gate_str, pos)
            valid_signal = valid_signal[1:-1]
            if valid_signal in gate_dict_d1:
                gate_dict_d1[valid_signal].extend(gated_signal)
            else:
                gate_dict_d1[valid_signal] = gated_signal

        return gate_dict, gated_list + gated_list_d1, gate_dict_d1

    def _extract_default_list(self):
        try:
            default_str = self.info_dict["DEFAULT RESET"]
        except:
            return {}

        default_dict = {}
        cond_position = find_at(default_str)
        for pos in cond_position:
            default_value = find_balanced_braces_backward(default_str, pos)
            default_value = default_value[1:-1].replace(" ", "")
            default_signal = find_balanced_braces_forward(default_str, pos)
            default_signal = default_signal[1:-1]
            default_dict[default_signal] = default_value
        return default_dict

    def _extract_filelist_list(self) -> list:
        filelist_str = self.info_dict["DESIGN FILE LIST"]
        assert filelist_str, bcolors.FAIL + "filelist was not specified." + bcolors.ENDC
        filelist_list = filelist_str.replace(" ", "").replace("\n", "")
        return filelist_list

    def _extract_ignore_list(self) -> list:
        input_ignore_list = self.info_dict["IGNORE INPUT"]
        if input_ignore_list:
            input_ignore_list = input_ignore_list.replace(" ", "").replace("\n", "").split(",")
        else:
            input_ignore_list = []
        output_ignore_list = self.info_dict["IGNORE OUTPUT"]
        if output_ignore_list:
            output_ignore_list = output_ignore_list.replace(" ", "").replace("\n", "").split(",")
        else:
            output_ignore_list = []

        ignore_list = input_ignore_list + output_ignore_list
        return ignore_list

    def _extract_fault_injection(self) -> list:
        fault_list = ["",[]]
        fault_str = self.info_dict["FAULT INJECTION"]
        if fault_str:
            fault_str.replace(" ", "").replace("\n", "")
            fault_str_split = fault_str.split("@")
            valid_signal = fault_str_split[1]
            fault_signal = fault_str_split[0].replace("{", "").replace("}", "").split(",")
            fault_list = [valid_signal, fault_signal]
        return fault_list

    def _extract_ip(self):
        ip_name = self.info_dict["IP NAME"].strip()
        assert ip_name, bcolors.FAIL + "'IP NAME' field was not specified." + bcolors.ENDC
        # ip_path = self.info_dict["IP INSTANCE PATH"].strip()

        dup_name = self.info_dict["DUPLICATION NAME"].strip()
        assert dup_name, bcolors.FAIL + "'DUPLICATION NAME' field was not specified." + bcolors.ENDC
        dup_path = self.info_dict["DUPLICATION INSTANCE PATH"].strip()  # Useful, but not mandatory

        return ip_name, dup_name, dup_path

    def _extract_clk_rst(self):
        clk = self.info_dict["CLOCK"].strip()
        rst = self.info_dict["RESET"].strip()
        assert clk and rst, bcolors.FAIL + "Clock/Reset were not specified." + bcolors.ENDC
        r2d = self.info_dict["RESET_2D"].strip()
        return clk, rst, r2d

    def _is_wrap(self) -> bool:
        dup_type = self.info_dict["DUPLICATION TYPE"].strip()
        if dup_type == "WRAP" or dup_type == "":
            is_wrap = True
        elif dup_type == "FLAT":
            is_wrap = False
        else:
            raise ValueError(f"Unsupport Duplication Type {dup_type}.")
        return is_wrap

    def _is_error_double(self) -> bool:
        dup_err = self.info_dict["ERROR DOUBLE"].strip().lower()
        if dup_err == "yes" or dup_err == "":
            is_err_dup = True
        elif dup_err == "no":
            is_err_dup = False
        else:
            raise ValueError(f"Unsupport Duplication Type {dup_err}.")
        return is_err_dup

    def _extract_err_port(self):
        ip_err_port = self.info_dict["ERROR PORT"].strip()
        try:
            dup_err_port = self.info_dict["DUPLICATION ERROR PORT"].strip()
        except:
            dup_err_port = ip_err_port
        return ip_err_port, dup_err_port

    # Some fields will be checked further individually/additionally in their dedicated methods
    def _template_error_check(self) -> None:
        # These will read later anyway, but it looks cooler to be read in advance lol
        err_port = self.info_dict["ERROR PORT"].strip()
        assert err_port, bcolors.FAIL + "Error port was not specified" + bcolors.ENDC
        fault_port = self.info_dict["FAULT INJECTION"].strip()
        assert fault_port, bcolors.FAIL + "Fault injection port was not specified" + bcolors.ENDC

        fault_port_split = fault_port.split("@")
        assert len(fault_port_split) == 2, bcolors.FAIL + "Fault injection format is incorrect." + bcolors.ENDC
        fault_port = fault_port_split[1].strip()
        if fault_port.replace("FIERR_", "", 1) != err_port.replace("ERR_", "", 1):
            print(bcolors.WARNING + f"Error Port and Fault Injection Port have inconsistent formats." + bcolors.ENDC)


def find_balanced_braces_backward(string: str, start_index: int):
    stack = 0
    balanced_start_index = None
    
    assert start_index > 0 or start_index <= len(string)
    
    for i in range(start_index, -1, -1):
        c = string[i]
        if c == '}':
            if stack == 0:
                balanced_start_index = i
            # Push to stack
            stack += 1
        elif c == '{':
            # Pop stack
            stack -= 1
            if stack == 0 and balanced_start_index is not None:
                return string[i:balanced_start_index + 1]
    
    return None
    
    
def find_balanced_braces_forward(string: str, start_index: int):
    stack = 0
    balanced_start_index = None
    
    assert start_index > 0 or start_index <= len(string)
    
    for i in range(start_index, len(string)):
        c = string[i]
        if c == '{':
            if stack == 0:
                balanced_start_index = i
            # Push to stack
            stack += 1
        elif c == '}':
            # Pop stack
            stack -= 1
            if stack == 0 and balanced_start_index is not None:
                return string[balanced_start_index:i + 1]
    
    return None
    
    
def find_at(string: str):
    positions = []
    length = len(string)

    for i in range(length):
        if string[i] == '@':
            # if i + 1 >= length or string[i + 1] != '@':
            if string[i + 1] != '@' and string[i - 1] != '@':
                positions.append(i)
    
    return positions
    

def find_at_at(string: str):
    positions = []
    length = len(string)

    for i in range(length - 1):
        if string[i:i + 2] == '@@':
            positions.append(i)
    
    return positions

