import re
import itertools
from typing import Optional

from Parity_generator.ClassExtractINFO.ExtractINFO_DCLS import ExtractINFO_DCLS
from Parity_generator.GenerateVerilog.GenerateVerilog import GenerateVerilog
from Parity_generator.ClassStats.StatsClass import StatsClass

from Parity_generator.moduleParser.extract_list_multipurpose import is_tie_float


class GenerateDCLS(GenerateVerilog):
    safety_scheme = 'DCLS'

    def __init__(self, ip_name: str, param_list: list, clk_rst_list: list, inport_list: list, outport_list: list, DCLS_INFOExtractor: ExtractINFO_DCLS):
        super().__init__(ip_name, param_list, clk_rst_list, inport_list, outport_list)
        self.ignore_list = DCLS_INFOExtractor._extract_ignore_list()
        self.fault_list = DCLS_INFOExtractor._extract_fault_injection()
        self.gate_dict, self.gated_list, self.gate_dict_d1 = DCLS_INFOExtractor._extract_gate_list()
        self.default_dict = DCLS_INFOExtractor._extract_default_list()
        self.valid_list_d1 = extract_valids_from_dict(self.gate_dict_d1)
        self.gate_dict_size = create_lookup_dict(self.inport_list + self.outport_list)
        self.merge_gate_dict = merge_gate_dict(self.gate_dict, self.gate_dict_d1)
        self.ignore_err_list = [port for port in self.ignore_list if not check_for_value_in_dict(port, self.merge_gate_dict)]
        self.dup_error = DCLS_INFOExtractor._is_error_double()
        self.ip_err_port, self.dup_err_port = DCLS_INFOExtractor._extract_err_port()

        self._verify_user_port()

    # Inherited methods
    # All additional arguments are for FLAT mode
    def _generate_wire(self, StatsAnalyzer: Optional[StatsClass] = None, port_sig_dict=None) -> str:
        self.port_list = [port for port in self.outport_list if port[1] not in self.ignore_list]
        self.port_list = self.outport_list
        if StatsAnalyzer:
            self.port_list = super()._convert_dimension_to_number(StatsAnalyzer)
        return super()._generate_wire(port_sig_dict)

    def _generate_reg(self, StatsAnalyzer: Optional[StatsClass] = None, level=2, port_sig_dict=None) -> str:
        reg_blk = ''
        if port_sig_dict is None:
            port_sig_dict = {}

        # self.port_list = self.inport_list
        self.port_list = [port for port in self.inport_list if port[1] not in self.ignore_list]
        if StatsAnalyzer:
            self.port_list = super()._convert_dimension_to_number(StatsAnalyzer)
        reg_blk += super()._generate_reg(level, port_sig_dict)

        # self.port_list = self.outport_list
        # self.port_list = [port for port in self.outport_list if port[1] not in self.ignore_list]
        self.port_list = [port for port in self.outport_list if port[1] not in self.ignore_err_list]
        for p in self.port_list:
            check_for_value_in_dict(p[1], self.merge_gate_dict)
        # self.port_list = self.outport_list  # even though excluded from comparison, they might still be used as valid signals
        if StatsAnalyzer:
            self.port_list = super()._convert_dimension_to_number(StatsAnalyzer)
        reg_blk += super()._generate_reg(level, port_sig_dict)

        return reg_blk

    def _generate_delay(self, level=2, port_sig_dict=None):
        delay_blk = ''
        level = 2   # For now, this is fixed at 2

        ungate_parsed_inport = [port for port in self.inport_list if port[1] not in self.gated_list]
        ungate_parsed_outport = [port for port in self.outport_list if port[1] not in self.gated_list]

        self.port_list = [port for port in ungate_parsed_inport if port[1] not in self.ignore_list]
        if self.port_list:
            delay_blk += super()._generate_delay(level, port_sig_dict)

        # self.port_list = [port for port in ungate_parsed_outport if port[1] not in self.ignore_list]
        self.port_list = [port for port in ungate_parsed_outport if port[1] not in self.ignore_err_list]
        if not self.port_list:
            print("Empty outport list")
        if self.port_list:
            delay_blk += super()._generate_delay(level, port_sig_dict, self.default_dict)

        delay_blk += self._generate_gated_delay(port_sig_dict)

        return delay_blk

    #[TODO] Add loop for different delay level (similar to GenerateVerilog)
    def _generate_gated_delay(self, port_sig_dict=None):
        if port_sig_dict is None:
            port_sig_dict = {}
        gate_block = ""

        # Gated that is not delayed
        for key, value_list in self.gate_dict.items():
            gate_block += f"always @(posedge {port_sig_dict.get(self.clk_rcv, self.clk_rcv)} or negedge {port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
            gate_block += f"\t if (!{port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
            for value in value_list:
                reset_value = self.default_dict.get(value, "'d0")
                gate_block += f"\t\tr_{value}_sliced_d1 <= {reset_value};\n"
            gate_block += f"\tend else if ({port_sig_dict.get(key, key)}) begin\n"
            for value in value_list:
                gate_block += f"\t\tr_{value}_sliced_d1 <= {port_sig_dict.get(value, value)};\n"
            gate_block += "\tend\n"
            gate_block += "end\n"

        gate_block += "\n"

        for key, value_list in self.gate_dict.items():
            gate_block += f"always @(posedge {port_sig_dict.get(self.clk_rcv, self.clk_rcv)} or negedge {port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
            gate_block += f"\t if (!{port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
            for value in value_list:
                reset_value = self.default_dict.get(value, "'d0")
                gate_block += f"\t\tr_{value}_sliced_d2 <= {reset_value};\n"
            # gate_block += f"\tend else if (r_{key}_sliced_d1) begin\n"
            gate_block += f"\tend else if ({add_prefix_suffix(key, 'r_', '_sliced_d1')}) begin\n"
            for value in value_list:
                gate_block += f"\t\tr_{value}_sliced_d2 <= r_{value}_sliced_d1;\n"
            gate_block += "\tend\n"
            gate_block += "end\n"

        # Gated that is delayed by 1 cycle
        for key, value_list in self.gate_dict_d1.items():
            gate_block += f"always @(posedge {port_sig_dict.get(self.clk_rcv, self.clk_rcv)} or negedge {port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
            gate_block += f"\t if (!{port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
            for value in value_list:
                reset_value = self.default_dict.get(value, "'d0")
                gate_block += f"\t\tr_{value}_sliced_d1 <= {reset_value};\n"
            gate_block += f"\tend else if ({add_prefix_suffix(key, 'r_', '_sliced_d1')}) begin\n"
            for value in value_list:
                gate_block += f"\t\tr_{value}_sliced_d1 <= {port_sig_dict.get(value, value)};\n"
            gate_block += "\tend\n"
            gate_block += "end\n"

        gate_block += "\n"

        for key, value_list in self.gate_dict_d1.items():
            gate_block += f"always @(posedge {port_sig_dict.get(self.clk_rcv, self.clk_rcv)} or negedge {port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
            gate_block += f"\t if (!{port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
            for value in value_list:
                reset_value = self.default_dict.get(value, "'d0")
                gate_block += f"\t\tr_{value}_sliced_d2 <= {reset_value};\n"
            gate_block += f"\tend else if ({add_prefix_suffix(key, 'r_', '_sliced_d2')}) begin\n"
            for value in value_list:
                gate_block += f"\t\tr_{value}_sliced_d2 <= r_{value}_sliced_d1;\n"
            gate_block += "\tend\n"
            gate_block += "end\n"

        # Extra level - Valid signals are usually single-bit (--> don't remember why I wrote this...)
        # Reg declaration
        is_all_input = True
        outport_list_name = [port[1] for port in self.outport_list]

        for value in self.valid_list_d1:
            value_pattern = rf'\b{re.escape(value)}\b'
#            value_is_used = [v for k, v in self.gate_dict_d1.items() if re.search(value_pattern, k)]
            value_is_used = list(itertools.chain.from_iterable([v for k, v in self.gate_dict_d1.items() if re.search(value_pattern, k)]))
            if bool(set(value_is_used) & set(outport_list_name)):
                is_all_input = False
                gate_block += f"\n reg {self.gate_dict_size[value][0]} r_{value}_sliced_d3 {self.gate_dict_size[value][0]};"

        if is_all_input:
            # print("No output valid signal is delayed")
            return gate_block
        else:
            print("There are delayed output valid signal")
        # Reg assignment
        gate_block += f"\nalways @(posedge {port_sig_dict.get(self.clk_rcv, self.clk_rcv)} or negedge {port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
        gate_block += f"\t if (!{port_sig_dict.get(self.rst_rcv, self.rst_rcv)}) begin\n"
        for value in self.valid_list_d1:
            # if value in outport_list_name:
            if bool(set(value_is_used) & set(outport_list_name)):
                reset_value = self.default_dict.get(value, "'d0")
                gate_block += f"\t\tr_{value}_sliced_d3 <= {reset_value};\n"
        gate_block += f"\tend else begin\n"
        for value in self.valid_list_d1:
            # if value in outport_list_name:
            if bool(set(value_is_used) & set(outport_list_name)):
                gate_block += f"\t\tr_{value}_sliced_d3 <= r_{value}_sliced_d2;\n"
        gate_block += "\tend\n"
        gate_block += "end\n"

        return gate_block

    def _generate_gated_error(self, port_sig_dict=None):
        if port_sig_dict is None:
            port_sig_dict = {}

        # For directly output error without mask
        err_sig_list = []
        fierr = self.fault_list[0]
        for fault_signal in self.fault_list[1]:
            # If error injection is done with slicing
            sig_slice = ""
            if "[" in fault_signal:
                ori_sig_name, sig_slice = fault_signal.split("[", 1)
                if sig_slice:
                    sig_slice = "[" + sig_slice
                    raise ValueError("Slicing FIERR feature not supported yet")
            else:
                ori_sig_name = fault_signal
            err_sig_list.append(ori_sig_name)

        err_check_blk = ""

        outport_list = [output[1] for output in self.outport_list]

        # for key, value_list in self.gate_dict.items():
        for key, value_list in self.merge_gate_dict.items():
            for value in value_list:
                if value in outport_list:
                    sliced_outport = port_sig_dict.get(value, value)
                    if sliced_outport:
                        if value in self.ignore_list:
                            # err_check_blk += f"assign w_{value}_ERRORCHECK = |(w_{value}_dup ^ {sliced_outport});\n"
                            pass
                        else:
                            # err_check_blk += f"assign w_{value}_ERRORCHECK = r_{key}_sliced_d2 ? |(w_{value}_dup ^ r_{value}_sliced_d2) : 0;\n"
                            if value in self.gate_dict[key]:
                                if value in err_sig_list:
                                    err_check_blk += f"assign w_{value}_ERRORCHECK = ({add_prefix_suffix(key, 'r_', '_sliced_d2')} || w_{fierr}) ? |(w_{value}_dup ^ r_{value}_sliced_d2) : 1'b0;\n"
                                else:
                                    err_check_blk += f"assign w_{value}_ERRORCHECK = {add_prefix_suffix(key, 'r_', '_sliced_d2')} ? |(w_{value}_dup ^ r_{value}_sliced_d2) : 1'b0;\n"
                            elif value in self.gate_dict_d1[key]:
                                if value in err_sig_list:
                                    err_check_blk += f"assign w_{value}_ERRORCHECK = ({add_prefix_suffix(key, 'r_', '_sliced_d3')} || w_{fierr}) ? |(w_{value}_dup ^ r_{value}_sliced_d2) : 1'b0;\n"
                                else:
                                    err_check_blk += f"assign w_{value}_ERRORCHECK = {add_prefix_suffix(key, 'r_', '_sliced_d3')} ? |(w_{value}_dup ^ r_{value}_sliced_d2) : 1'b0;\n"
                            else:
                                raise ValueError(f"Unknown signal {value}\n{self.gate_dict}\n{self.gate_dict_d1}")

        return err_check_blk

    # Unique methods
    def _generate_instance(self, rst_2d: str, duplicate=False, port_sig_dict=None, param_override=''):    
        instance_blk = ""
        param_blk = ""

        if port_sig_dict:
            param_blk += param_override
        else:
            port_sig_dict = {}
            if self.param_list:
                param_blk += "#("
                for param in self.param_list:
                    param_blk += f"\n    .{param[0]}({param[0]}),"
                param_blk = param_blk[:-1] + "\n" + ")"

        clk = port_sig_dict.get(self.clk_rcv, self.clk_rcv)
        rst = port_sig_dict.get(self.rst_rcv, self.rst_rcv)
        if duplicate:
            instance_blk += f"{self.ip_name} " + param_blk + f" u_{self.ip_name.lower()}_dc " + "("
            instance_blk += "\n" + f"    .{self.clk_rcv}({clk}),"
            if rst_2d:
                instance_blk += "\n" + f"    .{self.rst_rcv}({rst_2d}),"
                # instance_blk += "\n" + f"    .{rst_2d}({port_sig_dict.get(rst_2d, rst_2d)}),"
            else:
                instance_blk += "\n" + f"    .{self.rst_rcv}({rst}),"
            for inport in self.inport_list:
                mapped_inport = port_sig_dict.get(inport[1], inport[1])
                # if is_tie_float(mapped_inport) or inport[1] in self.ignore_list:
                if is_tie_float(mapped_inport) or inport[1] in self.ignore_err_list:
                    instance_blk += "\n" + f"    .{inport[1]}({mapped_inport}),"
                else:
                    instance_blk += "\n" + f"    .{inport[1]}(r_{inport[1]}_sliced_d2),"
            for outport in self.outport_list:
                mapped_outport = port_sig_dict.get(outport[1], outport[1])
                if is_tie_float(mapped_outport):
                    instance_blk += "\n" + f"    .{outport[1]}({mapped_outport}),"
                else:
                    # if outport[1] not in self.ignore_list:
                    if outport[1] not in self.ignore_err_list:
                        instance_blk += "\n" + f"    .{outport[1]}(w_{outport[1]}_sliced),"
                    else:
                        instance_blk += "\n" + f"    .{outport[1]}( ),"
        else:
            instance_blk += f"{self.ip_name} " + param_blk + f" u_{self.ip_name.lower()} " + "("
            instance_blk += "\n" + f"    .{self.clk_rcv}({clk}),"
            instance_blk += "\n" + f"    .{self.rst_rcv}({rst}),"
            for inport in self.inport_list:
                instance_blk += "\n" + f"    .{inport[1]}({port_sig_dict.get(inport[1], inport[1])}),"
            for outport in self.outport_list:
                instance_blk += "\n" + f"    .{outport[1]}({port_sig_dict.get(outport[1], outport[1])}),"

        instance_blk = instance_blk[:-1] + "\n" + ");\n"

        return instance_blk

    def _generate_error_check(self, port_sig_dict=None) -> str:
        if port_sig_dict is None:
            port_sig_dict = {}

        err_check_blk = ""
        # Wire declaration
        for outport in self.outport_list:
            sliced_outport = port_sig_dict.get(outport[1], outport[1])
            # if sliced_outport:  # Not float
            if sliced_outport and outport[1] not in self.ignore_list:  # Not float & not ignored
                err_check_blk += f"wire w_{outport[1]}_ERRORCHECK;\n"
        err_check_blk += "\n"

        # Checking logic
        for outport in self.outport_list:
            sliced_outport = port_sig_dict.get(outport[1], outport[1])
            if sliced_outport:
                if outport[1] in self.ignore_list:
                    # err_check_blk += f"assign w_{outport[1]}_ERRORCHECK = |(w_{outport[1]}_dup ^ {sliced_outport});\n"
                    pass
                else:
                    if outport[1] not in self.gated_list:
                        err_check_blk += f"assign w_{outport[1]}_ERRORCHECK = |(w_{outport[1]}_dup ^ r_{outport[1]}_sliced_d2);\n"

        err_check_blk += self._generate_gated_error()

        err_check_blk += "\nwire w_error_detection;\n"
        err_check_blk += "assign w_error_detection = ("
        for outport in self.outport_list:
            sliced_outport = port_sig_dict.get(outport[1], outport[1])
            # if sliced_outport:
            if sliced_outport and outport[1] not in self.ignore_list:
                err_check_blk += f"\n    w_{outport[1]}_ERRORCHECK |"
        err_check_blk = err_check_blk[:-1] + "\n);\n"

        return err_check_blk

    def _generate_error_mask(self, port_sig_dict=None) -> str:
        if port_sig_dict is None:
            port_sig_dict = {}
        clk = port_sig_dict.get(self.clk_rcv, self.clk_rcv)
        rst = port_sig_dict.get(self.rst_rcv, self.rst_rcv)

        err_mask_blk = (
            f"\nreg [1:0] r_cnt;\n"
            f"always @(posedge {clk} or negedge {rst}) begin\n"
            f"    if (~{rst}) begin\n"
            f"        r_cnt <= 2'd0;\n"
            f"    end else begin\n"
            f"        if (r_cnt != 2'b10)\n"
            f"            r_cnt <= r_cnt + 1;\n"
            f"    end\n"
            f"end\n\n"
        )

        err_mask_blk += (
            f"BOS_ERROR_DOUBLE u_dcls_err (\n"
            f"    .I_CLK    ({clk}),\n"
            f"    .I_RESETN ({rst}),\n"
            f"    .I_ERR_EN (w_error_detection && (r_cnt == 2'b10)),\n"
            f"    .I_ERR_CLR(~w_EN{self.dup_err_port}),\n"
            f"    .O_ERR    ({self.dup_err_port}),\n"
            f"    .O_ERR_B  ({self.dup_err_port}_B)\n"
            f");\n"
        )

        return err_mask_blk

    def _inject_error(self, StatsAnalyzer: Optional[StatsClass] = None, port_sig_dict=None) -> str:
        err_injection_blk = ""
        if port_sig_dict is None:
            port_sig_dict = {}

        err_sig_list = []
        fierr = self.fault_list[0]

        err_injection_blk += f"\nwire w_{fierr};"
        err_injection_blk += (f"\nBOS_SOC_SYNCHSR u_bos_synch_{fierr} ("
                              f"\n    .I_CLK ({port_sig_dict.get(self.clk_rcv, self.clk_rcv)}),"
                              f"\n    .I_RESETN ({port_sig_dict.get(self.rst_rcv, self.rst_rcv)}),"
                              f"\n    .I_D ({fierr}),"
                              f"\n    .O_Q (w_{fierr})"
                              f"\n);\n")

        # Not error injection but ... :)
        err_injection_blk += f"\nwire w_EN{self.dup_err_port};"
        err_injection_blk += (f"\nBOS_SOC_SYNCHSR"
                              f"\n//#("
                              f"\n//    .RST_VAL (1)"        
                              f"\n//)" 
                              f"\nu_bos_synch_EN{self.dup_err_port} ("
                              f"\n    .I_CLK ({port_sig_dict.get(self.clk_rcv, self.clk_rcv)}),"
                              f"\n    .I_RESETN ({port_sig_dict.get(self.rst_rcv, self.rst_rcv)}),"
                              f"\n    .I_D (EN{self.dup_err_port}),"
                              f"\n    .O_Q (w_EN{self.dup_err_port})"
                              f"\n);\n")

        err_injection_blk_only = ""
        for fault_signal in self.fault_list[1]:
            # If error injection is done with slicing
            sig_slice = ""
            if "[" in fault_signal:
                ori_sig_name, sig_slice = fault_signal.split("[", 1)
                if sig_slice:
                    sig_slice = "[" + sig_slice
                    raise ValueError("Slicing FIERR feature not supported yet")
            else:
                ori_sig_name = fault_signal
            err_sig_list.append(ori_sig_name)

            mapped_port = port_sig_dict.get(fault_signal, fault_signal)
            if is_tie_float(mapped_port):
                raise ValueError(f"[FLAT MODE] Floating outputs cannot be used for error injection ({fault_signal}).")
            else:
                # err_injection_blk_only += f"\nassign w_{ori_sig_name}_flip = {{ $bits(w_{ori_sig_name}_sliced) {{1'b0}} }};"
                # err_injection_blk_only += f"\nassign w_{ori_sig_name}_flip{sig_slice} = {{ $bits(w_{ori_sig_name}_sliced{sig_slice}) {{1'b1}} }};"
                pass

        # Another wire level(?) with error injection mux
        self.port_list = self.outport_list
        if StatsAnalyzer:
            self.port_list = super()._convert_dimension_to_number(StatsAnalyzer)
        for outport in self.port_list:
            mapped_outport = port_sig_dict.get(outport[1], outport[1])
            if mapped_outport:  # not float
                err_injection_blk += "\n" + f"wire {outport[0]} w_{outport[1]}_dup {outport[2]};"
                if outport[1] in err_sig_list:
                    err_injection_blk += "\n" + f"wire {outport[0]} w_{outport[1]}_flip {outport[2]};"
        err_injection_blk += err_injection_blk_only

        for outport in self.port_list:
            mapped_outport = port_sig_dict.get(outport[1], outport[1])
            if mapped_outport:  # not float
                if outport[1] not in self.ignore_list:
                    if outport[1] in err_sig_list:
                        # err_injection_blk += f"\nassign w_{outport[1]}_dup = w_{fierr} ? w_{outport[1]}_sliced ^ w_{outport[1]}_flip : w_{outport[1]}_sliced;"
                        err_injection_blk += f"\nassign w_{outport[1]}_dup = w_{fierr} ? ~w_{outport[1]}_sliced : w_{outport[1]}_sliced;"
                    else:
                        err_injection_blk += f"\nassign w_{outport[1]}_dup = w_{outport[1]}_sliced;"

        return err_injection_blk

    def _verify_user_port(self) -> None:
        inport_list_name = [port[1] for port in self.inport_list]
        outport_list_name = [port[1] for port in self.outport_list]
        port_list_name = inport_list_name + outport_list_name
        for ignore_port in self.ignore_list:
            if ignore_port not in port_list_name:
                raise ValueError(f"Port {ignore_port} doesn't exist in module {self.ip_name}")

        if self.fault_list:
            for fault_port in self.fault_list[1]:
                if fault_port.split("[", 1)[0] not in port_list_name:
                    raise ValueError(f"Port {fault_port} doesn't exist in module {self.ip_name}")

        # if self.gate_dict:
        # if {**self.gate_dict, **self.gate_dict_d1}:
        if self.merge_gate_dict:
            # for key, values in self.gate_dict.items():
            pattern = r'\b\w+\b'
            for key, values in {**self.gate_dict, **self.gate_dict_d1}.items():
                key_matches = re.findall(pattern, key)
                for key_match in key_matches:
                    if key_match not in port_list_name:
                        raise ValueError(f"Port {key_match} doesn't exist in module {self.ip_name}")
                    else:
                        for value in values:
                            value_matches = re.findall(pattern, value)
                            for value_match in value_matches:
                                if value_match not in port_list_name:
                                    raise ValueError(f"Port {value_match} doesn't exist in module {self.ip_name}")


def add_prefix_suffix(text, prefix='r_', suffix='_d1'):
    pattern = r'\b\w+\b'

    def replace_word(match):
        word = match.group(0)
        if word.isdigit():
            return word
        elif word.startswith("'"):
            return word
        else:
            return f"{prefix}{word}{suffix}"

    result = re.sub(pattern, replace_word, text)
    
    return result


def extract_valids_from_dict(dictionary: dict) -> list:
    words = []
    pattern = r'\b\w+\b'

    for key in dictionary.keys():
        words.extend(re.findall(pattern, key))
        
    return words


def merge_gate_dict(gate_dict: dict, gate_dict_d1: dict):
    merged_dict = {}

    for key, value_list in gate_dict.items():
        if key in merged_dict:
            merged_dict[key].extend(value_list)
        else:
            merged_dict[key] = value_list[:]

    for key, value_list in gate_dict_d1.items():
        if key in merged_dict:
            merged_dict[key].extend(value_list)
        else:
            merged_dict[key] = value_list[:]
    
    return merged_dict


def check_for_value_in_dict(signal_name: str, merged_dict: dict):
    concatenated_keys = ' '.join(merged_dict.keys())
    if re.search(rf'\b{re.escape(signal_name)}\b', concatenated_keys):
        # print(f"Signal '{signal_name}' is used as valid signal")
        return True
    else:
        # print("No match found.")
        return False


def create_lookup_dict(port_list):
    lookup_dict = {}
    for port in port_list:
        size1, name, size2 = port
        lookup_dict[name] = (size1, size2)
    return lookup_dict

