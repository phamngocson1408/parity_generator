# The script doesn't provide artistic quality lol
# Removing all parities can be troublesome, so for now:
# - Replace the original parity instance with a new one
# - Only add FIERR port (without touching other parity ports)
# --> This class is to remove all the port as well, which is not yet used for now

import re


class RemoveParity:
    safety_scheme = 'Parity'
    pattern = r'.*\b\w*_PARITY\b.*'
    pattern_b = r'.*\b\w*_PARITY_B\b.*'

    def __init__(self, port_declaration: str):
        self.port_declaration = port_declaration

    # This is a very naive version that remove the whole line containing the port
    # For more sophisticated version, refer to DCLS removal (but only for single-bit)
    def _remove_port(self) -> str:
        cleaned_declaration = re.sub(self.pattern, '', self.port_declaration, flags=re.MULTILINE)
        cleaned_declaration = re.sub(self.pattern_b, '', cleaned_declaration, flags=re.MULTILINE)
        return cleaned_declaration

    # [TODO] Check if are there any other port declared
    def _remove_port_clean(self):
        ...

    def _remove_assignment(self, content: str, outport_list: list):
        content_copy = ""
        content_copy += content
        for outport in outport_list:
            # pattern = rf"assign\s+{re.escape(outport)}\s*=\s*(\S+)\s*;"
            pattern = rf"assign\s+{re.escape(outport)}\s*=(.*?);"
            match = re.search(pattern, content_copy)
            if match:
                value_b = match.group(1)
                # print(value_b)
                pattern_wire = rf"wire\s+.*?{value_b.split('[')[0]}.*?;"
                content_copy = re.sub(pattern, '', content_copy)
                content_copy = re.sub(pattern_wire, '', content_copy)

        return content_copy

