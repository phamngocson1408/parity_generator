from DCLS_generator.ClassExtractINFO.ExtractINFO_Parity.ExtractINFO_Parity import ExtractINFO_Parity


class ExtractINFO_Parity_Signal(ExtractINFO_Parity):
    def __init__(self, info_dict):
        self.info_dict = info_dict

    # --------------------------------------------
    # COMMON
    # --------------------------------------------

    # --------------------------------------------
    # DRIVER
    # --------------------------------------------
    def _extract_filelist_list_drv(self) -> list:
        filelist_str = self.info_dict["DRIVER FILE LIST"]
        assert filelist_str, "filelist was not specified."
        filelist_list = filelist_str.replace(" ", "").replace("\n", "")
        return filelist_list

    def _extract_parity_signals_drv(self):
        drv_port = self.info_dict["DRIVER SIGNAL PORT NAME"].strip()
        drv_par_port = self.info_dict["DRIVER PARITY PORT NAME"].strip()
        return drv_port, drv_par_port

    def _extract_drv_name(self):
        drv_name = self.info_dict["DRIVER NAME"].strip()
        return drv_name

    def _extract_driver_clock_reset(self):
        clk = self.info_dict["DRIVER CLOCK"].strip()
        rst = self.info_dict["DRIVER RESET"].strip()
        return clk, rst

    # --------------------------------------------
    # RECEIVER
    # --------------------------------------------
    def _extract_filelist_list_rcv(self) -> list:
        filelist_str = self.info_dict["RECEIVER FILE LIST"]
        assert filelist_str, "filelist was not specified."
        filelist_list = filelist_str.replace(" ", "").replace("\n", "")
        return filelist_list

    def _extract_parity_signals_rcv(self):
        rcv_port = self.info_dict["RECEIVER SIGNAL PORT NAME"].strip()
        rcv_par_port = self.info_dict["RECEIVER PARITY PORT NAME"].strip()
        return rcv_port, rcv_par_port

    def _extract_error_port_rcv(self):
        rcv_err_port = self.info_dict["RECEIVER ERROR PORT"].strip()
        rcv_err_dup  = self.info_dict["RECEIVER ERROR DOUBLE"].strip()
        if rcv_err_dup.lower() == "yes":
            rcv_err_dup = True
        elif rcv_err_dup == "":
            rcv_err_dup = True
            print("Error doubling is not specified. Default is 'YES'.")
        elif rcv_err_dup.lower() == "no":
            rcv_err_dup = False
        else:
            raise ValueError(f"Un-recognized doubling mode {rcv_err_dup}.")
        return rcv_err_port, rcv_err_dup

    def _extract_rcv_name(self):
        rcv_name = self.info_dict["RECEIVER NAME"].strip()
        return rcv_name

    def _extract_receiver_clock_reset(self):
        clk = self.info_dict["RECEIVER CLOCK"].strip()
        rst = self.info_dict["RECEIVER RESET"].strip()
        return clk, rst

    def _extract_signal_valid_name(self):
        """Extract SIGNAL VALID NAME from INFO file. Returns empty string if not specified."""
        signal_valid_name = self.info_dict.get("SIGNAL VALID NAME", "").strip()
        return signal_valid_name

    # --------------------------------------------
    # CHECK HUMAN ERROR
    # --------------------------------------------
    # def _check_duplicate(self, all_dict):


