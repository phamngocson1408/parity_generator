import re
from DCLS_generator.ClassExtractData.ExtractPort import ExtractPort


class ExtractInport(ExtractPort):
    data_type = 'Input'
    pattern = r'\binput\b.*?(?=\binput\b|\boutput\b|;|$)'  # input

    def __init__(self, declaration_content, module_content):
        super().__init__(declaration_content, module_content)

    def _extract_clk_rst(self, clk: str, rst: str):
        parsed_inport = self._extract_dimension()
        signal_port = []
        # Use list to check the number of component also
        clk_port = []
        rst_port = []

        for inports in parsed_inport:
            if inports[1] != clk and inports[1] != rst:
                signal_port.append([inports[0], inports[1], inports[2]])
            else:
                if inports[1] == clk:
                    clk_port.append([inports[0], inports[1], inports[2]])
                elif inports[1] == rst:
                    rst_port.append([inports[0], inports[1], inports[2]])
                else:
                    raise ValueError("To be or not to be")

        if len(clk_port) != 1 or len(rst_port) != 1:
            raise ValueError(
                f"Expect exactly 1 {clk} and 1 {rst} but found {len(clk_port)} {clk}s and {len(rst_port)} {rst}s")

        return signal_port, [clk, rst]

