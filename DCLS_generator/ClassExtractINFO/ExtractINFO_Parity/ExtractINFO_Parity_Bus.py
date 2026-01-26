from DCLS_generator.ClassExtractINFO.ExtractINFO_Parity.ExtractINFO_Parity import ExtractINFO_Parity


class ExtractINFO_Parity_Bus(ExtractINFO_Parity):
    def __init__(self, info_dict):
        self.info_dict = info_dict
        self._extract_fierr_location()

    def _extract_fault_injection(self) -> list:
        fault_list = []
        fault_str = self.info_dict["FAULT INJECTION"]
        if fault_str:
            fault_str_list = fault_str.split(",")
            for fault_sub_str in fault_str_list:
                fault_sub_str.replace(" ", "").replace("\n", "")
                fault_str_split = fault_sub_str.split("@")
                valid_signal = fault_str_split[1]
                fault_signal = fault_str_split[0].replace("{", "").replace("}", "").split(",")
                fault_list += [[valid_signal, fault_signal]]
        return fault_list

    # [TODO] Move this to GenerateParityBus later
    # For now, only support data fierr for regular channel and parity fierr for checker
    def _process_fault_injection(self) -> str:
        # Data of this field should be consistent
        signal_list = self.info_dict["FAULT INJECTION"].split(",")
        if signal_list[0]:
            if self._extract_error_port_ip()[0]:
                total_size = int(super()._extract_dimension()[0] / super()._extract_dimension()[1])
            else:
                total_size = super()._extract_dimension()[0]

            signal_name = signal_list[0].split("@")[0].split("[")[0].strip()
            control_signal = f"r_{signal_list[0].split('@')[1].split('[')[0].strip()}"
            result_signal = f"r_{signal_name}"

            return generate_verilog_assign(signal_list, total_size, signal_name, control_signal, result_signal)
        else:
            ip_port, ip_par_port =  self._extract_parity_signals_ip()
            ip_err_port, ip_err_dup = self._extract_error_port_ip()
            if ip_err_port:
                return f"\nr_{ip_par_port} = {ip_par_port};"
            else:
                return f"\nr_{ip_port} = {ip_port};"
    # --------------------------------------------
    # COMMON
    # --------------------------------------------
    # def _extract_dimension(self):
    #     bit_width = int(self.info_dict["BIT WIDTH"].strip())
    #     par_width = int(self.info_dict["PARITY SOURCE BIT WIDTH"].strip())
    #     return bit_width, par_width

    # --------------------------------------------
    # IP
    # --------------------------------------------
    def _extract_filelist_list_ip(self) -> list:
        filelist_str = self.info_dict["IP FILE LIST"]
        assert filelist_str, f"filelist was not specified. {self.info_dict}"
        filelist_list = filelist_str.replace(" ", "").replace("\n", "")
        return filelist_list

    def _extract_ip_name(self):
        ip_name = self.info_dict["IP NAME"].strip()
        return ip_name

    def _extract_ip_clock_reset(self):
        clk = self.info_dict["IP CLOCK NAME"].strip()
        rst = self.info_dict["IP RESET NAME"].strip()
        return clk, rst

    def _extract_parity_signals_ip(self):
        ip_port = self.info_dict["IP SIGNAL PORT NAME"].strip()
        ip_par_port = self.info_dict["IP PARITY PORT NAME"].strip()
        return ip_port, ip_par_port

    def _extract_error_port_ip(self):
        # ip_err_port decide the direction of the parity check
        # 0: IP->BUS, output IP parity
        # 1: BUS->IP, input IP parity
        ip_err_port = self.info_dict["IP ERROR PORT"].strip()
        ip_err_dup  = self.info_dict["IP ERROR DOUBLE"].strip()
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

    def _extract_fierr_location(self) -> None:
        location = self.info_dict["FAULT INJECTION LOCATION"].strip()
        if location == "CHECKER":
            is_checker = True
        elif location == "":
            is_checker = False
        else:
            raise ValueError("Invalid FIERR location")

        if is_checker:
            ip_err_port, ip_err_dup = self._extract_error_port_ip()
            assert ip_err_port, "Inconsistent information between Error port and FIERR location"

    # --------------------------------------------
    # BUS
    # --------------------------------------------
    def _extract_filelist_list_bus(self) -> list:
        filelist_str = self.info_dict["BUS FILE LIST"]
        filelist_list = filelist_str.replace(" ", "").replace("\n", "")
        return filelist_list

    def _extract_bus_name(self):
        bus_name = self.info_dict["BUS NAME"].strip()
        return bus_name

    def _extract_bus_clock_reset(self):
        clk = self.info_dict["BUS CLOCK NAME"].strip()
        rst = self.info_dict["BUS RESET NAME"].strip()
        return clk, rst

    def _extract_parity_signals_bus(self):
        bus_port = self.info_dict["BUS SIGNAL PORT NAME"].strip()
        bus_par_port = self.info_dict["BUS PARITY PORT NAME"].strip()
        return bus_port, bus_par_port

    def _extract_error_port_bus(self):
        # ip_err_port decide the direction of the parity check
        # 0: IP->BUS, output IP parity
        # 1: BUS->IP, input IP parity
        bus_err_port = self.info_dict["BUS ERROR PORT"].strip()
        bus_err_dup  = self.info_dict["BUS ERROR DOUBLE"].strip()
        if bus_err_dup.lower() == "yes" or bus_err_dup == "":
            bus_err_dup = True
        elif bus_err_dup.lower() == "no":
            bus_err_dup = False
        else:
            raise ValueError(f"Un-recognized doubling mode {bus_err_dup}.")
        return bus_err_port, bus_err_dup


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
