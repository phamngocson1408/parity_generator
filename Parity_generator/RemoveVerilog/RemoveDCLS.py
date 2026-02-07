# The script doesn't provide artistic quality lol

import re
from Parity_generator.ClassExtractINFO.ExtractINFO_DCLS import ExtractINFO_DCLS
from Parity_generator.instanceModifier.modify_instance import remove_dcls_signal, remove_dcls_port, add_last_valid_comma


class RemoveDCLS:
    safety_scheme = 'DCLS'

    def __init__(self, DCLS_INFOExtractor: ExtractINFO_DCLS):
        self.fault_list = DCLS_INFOExtractor._extract_fault_injection()
        self.ip_name, self.dup_name, self.dup_path = DCLS_INFOExtractor._extract_ip()
        self.err_dup = DCLS_INFOExtractor._is_error_double()
        _, _, self.r2d = DCLS_INFOExtractor._extract_clk_rst()
        self.ip_err_port, self.dup_err_port = DCLS_INFOExtractor._extract_err_port()
        self.inport_list, self.outport_list = self._create_port_list()

    def _create_port_list(self):
        inport_list = []
        outport_list = []
        if self.fault_list:
            inport_list.append(self.fault_list[0])
        inport_list.append(f"EN{self.ip_err_port}")
        inport_list.append(f"EN{self.dup_err_port}")
        if self.r2d:
            inport_list.append(self.r2d)
        outport_list.append(f"{self.dup_err_port}")
        outport_list.append(f"{self.ip_err_port}")
        if self.err_dup:
            outport_list.append(f"{self.dup_err_port}_B")
            outport_list.append(f"{self.ip_err_port}_B")
        return inport_list, outport_list

    def _remove_port_declaration(self, port_declaration: str):
        # Assuming all 1-bit signals
        # First, remove the name -> Then, remove "input" or "output" keywords
        # port_declaration = port_declaration.rstrip() + ","
        port_declaration = add_last_valid_comma(port_declaration.rstrip())
        port_list = self.inport_list + self.outport_list
        port_list = [port for port in port_list if port]
        for port in port_list:
            pattern = rf"\b{port}\b\s*,"
            port_declaration = re.sub(pattern, '', port_declaration)

        # pattern = r"\binput\b\s+\boutput\b"
        # pattern = r"\b(input|output)\b\s+\b(input|output|$)\b"
        # pattern = r"(\b(input|output)\b\s+(\n|$|\/\/))+"
        pattern = r"(\b(input|output|input\s+logic|output\s+logic)\b\s+(\n|$|\/\/.*?(\n|$)))+"
        matches = re.finditer(pattern, port_declaration)
        # for match in matches:
        #     print(f"Match: {match.group()} | Start: {match.start()} | End: {match.end()}")

        port_declaration = re.sub(pattern, '', port_declaration)
        port_declaration = remove_dcls_port(port_declaration)
        return port_declaration.strip()

    # def _remove_port_declaration_1995(self, port_declaration: str, content: str):
    #     port_declaration = self._remove_port_declaration(port_declaration)

    #     for port in self.outport_list:
    #         pattern = rf"\boutput\b.*?\b{port}\b.*?;"

    #     return port_declaration, content

    def _remove_instance_declaration(self, dup_name: str, instance_declaration: str):
        # Restore instance's name
        # instance_declaration = instance_declaration.replace(f"{dup_name}_DCLS", f"{dup_name}", 1)
#        instance_declaration = instance_declaration.replace("_DCLS", "", 1)
        instance_declaration = instance_declaration.split("(", 1)[0].replace("_DCLS", "", 1) + "(" + instance_declaration.split("(", 1)[1]
        # Remove DCLS port instances
        # instance_declaration += ","
        port_list = self.inport_list + self.outport_list
        for port in port_list:
            # pattern = rf"\.{port}\s*\(\s*{port}\s*\),"
            pattern = rf"\.{port}\s*\(\s*\w*\s*\),"
            instance_declaration = re.sub(pattern, '', instance_declaration)
        for port in port_list:
            # pattern = rf"\.{port}\s*\(\s*{port}\s*\)"
            pattern = rf"\.{port}\s*\(\s*\w*\s*\)"
            instance_declaration = re.sub(pattern, '', instance_declaration)

        instance_declaration = remove_dcls_signal(instance_declaration)
        return instance_declaration + ");"

    def _remove_assignment(self, content: str):
        # pattern = rf"assign\s+{self.ip_err_port}.*?;"
        # content = re.sub(pattern, '', content)
        # pattern = rf"assign\s+{self.ip_err_port}_B.*?;"
        # content = re.sub(pattern, '', content)

        pattern = rf"assign\s+{re.escape(self.ip_err_port)}\s*=\s*(\S+)\s*;"
        match = re.search(pattern, content)
        if match:
            value_b = match.group(1)
            # print(value_b)
            pattern_wire = rf"wire\s+{value_b}.*?;"
            content = re.sub(pattern, '', content)
            content = re.sub(pattern_wire, '', content)

        pattern = rf"assign\s+{re.escape(self.ip_err_port + '_B')}\s*=\s*(\S+)\s*;"
        match = re.search(pattern, content)
        if match:
            value_b = match.group(1)
            # print(value_b)
            pattern_wire = rf"wire\s+{value_b}_B.*?;"
            content = re.sub(pattern, '', content)
            content = re.sub(pattern_wire, '', content)
            
        return content


