from typing import Optional
from Parity_generator.moduleParser.extract_list_multipurpose import is_tie_float
from Parity_generator.ClassStats.StatsClass import StatsClass


class GenerateVerilog:
    safety_scheme = ''
    port_list = []  # A temporary port list for overriding methods

    def __init__(self, ip_name: str, param_list: list, clk_rst_list: list, inport_list: list, outport_list: list):
        self.ip_name = ip_name
        self.inport_list = inport_list
        self.outport_list = outport_list
        self.clk_rcv = clk_rst_list[0]
        self.rst_rcv = clk_rst_list[1]
        self.param_list = param_list

    # Generating methods
    def _generate_port(self):
        port_block = f"\n    input {self.clk_rcv},\n    input {self.rst_rcv},"

        for parsed_inport in self.inport_list:
            port_block += f"\n    input {parsed_inport[0]} {parsed_inport[1]} {parsed_inport[2]},"
        for parsed_outport in self.outport_list:
            port_block += f"\n    output {parsed_outport[0]} {parsed_outport[1]} {parsed_outport[2]},"
        port_block = port_block[:-1] + '\n'

        return port_block

    def _add_port(self) -> str:
        return ""

    def _generate_wire(self, port_signal_dict=None) -> str:
        if port_signal_dict is None:
            port_signal_dict = {}

        wire_block = ""
        for port in self.port_list:  # [dim_pack, port_name, dim_unpack]
            signal = port_signal_dict.get(port[1], port[1])
            if signal != '':
                wire_block += f"\nwire {port[0]} w_{(port[1])}_sliced {port[2]};"
        wire_block += '\n'

        return wire_block

    def _generate_reg(self, level=1, port_signal_dict=None) -> str:
        if port_signal_dict is None:
            port_signal_dict = {}

        reg_block = ""
        for i in range(level):
            for port in self.port_list:  # [dim_pack, port_name, dim_unpack]
                signal = port_signal_dict.get(port[1], port[1])
                if is_tie_float(signal) is False:
                    reg_block += f"\nreg {port[0]} r_{port[1]}_sliced_d{i+1} {port[2]};"
            reg_block += '\n'

        return reg_block

    def _generate_delay(self, level=2, port_signal_dict=None, default_dict={}):
        if port_signal_dict is None:
            port_signal_dict = {}
        clk = port_signal_dict.get(self.clk_rcv, self.clk_rcv)
        rst = port_signal_dict.get(self.rst_rcv, self.rst_rcv)

        level = 2   # N1 project
        delay_block = ''
        for i in range(level):
            delay_block += f"always @(posedge {clk} or negedge {rst}) begin\n"
            delay_block += f"\tif (!{rst}) begin\n"
            for port in self.port_list:
                reset_value = default_dict.get(port[1], "'d0")
                mapped_port = port_signal_dict.get(port[1], port[1])
                if is_tie_float(mapped_port) is False:
                    delay_block += f"\t\tr_{port[1]}_sliced_d{i+1} <= {reset_value};\n"
            delay_block += "\tend else begin\n"
            if i == 0:
                for port in self.port_list:
                    mapped_port = port_signal_dict.get(port[1], port[1])
                    if is_tie_float(mapped_port) is False:
                        delay_block += f"\t\tr_{port[1]}_sliced_d{i+1} <= {mapped_port};\n"
            else:
                for port in self.port_list:
                    mapped_port = port_signal_dict.get(port[1], port[1])
                    if is_tie_float(mapped_port) is False:
                        delay_block += f"\t\tr_{port[1]}_sliced_d{i+1} <= r_{port[1]}_sliced_d{i};\n"
            delay_block += "\tend\nend\n\n"

        return delay_block

    # Supporting methods
    # Borrow the method from Stats to convert all parameters to real numbers
    # Since parameters between 2 modules might use the same parameter name with different values
    def _convert_dimension_to_number(self, StatsAnalyzer: StatsClass):
        converted_port_list = []
        for port in self.port_list:
            converted_dimension_pack = StatsAnalyzer._convert_dimension(port[0])
            converted_dimension_unpack = StatsAnalyzer._convert_dimension(port[2])
            converted_port_list.append((converted_dimension_pack, port[1], converted_dimension_unpack))

        return converted_port_list

