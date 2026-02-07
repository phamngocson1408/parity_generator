import re
from Parity_generator.ClassExtractData.ExtractData import ExtractData


class ExtractPort(ExtractData):
    data_type = 'Port'
    # Experiment phase :)
    # pattern = r'(?=\binput\b|\boutput\b).*?(?=\binput\b|\boutput\b|;|$)'    # input & output
    pattern = r'\binput\b.*?(?=\binput\b|\boutput\b|;|$)|\boutput\b.*?(?=\binput\b|\boutput\b|;|$)'     # input & output

    def __init__(self, declaration_content, module_content):
        super().__init__(declaration_content, module_content)

    def _extract_dimension(self):
        declarations, _ = super()._extract_declaration_valid()
        port_keywords = re.compile(r'\b(?:input|output|logic|wire|reg|signed|unsigned)\s+')
        sized_ports = [port_keywords.sub('', port_content).replace(' ', '') for port_content in declarations]

        port_dimension = []
        # Each line
        for sized_port in sized_ports:
            dimension_pack = []
            startIndex = None

            if sized_port:
                if sized_port[0] == '[':
                    for i, c in enumerate(sized_port):
                        if c == '[':
                            startIndex = i
                        elif c == ']':
                            dimension_pack.append(sized_port[startIndex:i + 1])
                            if sized_port[i + 1] != '[':
                                break

                port_unpack = sized_port.replace(''.join(dimension_pack), '')

                ports = port_unpack.split(',')
                # Each port in a line
                for port in ports:
                    if '[' in port:
                        name, dimension = port.split('[', 1)
                        if name.strip():
                            port_dimension.append((''.join(dimension_pack), name.strip(), '[' + dimension))
                    else:
                        if port.strip():
                            port_dimension.append((''.join(dimension_pack), port.strip(), ''))

        return port_dimension


