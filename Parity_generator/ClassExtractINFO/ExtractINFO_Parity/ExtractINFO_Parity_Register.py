from Parity_generator.ClassExtractINFO.ExtractINFO_Parity.ExtractINFO_Parity import ExtractINFO_Parity


class ExtractINFO_Parity_Register(ExtractINFO_Parity):
    def __init__(self, info_dict):
        self.info_dict = info_dict

    def _extract_filelist_list_ip(self) -> list:
        filelist_str = self.info_dict["IP FILE LIST"]
        assert filelist_str, "filelist was not specified."
        filelist_list = filelist_str.replace(" ", "").replace("\n", "")
        return filelist_list

    def _extract_register_error_port(self):
        reg_err_port = self.info_dict["REGISTER ERROR PORT"].strip()
        reg_err_dup  = self.info_dict["REGISTER ERROR DOUBLE"].strip()
        return reg_err_port, reg_err_dup

    def _extract_register_clk_rst(self):
        clk = self.info_dict["REGISTER CLOCK"].strip()
        rst = self.info_dict["REGISTER RESET"].strip()
        return clk, rst

    def _extract_reg(self):
        reg_name = self.info_dict["REGISTER NAME"].strip()
        reg_par_name = self.info_dict["REGISTER PARITY NAME"].strip()
        return reg_name, reg_par_name

    def _extract_signal(self):
        val_sig = self.info_dict["REGISTER VALID"].strip()
        reg_sig = self.info_dict["REGISTER INPUT"].strip()
        return val_sig, reg_sig

    def _extract_err_port_reg(self):
        reg_err_port = self.info_dict["REGISTER ERROR PORT"].strip()
        reg_err_dup = self.info_dict["REGISTER ERROR DOUBLE"].strip()
        if reg_err_dup.lower() == "yes":
            reg_err_dup = True
        elif reg_err_dup == "":
            reg_err_dup = True
            print("Error doubling is not specified. Default is 'YES'.")
        elif reg_err_dup.lower() == "no":
            reg_err_dup = False
        else:
            raise ValueError(f"Un-recognized doubling mode {reg_err_dup}.")
        return reg_err_port, reg_err_dup

    def _extract_ip_name(self):
        ip_name = self.info_dict["IP NAME"].strip()
        return ip_name

    def _extract_signal_valid_name(self):
        """Extract SIGNAL VALID NAME from INFO file. Returns empty string if not specified."""
        signal_valid_name = self.info_dict.get("SIGNAL VALID NAME", "").strip()
        return signal_valid_name

