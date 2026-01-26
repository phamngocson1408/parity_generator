import re
from DCLS_generator.common.prettycode import bcolors
from DCLS_generator.ClassExtractINFO.ExtractINFO import ExtractINFO


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

