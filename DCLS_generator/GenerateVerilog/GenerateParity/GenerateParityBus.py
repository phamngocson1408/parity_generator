from DCLS_generator.GenerateVerilog.GenerateVerilog import GenerateVerilog
from DCLS_generator.ClassExtractINFO.ExtractINFO_Parity.ExtractINFO_Parity_Bus import ExtractINFO_Parity_Bus
from DCLS_generator.instanceModifier.modify_instance import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class GenerateBus(GenerateVerilog):
    safety_scheme = 'Parity'
    ip_set = set()
    bus_set = set()

    # IP
    ip_clk_rst_blk = {}
    ip_port_blk = {}
    ip_err_port_blk = {}
    ip_wire_blk = {}
    ip_reg_blk = {}
    ip_sig_assign = {}
    ip_par_blk = {}
    fault_inj_blk = {}

    ip_bus_par_blk = {}
    ip_bus_par_list = {}
    ip_bus_err_blk = {}

    # Tracking common special signals that are used for multiple signals
    ip_fierr_map = {}
    is_error_dup_ip = {}

    # BUS
    bus_par_blk = {}
    bus_clk_rst_blk = {}
    bus_port_blk = {}
    bus_err_port_blk = {}
    bus_wire_blk = {}
    bus_reg_blk = {}
    bus_sig_assign = {}

    bus_bus_par_blk = {}
    bus_bus_par_list = {}
    bus_bus_err_blk = {}

    # Tracking common special signals that are used for multiple signals
    # bus_fierr_map = {}  # For now, do not inject error from bus side
    is_error_dup_bus = {}

    # List of ports
    original_inport = {}
    original_outport = {}
    extra_inport = {}
    extra_outport = {}

    original_inport_bus = {}
    original_outport_bus = {}
    extra_inport_bus = {}
    extra_outport_bus = {}

    def __init__(self, Parity_INFOExtractor: ExtractINFO_Parity_Bus):
        # Info read from INFO file
        self.bit_width, self.par_width = Parity_INFOExtractor._extract_dimension()
        self.is_even = Parity_INFOExtractor._is_even()
        # IP
        self.ip_port, self.ip_par_port = Parity_INFOExtractor._extract_parity_signals_ip()
        self.clk_ip, self.rst_ip = Parity_INFOExtractor._extract_ip_clock_reset()
        self.fault_list = Parity_INFOExtractor._extract_fault_injection()
        self.ip_name = Parity_INFOExtractor._extract_ip_name()
        self.ip_err_port, self.ip_err_dup = Parity_INFOExtractor._extract_error_port_ip()
        self.drive_receive = Parity_INFOExtractor._extract_drive_receive()
        self.signal_valid_name = Parity_INFOExtractor._extract_signal_valid_name()
        self.comparator_input_width = Parity_INFOExtractor._extract_comparator_input_width()
        self.comparator_depth = Parity_INFOExtractor._extract_comparator_depth()        # BUS - REMOVED: BUS columns have been removed from INFO file
        # self.bus_name = Parity_INFOExtractor._extract_bus_name()
        # self.bus_port, self.bus_par_port = Parity_INFOExtractor._extract_parity_signals_bus()
        # self.clk_bus, self.rst_bus = Parity_INFOExtractor._extract_bus_clock_reset()
        # self.bus_err_port, self.bus_err_dup = Parity_INFOExtractor._extract_error_port_bus()
        # Share across multiple rows
        self._init_generator()
        self.pre_print_fierr = Parity_INFOExtractor._process_fault_injection()
        # self._generate_reg_ip()

    # --------------------------------------------
    # IP
    # --------------------------------------------
    # ------------------ Port ------------------ #
    def _generate_port_ip(self):
        port_blk = ""
        port_blk += f"\n    input  [{self.bit_width}-1:0] {self.ip_port},"
        if self.drive_receive == "RECEIVE":
            port_blk += f"\n    input  [{self.bit_width // self.par_width}-1:0] {self.ip_par_port},"
        else:
            port_blk += f"\n    output [{self.bit_width // self.par_width}-1:0] {self.ip_par_port},"
        if self.signal_valid_name:
            port_blk += f"\n    input  {self.signal_valid_name},"
        return port_blk

    def _generate_port_ip_err(self):
        port_blk = ""
        port_blk += f"\n    input  EN{self.ip_err_port},"
        port_blk += f"\n    output {self.ip_err_port},"
        if self.ip_err_dup:
            port_blk += f"\n    output {self.ip_err_port}_B,"
        return port_blk

    # def _generate_port_bus(self):
    #     port_blk = ""
    #     if self.bus_port:
    #         port_blk += f"\n    input  [{self.bit_width}-1:0] {self.bus_port},"
    #     if self.bus_par_port:
    #         port_blk += f"\n    input  [{self.par_width}-1:0] {self.bus_par_port},"
    #     return port_blk

    # def _generate_port_bus_err(self):
    #     port_blk = ""
    #     port_blk += f"\n    output {self.ip_err_port},"
    #     if self.ip_err_dup:
    #         port_blk += f"\n    output {self.ip_err_port}_B,"
    #     return port_blk

    # ------------------ Wire ------------------ #
    def _generate_wire_ip(self):
        port_blk = ""
        if self.fault_list:
            # Only create register for data signal if fault injection is enabled
            port_blk = f"\nreg [{self.bit_width}-1:0] r_{self.ip_port};"
        return port_blk

    # def _generate_wire_bus(self):
    #     port_blk = f"\nreg [{self.bit_width}-1:0] r_{self.bus_port};"
    #     return port_blk

    # ----------------- Parity ----------------- #
    def _generate_parity_ip(self):
        parity_blk = ""

        if self.drive_receive == "DRIVE":
            sliced_dimension = split_dimension(self.bit_width, self.par_width)
            if self.signal_valid_name:
                # Generate parity only when signal_valid is 1, else 0
                for i, sliced in enumerate(sliced_dimension):
                    if self.is_even:
                        parity_blk += f"\nassign {self.ip_par_port}[{i}] = {self.signal_valid_name} ? (^r_{self.ip_port}{sliced}) : 1'b0;"
                    else:
                        parity_blk += f"\nassign {self.ip_par_port}[{i}] = {self.signal_valid_name} ? ~(^r_{self.ip_port}{sliced}) : 1'b0;"
            else:
                # Original behavior without SIGNAL VALID NAME
                for i, sliced in enumerate(sliced_dimension):
                    if self.is_even:
                        parity_blk += f"\nassign {self.ip_par_port}[{i}] = ^r_{self.ip_port}{sliced};"
                    else:
                        parity_blk += f"\nassign {self.ip_par_port}[{i}] = ~(^r_{self.ip_port}{sliced});"
        elif self.drive_receive == "RECEIVE":
            sliced_dimension = split_dimension(self.bit_width, self.par_width)
            
            if self.signal_valid_name:
                # Gate data with SIGNAL VALID NAME before calculating parity
                parity_blk += f"\nwire [{self.bit_width}-1:0] w_{self.ip_port}_gated = {self.signal_valid_name} ? {self.ip_port} : {self.bit_width}'b0;"
                for i, sliced in enumerate(sliced_dimension):
                    if self.is_even:
                        parity_blk += f"\nwire w_{self.ip_port.lower()}_parity_{i} = ^w_{self.ip_port}_gated{sliced};"
                    else:
                        parity_blk += f"\nwire w_{self.ip_port.lower()}_parity_{i} = ~(^w_{self.ip_port}_gated{sliced});"
            else:
                # Original behavior without SIGNAL VALID NAME
                for i, sliced in enumerate(sliced_dimension):
                    if self.is_even:
                        parity_blk += f"\nwire w_{self.ip_port.lower()}_parity_{i} = ^{self.ip_port}{sliced};"
                    else:
                        parity_blk += f"\nwire w_{self.ip_port.lower()}_parity_{i} = ~(^{self.ip_port}{sliced});"

        return parity_blk + "\n"

    # def _generate_parity_bus(self):
    #     parity_blk = ""

    #     if self.ip_err_port:
    #         sliced_dimension = split_dimension(self.bit_width, self.par_width)
    #         for i in range(len(sliced_dimension)):
    #             parity_blk += f"\nwire w_{self.ip_port.lower()}_parity_{i};"
    #         parity_blk += "\n"

    #         for i, sliced in enumerate(sliced_dimension):
    #             if self.is_even:
    #                 parity_blk += f"\nassign w_{self.ip_port.lower()}_parity_{i} = ^{self.ip_port}{sliced};"
    #             else:
    #                 parity_blk += f"\nassign w_{self.ip_port.lower()}_parity_{i} = ~(^{self.ip_port}{sliced});"

    #     return parity_blk

    # def _generate_parity_ip_at_bus(self):
    #     parity_blk = ""

    #     if not self.bus_err_port:
    #         sliced_dimension = split_dimension(self.bit_width, self.par_width)
    #         for i, sliced in enumerate(sliced_dimension):
    #             if self.is_even:
    #                 parity_blk += f"\nassign {self.bus_par_port}[{i}] = ^r_{self.bus_port}{sliced};"
    #             else:
    #                 parity_blk += f"\nassign {self.bus_par_port}[{i}] = ~(^r_{self.bus_port}{sliced});"

    #     return parity_blk + "\n"

    # def _generate_parity_bus_at_bus(self):
    #     parity_blk = ""

    #     if self.bus_err_port:
    #         sliced_dimension = split_dimension(self.bit_width, self.par_width)
    #         for i in range(len(sliced_dimension)):
    #             parity_blk += f"\nwire w_{self.bus_port.lower()}_parity_{i};"
    #     parity_blk += "\n"

    #     for i, sliced in enumerate(sliced_dimension):
    #         if self.is_even:
    #             parity_blk += f"\nassign w_{self.bus_port.lower()}_parity_{i} = ^{self.bus_port}{sliced};"
    #     else:
    #         parity_blk += f"\nassign w_{self.bus_port.lower()}_parity_{i} = ~(^{self.bus_port}{sliced});"

    # return parity_blk

    # ------------- Error Injection ------------ #
    def _assign_signal_ip(self) -> str:
        signal_assign_blk = f"\n    r_{self.ip_port} = {self.ip_port};"
        return signal_assign_blk

    # def _assign_signal_bus(self) -> str:
    #     signal_assign_blk = f"\n    r_{self.bus_port} = {self.bus_port};"
    #     return signal_assign_blk

    def _inject_error_checker(self):
        fault_sig_declare = set()
        fault_inj_blk = ""

        for fault_list in self.fault_list:
            fault_inj, fault_sig_list = fault_list
            # Extract port name without width specification (e.g., "FIERR_PORT" from "FIERR_PORT[3:0]")
            fault_inj_name = fault_inj.split("[")[0].strip()
            
            # For auto-generated FIERR ports, no per-bit portion logic needed
            # Just use the whole port
            portion = ""
            
            # DEBUG
            # print(f"DEBUG: ip_name={self.ip_name}, ip_err_port={self.ip_err_port}, drive_receive={self.drive_receive}, fault_sig_list={fault_sig_list}")
            
            if fault_list:
                fault_inj_blk += f"\n    if (r_{fault_inj_name}) begin"
                for fault_sig in fault_sig_list:
                    fault_sig_split = fault_sig.split("[")
                    fault_sig_name = fault_sig_split[0].strip()
                    fault_sig_dim  = "[" + fault_sig_split[1]

                    # For RECEIVE mode (parity check), skip all logic as DCLS_COMPARATOR_TEMPLATE directly uses input parity
                    if self.ip_err_port and self.drive_receive == "RECEIVE":
                        # Skip register creation and assignment for receiver parity
                        continue
                    else:
                        fault_sig_declare.add(f"\nreg [{int(self.bit_width/self.par_width)-1}:0] r_{fault_sig_name};")
                        fault_inj_blk += f"\n        r_{fault_sig_name}{portion} = {concat_2d(fault_sig_name, fault_sig_dim, self.bit_width)}{portion};"

                fault_inj_blk += f"\n    end else begin"
                for fault_sig in fault_sig_list:
                    fault_sig_name = fault_sig.split("[")[0].strip()

                    # Skip assignment for receiver parity in RECEIVE mode
                    if self.ip_err_port and self.drive_receive == "RECEIVE":
                        continue
                    else:
                        fault_inj_blk += f"\n        r_{fault_sig_name}{portion} = {fault_sig_name}{portion};"
                fault_inj_blk += f"\n    end"

        return "".join(fault_sig_declare), fault_inj_blk

    # ----------------- Error ------------------ #
    def _generate_error_check_ip(self) -> str:
        err_blk = ""
        if self.drive_receive == "RECEIVE":
            err_blk += f"\n\nwire w_AnyError_{self.ip_port};"

            # Use DCLS_COMPARATOR_TEMPLATE instead of reduction XOR
            # Calculate parity width
            par_width_bits = self.bit_width // self.par_width
            
            err_blk += f"\nDCLS_COMPARATOR_TEMPLATE #(\n"
            err_blk += f"    .DATA_WIDTH({par_width_bits}),\n"
            err_blk += f"    .MAX_INPUT_WIDTH({self.comparator_input_width}),\n"
            err_blk += f"    .NUM_OR_STAGES({self.comparator_depth})\n"
            err_blk += f") u_comparator_{self.ip_port.lower()} (\n"
            err_blk += f"    .CLK({self.clk_ip}),\n"
            err_blk += f"    .RESETN({self.rst_ip}),\n"
            err_blk += f"    .DATA_IN_A({self.ip_par_port}),\n"
            
            # Calculate expected parity
            sliced_dimension = split_dimension(self.bit_width, self.par_width)
            err_blk += f"    .DATA_IN_B({{ "
            for i in range(len(sliced_dimension)-1, -1, -1):  # from high to low
                err_blk += f"w_{self.ip_port.lower()}_parity_{i}, "
            err_blk = err_blk[:-2] + f" }}),\n"
            
            err_blk += f"    .ENERR_DCLS(r_EN{self.ip_err_port}),\n"
            err_blk += f"    .FIERR_DCLS(r_FIERR_{self.ip_port}),\n"
            err_blk += f"    .ERR_DCLS({self.ip_err_port}),\n"
            err_blk += f"    .ERR_DCLS_B({self.ip_err_port}_B)\n"
            err_blk += f");\n"

            # No longer need to track w_AnyError_ since we're directly connecting to output ports
        return err_blk

    # def _generate_error_check_bus(self) -> str:
    #     err_blk = ""
    #     if self.bus_err_port:
    #         err_blk += f"\n\nwire w_AnyError_{self.bus_port};"

    #         sliced_dimension = split_dimension(self.bit_width, self.par_width)
    #         err_blk += f"\nassign w_AnyError_{self.bus_port} = ("
    #         for i in range(len(sliced_dimension)):
    #             err_blk += f"\n    (w_{self.bus_port.lower()}_parity_{i} ^ r_{self.bus_par_port}[{i}]) |"

    #         err_blk = err_blk[:-1] + "\n);\n"

    #         GenerateBus.ip_bus_par_list[self.bus_name][self.bus_err_port].append(f"w_AnyError_{self.bus_port}")
    #     return err_blk

    def _generate_error(self, ip_name: str, clk: str, rst: str, is_err_dup: bool):
        # BOS_ERROR_DOUBLE module is no longer needed - error ports are directly connected
        # from DCLS_COMPARATOR_TEMPLATE output (ERR_DCLS and ERR_DCLS_B)
        return ""

    # --------------------------------------------
    # WRAPPER
    # --------------------------------------------
    # This should be run once for each row
    def _wrapper_ip(self) -> None:
        GenerateBus.ip_port_blk[self.ip_name] += self._generate_port_ip()
        GenerateBus.ip_wire_blk[self.ip_name] += self._generate_wire_ip()
        GenerateBus.ip_reg_blk[self.ip_name] += self._inject_error_checker()[0]
        if not self.ip_err_port:
            GenerateBus.ip_sig_assign[self.ip_name] += self._assign_signal_ip()
            # GenerateBus.fault_inj_blk[self.ip_name] += self._inject_error()
            # GenerateBus.fault_inj_blk[self.ip_name] += self._inject_error_checker()
        # GenerateBus.fault_inj_blk[self.ip_name] += "".join(self._inject_error_checker()[1])
        GenerateBus.fault_inj_blk[self.ip_name] += "\n\t" + self.pre_print_fierr
        GenerateBus.ip_par_blk[self.ip_name] += self._generate_parity_ip()

        # GenerateBus.ip_bus_par_blk[self.ip_name] += self._generate_parity_bus()  # REMOVED: BUS columns removed
        GenerateBus.ip_bus_err_blk[self.ip_name] += self._generate_error_check_ip()

    # def _wrapper_bus(self) -> None:
    #     GenerateBus.bus_port_blk[self.bus_name] += self._generate_port_bus()
    #     GenerateBus.bus_wire_blk[self.bus_name] += self._generate_wire_bus()
    #     GenerateBus.bus_reg_blk[self.bus_name] += self._inject_error_checker()[0]
    #     if not self.bus_err_port:
    #         GenerateBus.bus_sig_assign[self.bus_name] += self._assign_signal_bus()
    #     GenerateBus.bus_bus_par_blk[self.bus_name] += self._generate_parity_bus()

    #     GenerateBus.bus_bus_par_blk[self.bus_name] += self._generate_parity_bus()
    #     GenerateBus.bus_bus_err_blk[self.bus_name] += self._generate_error_check_bus()

    def _list_port_ip(self):
        port_list = {}
        for ip_name in GenerateBus.ip_set:
            original_inport  = list(set(tuple(lst) for lst in GenerateBus.original_inport[ip_name]))
            original_outport = list(set(tuple(lst) for lst in GenerateBus.original_outport[ip_name]))
            extra_inport     = list(set(tuple(lst) for lst in GenerateBus.extra_inport[ip_name]))
            extra_outport    = list(set(tuple(lst) for lst in GenerateBus.extra_outport[ip_name]))
            port_list[ip_name] = original_inport, original_outport, extra_inport, extra_outport
        return port_list

    # def _list_port_bus(self):
    #     port_list = {}
    #     for bus_name in GenerateBus.bus_set:
    #         original_inport  = list(set(tuple(lst) for lst in GenerateBus.original_inport_bus[bus_name]))
    #         original_outport = list(set(tuple(lst) for lst in GenerateBus.original_outport_bus[bus_name]))
    #         extra_inport     = list(set(tuple(lst) for lst in GenerateBus.extra_inport_bus[bus_name]))
    #         extra_outport    = list(set(tuple(lst) for lst in GenerateBus.extra_outport_bus[bus_name]))
    #     port_list[bus_name] = original_inport, original_outport, extra_inport, extra_outport
    # return port_list

    # This should be run once for each Driver
    # def _generate_module_ip(self):
    def _generate_module_ip(self, ip_name):
        fierr_dup = set()
        module_blk = ""
        fierr_declaration_set = set()
        # for ip_name in GenerateBus.ip_set:
        clk = GenerateBus.ip_clk_rst_blk[ip_name].get('clk')
        rst = GenerateBus.ip_clk_rst_blk[ip_name].get('rst')

        module_blk += f"module {ip_name}_IP_PARITY_GEN ("
        module_blk += f"\n    input {clk}, {rst},"
        fierr_cnt = count_fierr_bit(GenerateBus.ip_fierr_map[ip_name])
        for fierr, _ in GenerateBus.ip_fierr_map[ip_name].items():
            cnt = fierr_cnt[fierr.split('[')[0].strip()]
            fierr_declaration_set.add(f"\n    input [{cnt}-1:0] {fierr.split('[')[0].strip()},")
            # module_blk += f"\n    input {fierr},"
        module_blk += "".join(fierr_declaration_set)
        for ip_err_port in GenerateBus.ip_bus_par_list[ip_name]:
            module_blk += GenerateBus.ip_err_port_blk[ip_err_port]
        module_blk += GenerateBus.ip_port_blk[ip_name]
        module_blk = module_blk[:-1] + "\n);\n"

        module_blk += GenerateBus.ip_wire_blk[ip_name] + "\n"
        for fierr, _ in GenerateBus.ip_fierr_map[ip_name].items():
            if "[" in fierr:
                if fierr.split("[")[0] not in fierr_dup:
                    module_blk += generate_synchronizer(clk=clk, rst=rst, signal=fierr.split("[")[0], size=(self.bit_width/self.par_width))
                    fierr_dup.add(fierr.split("[")[0])
            else:
                module_blk += generate_synchronizer(clk=clk, rst=rst, signal=fierr)
        
        # Add synchronizer for EN{ip_err_port} signal to create r_ENERR_{ip_err_port}
        for ip_err_port in GenerateBus.ip_bus_par_list[ip_name]:
            module_blk += generate_synchronizer(clk=clk, rst=rst, signal=f"EN{ip_err_port}")
        
        module_blk += GenerateBus.ip_reg_blk[ip_name] + "\n"
        module_blk += "\nalways@(*) begin"
        # module_blk += GenerateBus.ip_sig_assign[ip_name]
        module_blk += GenerateBus.fault_inj_blk[ip_name]
        # module_blk += self.pre_print_fierr
        module_blk += "\nend\n"

        module_blk += GenerateBus.ip_par_blk[ip_name]
        module_blk += GenerateBus.ip_bus_par_blk[ip_name]
        module_blk += GenerateBus.ip_bus_err_blk[ip_name]
        module_blk += self._generate_error(ip_name, clk, rst, GenerateBus.is_error_dup_ip[ip_name])

        module_blk += "\nendmodule\n\n"

        return module_blk

    # def _generate_module_bus(self):
    #     fierr_dup = set()
    #     module_blk = ""
    #     for bus_name in GenerateBus.bus_set:
    #         clk = GenerateBus.bus_clk_rst_blk[bus_name].get('clk')
    #         rst = GenerateBus.bus_clk_rst_blk[bus_name].get('rst')

    #         module_blk += f"module {bus_name}_BUS_PARITY_GEN ("
    #         module_blk += f"\n    input {clk}, {rst},"
    #         # [TODO]
    #         for bus_err_port in GenerateBus.bus_bus_par_list[bus_name]:
    #         module_blk += GenerateBus.bus_err_port_blk[bus_err_port]
    #     module_blk += GenerateBus.bus_port_blk[bus_name]
    #     module_blk = module_blk[:-1] + "\n);\n"

    #     module_blk += GenerateBus.bus_wire_blk[bus_name] + "\n"
    #     module_blk += GenerateBus.bus_reg_blk[bus_name] + "\n"
    #     module_blk += "\nalways@(*) begin"
    #     module_blk += GenerateBus.fault_inj_blk[bus_name]
    #     module_blk += "\nend\n"

    #     module_blk += GenerateBus.bus_par_blk[bus_name]
    #     module_blk += GenerateBus.bus_bus_par_blk[bus_name]
    #     module_blk += GenerateBus.ip_bus_err_blk[bus_name]
    #     module_blk += self._generate_error(bus_name, clk, rst, GenerateBus.is_error_dup_bus[bus_name])

    #     module_blk += "\nendmodule\n\n"

    # return module_blk

    # This should be run after finish generating
    def _reset_generator(self) -> None:
        # IP
        GenerateBus.ip_set = set()

        GenerateBus.ip_clk_rst_blk = {}
        GenerateBus.ip_port_blk = {}
        GenerateBus.ip_err_port_blk = {}
        GenerateBus.ip_wire_blk = {}
        GenerateBus.ip_reg_blk = {}
        GenerateBus.ip_sig_assign = {}
        GenerateBus.ip_par_blk = {}
        GenerateBus.fault_inj_blk = {}

        GenerateBus.ip_bus_par_blk = {}
        GenerateBus.ip_bus_err_blk = {}

        GenerateBus.ip_fierr_map = {}
        GenerateBus.is_error_dup_ip = {}

        # BUS
        GenerateBus.bus_clk_rst_blk = {}
        GenerateBus.bus_port_blk = {}
        GenerateBus.bus_err_port_blk = {}
        GenerateBus.bus_wire_blk = {}
        GenerateBus.bus_reg_blk = {}
        GenerateBus.bus_sig_assign = {}

        GenerateBus.bus_fierr_map = {}
        GenerateBus.is_error_dup_bus = {}

        # Port list
        GenerateBus.original_inport = []
        GenerateBus.original_outport = []
        GenerateBus.extra_inport = []
        GenerateBus.extra_outport = []

    # This should be run before starting generating
    def _init_generator(self) -> None:
        if self.ip_name not in GenerateBus.ip_set:
            # Keep track of IP/BUS list
            GenerateBus.ip_set.add(self.ip_name)
            # GenerateBus.bus_set.add(self.bus_name)  # REMOVED: BUS columns removed
            GenerateBus.is_error_dup_ip[self.ip_name] = self.ip_err_dup
            # GenerateBus.is_error_dup_bus[self.bus_name] = self.bus_err_dup  # REMOVED: BUS columns removed
            # Port list
            GenerateBus.original_inport[self.ip_name] = [["", self.clk_ip, ""], ["", self.rst_ip, ""]]
            GenerateBus.original_outport[self.ip_name] = []
            GenerateBus.extra_inport[self.ip_name] = []
            GenerateBus.extra_outport[self.ip_name] = []

            # GenerateBus.original_inport_bus[self.bus_name] = [["", self.clk_bus, ""], ["", self.rst_bus, ""]]  # REMOVED: BUS columns removed
            # GenerateBus.original_outport_bus[self.bus_name] = []  # REMOVED: BUS columns removed
            # GenerateBus.extra_inport_bus[self.bus_name] = []  # REMOVED: BUS columns removed
            # GenerateBus.extra_outport_bus[self.bus_name] = []  # REMOVED: BUS columns removed
            # Init IP ...
            GenerateBus.ip_port_blk[self.ip_name] = ""
            GenerateBus.ip_wire_blk[self.ip_name] = ""
            GenerateBus.ip_reg_blk[self.ip_name] = ""
            GenerateBus.ip_sig_assign[self.ip_name] = ""
            GenerateBus.ip_par_blk[self.ip_name] = ""
            GenerateBus.fault_inj_blk[self.ip_name] = ""

            GenerateBus.ip_bus_par_blk[self.ip_name] = ""
            GenerateBus.ip_bus_par_list[self.ip_name] = {}
            GenerateBus.ip_bus_err_blk[self.ip_name] = ""
            GenerateBus.ip_clk_rst_blk[self.ip_name] = {"clk": self.clk_ip, "rst": self.rst_ip}
            GenerateBus.ip_fierr_map[self.ip_name] = {}

            # Init BUS - REMOVED: BUS columns removed
            # GenerateBus.bus_clk_rst_blk[self.bus_name] = {"clk": self.clk_bus, "rst": self.rst_bus}
            # GenerateBus.bus_port_blk[self.bus_name] = ""
            # GenerateBus.bus_err_port_blk[self.bus_name] = ""
            # GenerateBus.bus_wire_blk[self.bus_name] = ""
            # GenerateBus.bus_reg_blk[self.bus_name] = ""
            # GenerateBus.bus_sig_assign[self.bus_name] = ""

        # if self.fault_list and not self.ip_err_port:
        if self.fault_list:
            try:
                for fault_list in self.fault_list:
                    GenerateBus.ip_fierr_map[self.ip_name][fault_list[0]].add({self.ip_port})
            except:
                for fault_list in self.fault_list:
                    GenerateBus.ip_fierr_map[self.ip_name][fault_list[0]] = {self.ip_port}

        if self.ip_err_port:
            GenerateBus.original_inport[self.ip_name].append([f"[{self.bit_width}-1:0]", self.ip_port, ""])
            GenerateBus.extra_inport[self.ip_name].append([f"[{self.bit_width // self.par_width}-1:0]", self.ip_par_port, ""])
            GenerateBus.extra_outport[self.ip_name].append([f"", self.ip_err_port, ""])
            GenerateBus.extra_inport[self.ip_name].append([f"", f"EN{self.ip_err_port}", ""])
            if self.ip_err_dup:
                GenerateBus.extra_outport[self.ip_name].append([f"", f"{self.ip_err_port}_B", ""])
        else:
            GenerateBus.original_outport[self.ip_name].append([f"[{self.bit_width}-1:0]", self.ip_port, ""])
            GenerateBus.extra_outport[self.ip_name].append([f"[{self.bit_width // self.par_width}-1:0]", self.ip_par_port, ""])
        
        for fault_list in self.fault_list:
            # FIERR port is always 1 bit
            control_port_name = fault_list[0].split("[")[0]  # Get port name
            GenerateBus.extra_inport[self.ip_name].append(["", control_port_name, ""])
        
        # Add SIGNAL VALID NAME port if specified
        if self.signal_valid_name:
            GenerateBus.extra_inport[self.ip_name].append(["", self.signal_valid_name, ""])

        if self.ip_name in GenerateBus.ip_set:
            if self.ip_err_port:
                try:
                    GenerateBus.ip_bus_par_list[self.ip_name][self.ip_err_port]
                except:
                    GenerateBus.ip_bus_par_list[self.ip_name][self.ip_err_port] = []
                    if self.drive_receive == "RECEIVE":
                        GenerateBus.ip_err_port_blk[self.ip_err_port] = self._generate_port_ip_err()


def split_dimension(size: int, part_size: int) -> list:
    assert size and size > 0, "'BIT WIDTH' should be an integer."
    # Extract dimension
    msb = size - 1
    lsb = 0

    # Calculate ["BIT WIDTH"] and ["PARITY SOURCE BIT WIDTH"]
    range_size = msb - lsb + 1
    assert range_size % part_size == 0, "'BIT WIDTH' should be in multiples of 'PARITY BIT WIDTH'."
    n = range_size // part_size

    result = []
    for i in range(n):
        start = lsb + i * part_size
        if i == n - 1:
            end = msb
        else:
            end = start + part_size - 1
        result.append(f"[{end}:{start}]")

    return result


def generate_synchronizer(clk: str, rst: str, signal: str, size=1) -> str:
    assert size > 0 and signal != ""

    sync_blk = ""
    if size == 1:
        sync_blk += f"\nreg r_{signal};"
    else:
        sync_blk += f"\nreg [{int(size)}-1:0] r_{signal};"
    sync_blk += (f"\nBOS_SOC_SYNCHSR #(.DW({int(size)})) u_bos_synch_{signal} ("
                 f"\n    .I_CLK ({clk}),"
                 f"\n    .I_RESETN ({rst}),"
                 f"\n    .I_D ({signal}),"
                 f"\n    .O_Q (r_{signal})"
                 f"\n);\n")
    return sync_blk


def concat_2d(signal: str, sliced: str, width: int):
    bit_selection = sliced.strip()[1:-1]
    bit_selection = bit_selection.split(":")
    if len(bit_selection) == 1:
        b = int(bit_selection[0])
        if b == 0:
            concated_signal = f"{{{signal}[{width - 1}:1], ~{signal}[0]}}"
        elif b == width - 1:
            concated_signal = f"{{~{signal}[{width-1}], {signal}[{width - 2}:0]}}"
        elif b > 0 or b < width - 1:
            concated_signal = f"{{{signal}[{width - 1}:{b + 1}], ~{signal}[{b}], {signal}[{b - 1}:0]}}"
        else:
            raise ValueError("Bit selection is out of bound")
    elif len(bit_selection) == 2:
        msb = int(bit_selection[0])
        lsb = int(bit_selection[1])
        assert msb >= lsb
        if lsb == 0 and msb < width - 1:
            concated_signal = f"{{{signal}[{width - 1}:{msb + 1}], ~{signal}[{msb}:0]}}"
        elif msb == width - 1 and lsb > 0:
            concated_signal = f"{{~{signal}[{width-1}:{lsb}], {signal}[{lsb - 1}:0]}}"
        elif lsb > 0 or msb < width - 1:
            concated_signal = f"{{{signal}[{width - 1}:{msb + 1}], ~{signal}[{msb}:{lsb}], {signal}[{lsb - 1}:0]}}"
        else:
            raise ValueError("Bit selection is out of bound")
    else:
        raise ValueError("Unsupported bit slicing format")

    return concated_signal


def bracket2underscore(sliced_signal: str) -> str:
    return sliced_signal.replace("[", "_").replace("]", "_").replace(":", "_")


def portion_extraction(sliced_signal: str) -> str:
    start = sliced_signal.rfind('[')
    end = sliced_signal.rfind(']')

    if start >= 0 and end <= len(sliced_signal) and end > start:
        sliced_value = sliced_signal[start + 1:end]
        return sliced_value
    else:
        return ""


def count_fierr_bit(old_dict: dict):
    new_dict = {}

    for key in old_dict:
        new_key = key.split("[")[0].strip()

        if new_key in new_dict:
            new_dict[new_key] += 1
        else:
            new_dict[new_key] = 1
    return new_dict


