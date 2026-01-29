import re

from DCLS_generator.GenerateVerilog.GenerateVerilog import GenerateVerilog
from DCLS_generator.ClassExtractINFO.ExtractINFO_Parity.ExtractINFO_Parity_Register import ExtractINFO_Parity_Register
from DCLS_generator.instanceModifier.modify_instance import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class GenerateRegister(GenerateVerilog):
    safety_scheme = 'Parity Register'
    ip_set = set()

    par_wire_blk = {}
    par_reg_blk = {}
    par_err_blk = {}

    reg_port_blk = {}
    valid_blk = {}

    # Tracking common special signals that are used for multiple signals
    reg_fierr_map = {}
    ip_sig_assign = {}
    fault_inj_blk = {}
    reg_err_port_blk = {}

    # List of things
    original_inport = {}
    extra_inport = {}
    extra_outport = {}

    reg_par_list = {}
    reg_clk_rst_list = {}
    is_error_dup = {}

    def __init__(self, Parity_INFOExtractor: ExtractINFO_Parity_Register):
        # Info read from INFO file
        self.reg_name, self.reg_par_name = Parity_INFOExtractor._extract_reg()
        self.bit_width, self.par_width = Parity_INFOExtractor._extract_dimension()
        self.clk, self.rst = Parity_INFOExtractor._extract_register_clk_rst()

        self.fault_list = Parity_INFOExtractor._extract_fault_injection()

        self.ip_name = Parity_INFOExtractor._extract_ip_name()
        self.val_sig, self.reg_sig = Parity_INFOExtractor._extract_signal()
        self.signal_valid_name = Parity_INFOExtractor._extract_signal_valid_name()
        self.reg_err_port, self.reg_err_dup = Parity_INFOExtractor._extract_err_port_reg()
        self.is_even = Parity_INFOExtractor._is_even()
        # Share across multiple rows
        self._init_generator()

    def _generate_port(self, ip_name: str):
        port_blk = ""

        original_inport = list(set(tuple(lst) for lst in GenerateRegister.original_inport[ip_name]))
        for port in original_inport:
            port_blk += f"\n    input {port[0]}  {port[1]} {port[2]},"
        return port_blk

    def _generate_port_err(self):
        port_blk = ""
        if self.reg_err_port:
            port_blk += f"\n    output  {self.reg_err_port},"
            if self.reg_err_dup:
                port_blk += f"\n    output  {self.reg_err_port}_B,"
        return port_blk

    def _generate_valid(self):
        valid_blk = ""
        valid_blk += (f"\nwire {self.reg_name}_valid;"
                      f"\nassign {self.reg_name}_valid = {self.val_sig};")
        return valid_blk

    def _generate_parity_wire(self):
        parity_blk = ""

        sliced_dimension = split_dimension(self.bit_width, self.par_width)

        parity_blk += f"\nwire [{len(sliced_dimension)}-1:0] w_{self.reg_name}_par;"
        parity_blk += "\n"

        if self.signal_valid_name:
            # Gate data with SIGNAL VALID NAME before calculating parity
            parity_blk += f"wire [{self.bit_width}-1:0] w_{self.reg_name}_gated = {self.signal_valid_name} ? {self.reg_name} : {self.bit_width}'b0;"
            parity_blk += "\n"
            for i, sliced in enumerate(sliced_dimension):
                parity_blk += f"\nassign w_{self.reg_name}_par[{i}] = ^w_{self.reg_name}_gated{sliced};"
        else:
            # Original behavior without SIGNAL VALID NAME
            for i, sliced in enumerate(sliced_dimension):
                parity_blk += f"\nassign w_{self.reg_name}_par[{i}] = ^{self.reg_name}{sliced};"

        parity_blk += "\n"
        return parity_blk

    def _generate_parity_reg(self):
        parity_blk = ""

        sliced_dimension = split_dimension(self.bit_width, self.par_width)

        parity_blk += f"\nreg [{len(sliced_dimension)}-1:0] {self.reg_par_name};"
        parity_blk += "\n"

        parity_blk += (f"\nalways@(posedge {self.clk} or negedge {self.rst}) begin"
                       f"\n    if (!{self.rst})"
                       f"\n        {self.reg_par_name} <= 0;"
                       f"\n    else if ({self.reg_name}_valid) begin")
        
        if self.signal_valid_name:
            # Generate parity only when signal_valid is 1, else 0
            for i, sliced in enumerate(sliced_dimension):
                parity_blk += f"\n        {self.reg_par_name}[{i}] <= {self.signal_valid_name} ? (^{self.reg_sig}{sliced}) : 1'b0;"
        else:
            # Original behavior without SIGNAL VALID NAME
            for i, sliced in enumerate(sliced_dimension):
                parity_blk += f"\n        {self.reg_par_name}[{i}] <= ^{self.reg_sig}{sliced};"
        
        parity_blk += "\n    end\nend"

        parity_blk += "\n"
        return parity_blk

    def _assign_signal(self) -> str:
        sliced_dimension = split_dimension(self.bit_width, self.par_width)
        signal_assign_blk = f"\nwire [{len(sliced_dimension)}-1:0] w_{self.reg_par_name};"
        signal_assign_blk += f"\nassign w_{self.reg_par_name} = {self.reg_par_name};"
        return signal_assign_blk

    def _inject_error(self):
        fault_inj, fault_sig_list = self.fault_list

        fault_inj_blk = ""
        if self.fault_list:
            for fault_sig in fault_sig_list:
                fault_sig_split = fault_sig.split("[")
                fault_sig_name = fault_sig_split[0]
                fault_sig_dim  = "[" + fault_sig_split[1]

                assert fault_sig_name == self.reg_par_name, f"Reg name and Error name don't match {fault_sig_name} vs {self.reg_par_name}."

                fault_inj_blk += f"\nassign w_{fault_sig_name}{fault_sig_dim} = r_{fault_inj} ? ~{fault_sig_name}{fault_sig_dim} : {fault_sig_name}{fault_sig_dim};"

        return fault_inj_blk


    def _generate_error_check(self):
        err_blk = ""
        err_blk += f"\nwire w_AnyError_{self.reg_name};"
        err_blk += f"\nassign w_AnyError_{self.reg_name} = ("
        
        sliced_dimension = split_dimension(self.bit_width, self.par_width)
        for i, sliced in enumerate(sliced_dimension):
            err_blk += f"\n    (w_{self.reg_par_name}[{i}] ^ w_{self.reg_name}_par[{i}]) |"
        err_blk = err_blk[:-1] + "\n);"

        GenerateRegister.reg_par_list[self.ip_name][self.reg_err_port].append(f"w_AnyError_{self.reg_name}")
        return err_blk, [err_blk]

    def _generate_error(self, ip_name: str, clk: str, rst: str, is_err_dup: bool):
        err_blk = ""
        for error in GenerateRegister.reg_par_list[ip_name]:
            err_blk += f"\nwire w_AnyError_{error};"
            err_blk += f"\nassign w_AnyError_{error} ="
            for anyerror in GenerateRegister.reg_par_list[ip_name][error]:
                err_blk += f" {anyerror} |"
            err_blk = err_blk[:-2] + ";\n"

            err_blk += f"\nreg r_{error};"
            err_blk += (f"\nalways@(posedge {clk} or negedge {rst}) begin"
                        f"\n    if (!{rst}) begin"
                        f"\n        r_{error} <= 1'b0;"
                        f"\n    end else begin"
                        f"\n        r_{error} <= w_AnyError_{error};"
                        f"\n    end"
                        f"\nend")

            err_blk += f"\nassign {error} = r_{error};"
            if is_err_dup:
                err_blk += f"\nassign {error}_B = ~r_{error};"

        return err_blk

    # Wrapper
    def _list_port(self):
        port_list = {}
        for ip_name in GenerateRegister.ip_set:
            original_inport = list(set(tuple(lst) for lst in GenerateRegister.original_inport[ip_name]))
            extra_inport  = list(set(tuple(lst) for lst in GenerateRegister.extra_inport[ip_name]))
            extra_outport = list(set(tuple(lst) for lst in GenerateRegister.extra_outport[ip_name]))
            port_list[ip_name] = original_inport, extra_inport, extra_outport
        return port_list

    # Assuming regs are different
    def _generate_module_reg(self):
        module_blk = ""
        for ip_name in GenerateRegister.ip_set:
            clk = GenerateRegister.reg_clk_rst_list[ip_name].get('clk')
            rst = GenerateRegister.reg_clk_rst_list[ip_name].get('rst')

            module_blk += f"module {ip_name}_REG_PARITY_GEN ("
            # module_blk += f"\n    input {clk}, {rst},"
            module_blk += self._generate_port(ip_name)
            for fierr, _ in GenerateRegister.reg_fierr_map[ip_name].items():
                module_blk += f"\n    input {fierr},"
            for ip_err_port in GenerateRegister.reg_par_list[ip_name]:
                module_blk += GenerateRegister.reg_err_port_blk[ip_err_port]
            # module_blk += GenerateRegister.reg_port_blk[ip_name]
            module_blk = module_blk[:-1] + "\n);\n"

            module_blk += GenerateRegister.par_wire_blk[ip_name] + "\n"
            module_blk += GenerateRegister.par_reg_blk[ip_name] + "\n"
            for fierr, _ in GenerateRegister.reg_fierr_map[ip_name].items():
                module_blk += generate_synchronizer(clk=clk, rst=rst, signal=fierr)
            module_blk += GenerateRegister.ip_sig_assign[ip_name]
            module_blk += GenerateRegister.fault_inj_blk[ip_name]

            # par_err_blk = list(set(tuple(lst) for lst in GenerateRegister.par_err_blk[ip_name]))
            par_err_blk = list(set(GenerateRegister.par_err_blk[ip_name]))
            module_blk += "".join(par_err_blk)
            # module_blk += GenerateRegister.par_err_blk[ip_name]
            module_blk += self._generate_error(ip_name, clk, rst, GenerateRegister.is_error_dup[self.ip_name])

            module_blk += "\nendmodule\n\n"

        return module_blk

    def _wrapper_reg(self) -> None:
        GenerateRegister.par_wire_blk[self.ip_name] += self._generate_parity_wire()
        GenerateRegister.par_reg_blk[self.ip_name] += self._generate_parity_reg()
        # GenerateRegister.par_err_blk[self.ip_name] += self._generate_error_check()[0]
        GenerateRegister.par_err_blk[self.ip_name] += self._generate_error_check()[1]
        # GenerateRegister.reg_port_blk[self.ip_name] += self._generate_port()
        GenerateRegister.ip_sig_assign[self.ip_name] += self._assign_signal()
        GenerateRegister.fault_inj_blk[self.ip_name] += self._inject_error()
        GenerateRegister.valid_blk[self.ip_name] += self._generate_valid()

    # This should be run after finish generating
    def _reset_generator(self) -> None:
        GenerateRegister.ip_set = set()
        GenerateRegister.reg_par_list = {}
        # Port list
        GenerateRegister.original_inport = []
        GenerateRegister.extra_inport = []
        GenerateRegister.extra_outport = []

        GenerateRegister.reg_port_blk = {}
        GenerateRegister.reg_err_port_blk = {}
        GenerateRegister.valid_blk = {}

        GenerateRegister.par_wire_blk = {}
        GenerateRegister.par_reg_blk = {}
        GenerateRegister.par_err_blk = {}

        GenerateRegister.reg_fierr_map = {}
        GenerateRegister.ip_sig_assign = {}
        GenerateRegister.fault_inj_blk = {}
        GenerateRegister.reg_clk_rst_list = {}
        GenerateRegister.is_error_dup = {}

    # This should be run before starting generating
    def _init_generator(self) -> None:
        if self.ip_name not in GenerateRegister.ip_set:
            # Keep track of IP list
            GenerateRegister.ip_set.add(self.ip_name)
            GenerateRegister.is_error_dup[self.ip_name] = self.reg_err_dup
            GenerateRegister.reg_par_list[self.ip_name] = {}
            GenerateRegister.reg_clk_rst_list[self.ip_name] = {"clk": self.clk, "rst": self.rst}
            # Port list
            GenerateRegister.original_inport[self.ip_name] = [["", self.clk, ""], ["", self.rst, ""]]
            GenerateRegister.extra_inport[self.ip_name] = []
            GenerateRegister.extra_outport[self.ip_name] = []

            GenerateRegister.par_wire_blk[self.ip_name] = ""
            GenerateRegister.par_reg_blk[self.ip_name] = ""
            # GenerateRegister.par_err_blk[self.ip_name] = ""
            GenerateRegister.par_err_blk[self.ip_name] = []

            GenerateRegister.reg_port_blk[self.ip_name] = ""
            GenerateRegister.valid_blk[self.ip_name] = ""

            GenerateRegister.reg_fierr_map[self.ip_name] = {}
            GenerateRegister.ip_sig_assign[self.ip_name] = ""
            GenerateRegister.fault_inj_blk[self.ip_name] = ""

        if self.fault_list:
            try:
                GenerateRegister.reg_fierr_map[self.ip_name][self.fault_list[0]].add({self.reg_par_name})
            except:
                GenerateRegister.reg_fierr_map[self.ip_name][self.fault_list[0]] = {self.reg_par_name}

        GenerateRegister.extra_outport[self.ip_name].append([f"", self.reg_err_port, ""])
        if self.reg_err_dup:
            GenerateRegister.extra_outport[self.ip_name].append([f"", f"{self.reg_err_port}_B", ""])
        GenerateRegister.extra_inport[self.ip_name].append([f"", self.fault_list[0], ""])
        GenerateRegister.original_inport[self.ip_name].append([f"[{self.bit_width-1}:0]", self.reg_name, ""])
        GenerateRegister.original_inport[self.ip_name].append([f"[{self.bit_width-1}:0]", self.reg_sig, ""])
        GenerateRegister.original_inport[self.ip_name].append([f"", f"{self.reg_name}_valid", ""])
        
        # Add SIGNAL VALID NAME port if specified
        if self.signal_valid_name:
            GenerateRegister.extra_inport[self.ip_name].append([f"", self.signal_valid_name, ""])

        if self.reg_err_port:
            try:
                GenerateRegister.reg_par_list[self.ip_name][self.reg_err_port]
            except:
                GenerateRegister.reg_par_list[self.ip_name][self.reg_err_port] = []
                GenerateRegister.reg_err_port_blk[self.reg_err_port] = self._generate_port_err()


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


def convert_condition_to_signal(condition):
    # Define a regex pattern for special characters
    pattern = r'[=\+\-&|]'
    # Replace all special characters with an underscore
    result = re.sub(pattern, '_', condition)
    return result


