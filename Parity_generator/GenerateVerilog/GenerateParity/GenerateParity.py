from Parity_generator.GenerateVerilog.GenerateVerilog import GenerateVerilog
from Parity_generator.extract_info_classes import ExtractINFO_Parity_Signal
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


class GenerateParity(GenerateVerilog):
    safety_scheme = 'Parity'
    drv_set = set()
    rcv_set = set()
    
    # MD5 and version tracking
    md5_hash = ""
    script_version = "3.0.0"

    drv_clk_rst_blk = {}
    drv_port_blk = {}
    drv_wire_blk = {}
    drv_sig_assign = {}
    drv_par_blk = {}
    fault_inj_blk = {}

    rcv_clk_rst_blk = {}
    rcv_port_blk = {}
    rcv_par_blk = {}
    rcv_par_list = {}
    rcv_err_blk = {}

    # Tracking common special signals that are used for multiple signals
    drv_fierr_map = {}  # might be shared across multiple row

    # List of things
    original_inport_drv = {}
    original_outport_drv = {}
    extra_inport_drv = {}
    extra_outport_drv = {}

    original_inport_rcv = {}
    original_outport_rcv = {}
    extra_inport_rcv = {}
    extra_outport_rcv = {}

    err_list = {}   # might be shared across multiple row

    def __init__(self, Parity_INFOExtractor: ExtractINFO_Parity_Signal):
        # Info read from INFO file
        self.drv_port, self.drv_par_port = Parity_INFOExtractor._extract_parity_signals_drv()
        self.rcv_port, self.rcv_par_port = Parity_INFOExtractor._extract_parity_signals_rcv()
        self.bit_width, self.par_width = Parity_INFOExtractor._extract_dimension()
        self.clk_drv, self.rst_drv = Parity_INFOExtractor._extract_driver_clock_reset()
        self.clk_rcv, self.rst_rcv = Parity_INFOExtractor._extract_receiver_clock_reset()
        self.fault_list = Parity_INFOExtractor._extract_fault_injection()
        self.drv_name = Parity_INFOExtractor._extract_drv_name()
        self.rcv_name = Parity_INFOExtractor._extract_rcv_name()
        self.signal_valid_name = Parity_INFOExtractor._extract_signal_valid_name()
        self.rcv_err_port, self.rcv_err_dup = Parity_INFOExtractor._extract_error_port_rcv()
        # Share across multiple rows
        self._init_generator()

    # --------------------------------------------
    # DRIVER
    # --------------------------------------------
    def _generate_parity_drv(self):
        parity_blk = ""

        sliced_dimension = split_dimension(self.bit_width, self.par_width)
        # for i, sliced in enumerate(sliced_dimension):
        #     parity_blk += f"\nassign {self.drv_par_port}[{i}] = (^(w_{self.drv_port}{sliced}));"

        parity_blk += f"\nreg [{len(sliced_dimension) - 1}:0] r_{self.drv_par_port};"
        parity_blk += (f"\nalways@(posedge {self.clk_drv} or negedge {self.rst_drv}) begin"
                       f"\n    if (!{self.rst_drv}) begin")
        for i, sliced in enumerate(sliced_dimension):
            parity_blk += f"\n        r_{self.drv_par_port}[{i}] <= 0;"
        parity_blk += "\n    end else begin"
        
        if self.signal_valid_name:
            # Generate parity only when signal_valid is 1, else 0
            for i, sliced in enumerate(sliced_dimension):
                parity_blk += f"\n        r_{self.drv_par_port}[{i}] <= {self.signal_valid_name} ? (^w_{self.drv_port}{sliced}) : 1'b0;"
        else:
            # Original behavior without SIGNAL VALID NAME
            for i, sliced in enumerate(sliced_dimension):
                parity_blk += f"\n        r_{self.drv_par_port}[{i}] <= ^w_{self.drv_port}{sliced};"
        
        parity_blk += ("\n    end"
                       "\nend")

        parity_blk += f"\nassign {self.drv_par_port} = r_{self.drv_par_port};"

        return parity_blk + "\n"

    def _generate_port_drv(self):
        port_blk = ""
        port_blk += f"\n    input  [{self.bit_width}-1:0] {self.drv_port},"
        port_blk += f"\n    output [{self.bit_width//self.par_width}-1:0] {self.drv_par_port},"
        return port_blk

    def _generate_wire_drv(self):
        port_blk = f"\nreg [{self.bit_width}-1:0] w_{self.drv_port};"
        return port_blk

    # --------------------------------------------
    # RECEIVER
    # --------------------------------------------
    def _assign_signal(self) -> str:
        signal_assign_blk = f"\n    w_{self.drv_port} = {self.drv_port};"
        return signal_assign_blk

    def _inject_error(self):
        fault_inj, fault_sig_list = self.fault_list

        fault_inj_blk = ""
        if self.fault_list:
            fault_inj_blk += f"\n    if (r_{fault_inj}) begin"

            for fault_sig in fault_sig_list:
                fault_sig_split = fault_sig.split("[")
                fault_sig_name = fault_sig_split[0]
                fault_sig_dim  = "[" + fault_sig_split[1]

                assert fault_sig_name == self.drv_port, "Port name and Error port name don't match."

                fault_inj_blk += f"\n        w_{fault_sig_name}{fault_sig_dim} = ~{fault_sig_name}{fault_sig_dim};"

            fault_inj_blk += f"\n    end"

        return fault_inj_blk

    def _generate_port_rcv(self):
        port_blk = ""
        # clk, rst
        if self.rcv_port:
            port_blk += f"\n    input  [{self.bit_width}-1:0] {self.rcv_port},"
        if self.rcv_par_port:
            port_blk += f"\n    input  [{self.par_width}-1:0] {self.rcv_par_port},"
        return port_blk

    def _generate_port_err(self, rcv_name: str):
        port_blk = ""

        for rcv_err_port in GenerateParity.err_list[rcv_name]:
            if rcv_err_port.endswith("_dup"):
                error_port = rcv_err_port[:-4]
                port_blk += f"\n    output {error_port},"
                port_blk += f"\n    output {error_port}_B,"
            else:
                error_port = rcv_err_port
                port_blk += f"\n    output {error_port},"

        return port_blk

    def _generate_parity_rcv(self):
        parity_blk = ""
        sliced_dimension = split_dimension(self.bit_width, self.par_width)
        parity_blk += generate_synchronizer(self.clk_rcv, self.rst_rcv, self.rcv_port, len(sliced_dimension))
        for i in range(len(sliced_dimension)):
            parity_blk += f"\nwire w_{self.rcv_port}_parity_{i};"
        parity_blk += "\n"

        if self.signal_valid_name:
            # Gate data with SIGNAL VALID NAME before calculating parity
            parity_blk += f"wire [{self.bit_width}-1:0] w_{self.rcv_port}_gated = {self.signal_valid_name} ? r_{self.rcv_port} : {self.bit_width}'b0;"
            parity_blk += "\n"
            for i, sliced in enumerate(sliced_dimension):
                parity_blk += f"\nassign w_{self.rcv_port}_parity_{i} = ^w_{self.rcv_port}_gated{sliced};"
        else:
            # Original behavior without SIGNAL VALID NAME
            for i, sliced in enumerate(sliced_dimension):
                parity_blk += f"\nassign w_{self.rcv_port}_parity_{i} = ^r_{self.rcv_port}{sliced};"

        parity_blk += "\n"
        return parity_blk

    def _generate_error_check(self):
        err_blk = ""
        err_blk += f"\nwire w_AnyError_{self.rcv_port};"

        sliced_dimension = split_dimension(self.bit_width, self.par_width)
        err_blk += f"\nassign w_AnyError_{self.rcv_port} = ("
        for i in range(len(sliced_dimension)):
            err_blk += f"\n    (w_{self.rcv_port}_parity_{i} ^ {self.rcv_par_port}[{i}]) |"

        err_blk = err_blk[:-1] + "\n);\n"

        GenerateParity.rcv_par_list[self.rcv_name].append(f"w_AnyError_{self.rcv_port}")
        return err_blk

    def _generate_error(self, rcv_name: str, clk_rcv: str, rst_rcv: str):
        err_blk = ""

        for rcv_err_port in GenerateParity.err_list[rcv_name]:
            if rcv_err_port.endswith("_dup"):
                error_port = rcv_err_port[:-4]
            else:
                error_port = rcv_err_port
            err_blk += f"wire w_AnyError_{error_port};"
            err_blk += f"\nassign w_AnyError_{error_port} ="
            for error_signal in GenerateParity.err_list[rcv_name][rcv_err_port]:
                err_blk += f" {error_signal} |"

            err_blk = err_blk[:-2] + ";\n"
            err_blk += self._generate_filter(error_port)
            err_blk += f"\nassign {error_port} = r_{error_port}_filtered;"
            if rcv_err_port.endswith("_dup"):
                err_blk += f"\nassign {error_port}_B = ~r_{error_port}_filtered;"

        return err_blk

    def _generate_filter(self, rcv_port: str, level=5):
        filter_blk = ""
        filter_blk += (f"\nreg [{level-1}:0] r_{rcv_port}_filter;"
                       f"\nreg r_{rcv_port}_filtered;")
        filter_blk += (f"\nalways@(posedge {self.clk_rcv} or negedge {self.rst_rcv}) begin"
                       f"\n    if (!{self.rst_rcv}) begin"
                       f"\n        r_{rcv_port}_filter <= 0;"
                       f"\n        r_{rcv_port}_filtered <= 0;"
                       f"\n    end else begin"
                       f"\n        r_{rcv_port}_filter <= {{r_{rcv_port}_filter[{level-2}:0], w_AnyError_{rcv_port}}};"
                       f"\n        if (&r_{rcv_port}_filter)"
                       f"\n            r_{rcv_port}_filtered <= 1'b1;"
                       # f"\n        else if (~|r_{self.rcv_port}_filter)"
                       # f"\n            r_{self.rcv_port}_filtered <= 1'b0;"
                       f"\n    end"
                       f"\nend")
        return filter_blk

    # --------------------------------------------
    # WRAPPER
    # --------------------------------------------
    # This should be run once for each row
    def _wrapper_drv(self) -> None:
        GenerateParity.drv_port_blk[self.drv_name] += self._generate_port_drv()
        GenerateParity.drv_wire_blk[self.drv_name] += self._generate_wire_drv()
        GenerateParity.drv_sig_assign[self.drv_name] += self._assign_signal()
        GenerateParity.drv_par_blk[self.drv_name] += self._generate_parity_drv()
        # NOTE: Fault injection disabled for driver signals - only kept for receiver signals

    def _list_port_drv(self):
        port_list = {}
        for drv_name in GenerateParity.drv_set:
            original_inport  = list(set(tuple(lst) for lst in GenerateParity.original_inport_drv[drv_name]))
            original_outport = list(set(tuple(lst) for lst in GenerateParity.original_outport_drv[drv_name]))
            extra_inport     = list(set(tuple(lst) for lst in GenerateParity.extra_inport_drv[drv_name]))
            extra_outport    = list(set(tuple(lst) for lst in GenerateParity.extra_outport_drv[drv_name]))
            port_list[drv_name] = original_inport, original_outport, extra_inport, extra_outport
        return port_list

    # This should be run once for each row
    def _wrapper_rcv(self) -> None:
        GenerateParity.rcv_port_blk[self.rcv_name] += self._generate_port_rcv()
        GenerateParity.rcv_par_blk[self.rcv_name] += self._generate_parity_rcv()
        GenerateParity.rcv_err_blk[self.rcv_name] += self._generate_error_check()

    def _list_port_rcv(self):
        port_list = {}
        for rcv_name in GenerateParity.rcv_set:
            original_inport  = list(set(tuple(lst) for lst in GenerateParity.original_inport_rcv[rcv_name]))
            original_outport = list(set(tuple(lst) for lst in GenerateParity.original_outport_rcv[rcv_name]))
            extra_inport     = list(set(tuple(lst) for lst in GenerateParity.extra_inport_rcv[rcv_name]))
            extra_outport    = list(set(tuple(lst) for lst in GenerateParity.extra_outport_rcv[rcv_name]))
            port_list[rcv_name] = original_inport, original_outport, extra_inport, extra_outport
        return port_list

    # This should be run once for each Driver
    def _generate_module_drv(self):
        module_blk = ""
        for drv_name in GenerateParity.drv_set:
            clk = GenerateParity.drv_clk_rst_blk[drv_name].get('clk')
            rst = GenerateParity.drv_clk_rst_blk[drv_name].get('rst')

            module_blk += "`timescale 1ns / 1ps\n\n"
            # Add MD5 and version header
            if GenerateParity.md5_hash:
                module_blk += f"// MD5@INFO : {GenerateParity.md5_hash}\n"
                module_blk += f"// Version@Script : {GenerateParity.script_version}\n"
            module_blk += f"module {drv_name}_SIGNAL_PARITY_GEN ("
            module_blk += f"\n    input {clk}, {rst},"
            # NOTE: Fault injection disabled for driver signals - fierr ports removed
            # for fierr, _ in GenerateParity.drv_fierr_map[drv_name].items():
            #     module_blk += f"\n    input {fierr},"
            module_blk += GenerateParity.drv_port_blk[drv_name]
            module_blk = module_blk[:-1] + "\n);\n"

            module_blk += GenerateParity.drv_wire_blk[drv_name]
            # NOTE: Fault injection disabled for driver signals - synchronizer for fierr removed
            # for fierr, _ in GenerateParity.drv_fierr_map[drv_name].items():
            #     module_blk += generate_synchronizer(clk=clk, rst=rst, signal=fierr)
            module_blk += "\nalways@(*) begin"
            module_blk += GenerateParity.drv_sig_assign[drv_name]
            # NOTE: Fault injection disabled for driver signals - fault injection logic removed
            # module_blk += GenerateParity.fault_inj_blk[drv_name]
            module_blk += "\nend\n"
            module_blk += GenerateParity.drv_par_blk[drv_name]
            module_blk += "\nendmodule\n\n"

        return module_blk

    # This should be run once for each Receiver
    def _generate_module_rcv(self):
        module_blk = ""
        for rcv_name in GenerateParity.rcv_set:
            clk = GenerateParity.rcv_clk_rst_blk[rcv_name].get('clk')
            rst = GenerateParity.rcv_clk_rst_blk[rcv_name].get('rst')
            module_blk += "`timescale 1ns / 1ps\n\n"
            # Add MD5 and version header
            if GenerateParity.md5_hash:
                module_blk += f"// MD5@INFO : {GenerateParity.md5_hash}\n"
                module_blk += f"// Version@Script : {GenerateParity.script_version}\n"
            module_blk += f"module {rcv_name}_SIGNAL_PARITY_GEN ("
            module_blk += f"\n    input {clk}, {rst},"
            module_blk += GenerateParity.rcv_port_blk[rcv_name]
            module_blk += self._generate_port_err(rcv_name)
            module_blk = module_blk[:-1] + "\n);\n"

            module_blk += GenerateParity.rcv_par_blk[rcv_name]
            module_blk += GenerateParity.rcv_err_blk[rcv_name]
            module_blk += self._generate_error(rcv_name, clk, rst)
            module_blk += "\nendmodule\n\n"

        return module_blk

    # This should be run after finish generating
    def _reset_generator(self):
        # Drv
        GenerateParity.drv_clk_rst_blk = {}
        GenerateParity.drv_port_blk = {}
        GenerateParity.drv_wire_blk = {}
        GenerateParity.drv_sig_assign = {}
        GenerateParity.drv_par_blk = {}
        GenerateParity.fault_inj_blk = {}
        # Port list
        GenerateParity.original_inport_drv = []
        GenerateParity.original_outport_drv = []
        GenerateParity.extra_inport_drv = []
        GenerateParity.extra_outport_drv = []

        # Rcv
        GenerateParity.rcv_clk_rst_blk = {}
        GenerateParity.rcv_port_blk = {}
        GenerateParity.rcv_par_blk = {}
        GenerateParity.rcv_par_list = {}
        GenerateParity.rcv_err_blk = {}
        # Port list
        GenerateParity.original_inport_rcv = []
        GenerateParity.original_outport_rcv = []
        GenerateParity.extra_inport_rcv = []
        GenerateParity.extra_outport_rcv = []

        GenerateParity.drv_fierr_map = {}
        GenerateParity.err_list = {}

    # This should be run before starting generating
    def _init_generator(self):
        # Driver
        if self.drv_name not in GenerateParity.drv_set:
            # Keep track of driver list
            GenerateParity.drv_set.add(self.drv_name)
            # Port list
            GenerateParity.original_inport_drv[self.drv_name] = [["", self.clk_drv, ""], ["", self.rst_drv, ""]]
            GenerateParity.original_outport_drv[self.drv_name] = []
            GenerateParity.extra_inport_drv[self.drv_name] = []
            GenerateParity.extra_outport_drv[self.drv_name] = []
            # Init driver ...
            GenerateParity.drv_clk_rst_blk[self.drv_name] = {"clk": self.clk_drv, "rst": self.rst_drv}
            GenerateParity.drv_port_blk[self.drv_name] = ""
            GenerateParity.drv_wire_blk[self.drv_name] = ""
            GenerateParity.drv_sig_assign[self.drv_name] = ""
            GenerateParity.drv_par_blk[self.drv_name] = ""
            GenerateParity.fault_inj_blk[self.drv_name] = ""

            GenerateParity.drv_fierr_map[self.drv_name] = {}
        # NOTE: Fault injection disabled for driver signals - fierr port not added to driver
        # if self.fault_list:
        #     try:
        #         GenerateParity.drv_fierr_map[self.drv_name][self.fault_list[0]].add({self.drv_port})
        #     except:
        #         GenerateParity.drv_fierr_map[self.drv_name][self.fault_list[0]] = {self.drv_port}

        GenerateParity.original_outport_drv[self.drv_name].append([f"[{self.bit_width}-1:0]", self.drv_port, ""])
        GenerateParity.extra_outport_drv[self.drv_name].append([f"[{self.bit_width//self.par_width}-1:0]", self.drv_par_port, ""])
        # NOTE: Fault injection disabled for driver signals - fierr port not added to driver
        # GenerateParity.extra_inport_drv[self.drv_name].append([f"", self.fault_list[0], ""])
        
        # Add SIGNAL VALID NAME port if specified
        if self.signal_valid_name:
            GenerateParity.extra_inport_drv[self.drv_name].append([f"", self.signal_valid_name, ""])

        # Receiver
        if self.rcv_name not in GenerateParity.rcv_set:
            # Keep track of receiver list
            GenerateParity.rcv_set.add(self.rcv_name)
            # Port list
            GenerateParity.original_inport_rcv[self.rcv_name] = [["", self.clk_rcv, ""], ["", self.rst_rcv, ""]]
            GenerateParity.original_outport_rcv[self.rcv_name] = []
            GenerateParity.extra_inport_rcv[self.rcv_name] = []
            GenerateParity.extra_outport_rcv[self.rcv_name] = []
            # Init receiver ...
            GenerateParity.rcv_clk_rst_blk[self.rcv_name] = {"clk": self.clk_rcv, "rst": self.rst_rcv}
            GenerateParity.rcv_port_blk[self.rcv_name] = ""
            GenerateParity.rcv_par_blk[self.rcv_name] = ""
            GenerateParity.rcv_par_list[self.rcv_name] = []
            GenerateParity.rcv_err_blk[self.rcv_name] = ""

            GenerateParity.err_list[self.rcv_name] = {}
        if self.rcv_err_port:
            if self.rcv_err_dup:
                try:
                    GenerateParity.err_list[self.rcv_name][f"{self.rcv_err_port}_dup"].add(f"w_AnyError_{self.rcv_port}")
                except:
                    GenerateParity.err_list[self.rcv_name][f"{self.rcv_err_port}_dup"] = {f"w_AnyError_{self.rcv_port}"}
            else:
                try:
                    GenerateParity.err_list[self.rcv_name][self.rcv_err_port].add(f"w_AnyError_{self.rcv_port}")
                except:
                    GenerateParity.err_list[self.rcv_name][self.rcv_err_port] = {f"w_AnyError_{self.rcv_port}"}

        GenerateParity.original_inport_rcv[self.rcv_name].append([f"[{self.bit_width}-1:0]", self.rcv_port, ""])
        GenerateParity.extra_inport_rcv[self.rcv_name].append([f"[{self.par_width}-1:0]", self.rcv_par_port, ""])
        GenerateParity.extra_outport_rcv[self.rcv_name].append(["", self.rcv_err_port, ""])
        if self.rcv_err_dup:
            GenerateParity.extra_outport_rcv[self.rcv_name].append(["", f"{self.rcv_err_port}_B", ""])
        
        # Add SIGNAL VALID NAME port if specified
        if self.signal_valid_name:
            GenerateParity.extra_inport_rcv[self.rcv_name].append([f"", self.signal_valid_name, ""])


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
        sync_blk += f"\nreg [{size}-1:0] r_{signal};"
    sync_blk += (f"\nBOS_SOC_SYNCHSR u_bos_synch_{signal} ("
                 f"\n    .I_CLK ({clk}),"
                 f"\n    .I_RESETN ({rst}),"
                 f"\n    .I_D ({signal}),"
                 f"\n    .O_Q (r_{signal})"
                 f"\n);\n")
    return sync_blk


