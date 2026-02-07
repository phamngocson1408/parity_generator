import pandas as pd
from Parity_generator.verification.pre_process import *

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class Gating:
    # axi_aw = ['awid', 'awaddr', 'awlen', 'awsize', 'awburst', 'awlock', 'awcache', 'awprot', 'awvalid', 'awready']
    # axi_w  = ['wid', 'wdata', 'wstrb', 'wlast', 'wvalid', 'wready']
    # axi_b  = ['bid', 'bresp', 'bvalid', 'bready']
    # axi_ar = ['arid', 'araddr', 'arlen', 'arsize', 'arburst', 'arlock', 'arcache', 'arprot', 'arvalid', 'arready']
    # axi_r  = ['rid', 'rdata', 'rresp', 'rlast', 'rvalid', 'rready']

    def __init__(self, inport_list: list, outport_list: list, gated_list_path: str):
        # print("To correctly generate AXI clock gating, please make sure your signals coding style is consistent.")
        self.inport_list = inport_list
        self.outport_list = outport_list
        self.gated_list_path = gated_list_path

    def _filter_gate_list(self):
        if self.gated_list_path:
            df = pd.read_excel(self.gated_list_path)
            df = df.dropna(axis=1, how='all')
            df = df.dropna(axis=0, how='all')
        else:
            return self.inport_list, self.outport_list

        gate_list = df.iloc[1:, 1].tolist()
        filtered_inport_list = []
        for port in self.inport_list:
            if port[1] not in gate_list:
                filtered_inport_list.append(port)
        filtered_outport_list = []
        for port in self.outport_list:
            if port[1] not in gate_list:
                filtered_outport_list.append(port)
        return filtered_inport_list, filtered_outport_list

    def _get_gate_list(self):
        if self.gated_list_path:
            df = pd.read_excel(self.gated_list_path)
        else:
            return {}
        # Remove empty columns & rows
        df = df.dropna(axis=1, how='all')
        df = df.dropna(axis=0, how='all')
        # Fill vertically to make dict
        df = df.fillna(method='ffill')

        gate_dict = {}
        for index, row in df.iloc[1:].iterrows():   # Loop through rows but skip the header row
            key = row.iloc[0]
            value = row.iloc[1]
            if key in gate_dict:
                gate_dict[key].append(value)
            else:
                gate_dict[key] = [value]

        return gate_dict

    def _create_gate_block(self, clk: str, rst: str, port_signal_dict=None) -> str:
        if port_signal_dict is None:
            port_signal_dict = {}
        gate_dict = self._get_gate_list()
        gate_block = ""
        for key, value_list in gate_dict.items():
            gate_block += f"always @(posedge {port_signal_dict.get(clk, clk)} or negedge {port_signal_dict.get(rst, rst)}) begin\n"
            gate_block += f"\t if (!{port_signal_dict.get(rst, rst)}) begin\n"
            for value in value_list:
                gate_block += f"\t\tr_{port_signal_dict.get(value, value)}_d1 <= 0;\n"
            gate_block += f"\tend else if ({port_signal_dict.get(key, key)}) begin\n"
            for value in value_list:
                gate_block += f"\t\tr_{port_signal_dict.get(value, value)}_d1 <= {port_signal_dict.get(value, value)};\n"
            gate_block += "\tend\n"
            gate_block += "end\n"

        gate_block += "\n"

        for key, value_list in gate_dict.items():
            gate_block += f"always @(posedge {port_signal_dict.get(clk, clk)} or negedge {port_signal_dict.get(rst, rst)}) begin\n"
            gate_block += f"\t if (!{port_signal_dict.get(rst, rst)}) begin\n"
            for value in value_list:
                gate_block += f"\t\tr_{port_signal_dict.get(value, value)}_d2 <= 0;\n"
            gate_block += f"\tend else if (r_{port_signal_dict.get(key, key)}_d1) begin\n"
            for value in value_list:
                gate_block += f"\t\tr_{port_signal_dict.get(value, value)}_d2 <= r_{port_signal_dict.get(value, value)}_d1;\n"
            gate_block += "\tend\n"
            gate_block += "end\n"

        return gate_block

