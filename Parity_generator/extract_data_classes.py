import re
from Parity_generator.common_utilities import bcolors
from dataclasses import dataclass
from Parity_generator.moduleParser.comment_process import CommentProcess


# ============================================================================
# Base Class: ExtractData
# ============================================================================
class ExtractData:
    data_type = 'Data'
    pattern: str    # input, output, param
    
    def __init__(self, declaration_content, module_content):
        self.declaration_content = CommentProcess(declaration_content).remove_comments()
        self.module_content = CommentProcess(module_content).remove_comments()

    def _extract_declaration(self, content):
        declarations = re.findall(self.pattern, content, flags=re.DOTALL)
        declarations = self._trim_declaration(declarations)

        return declarations

    def _extract_declaration_2001(self):
        return self._extract_declaration(self.declaration_content)

    def _extract_declaration_1995(self):
        return self._extract_declaration(self.module_content)

    def _extract_declaration_valid(self):
        if self._extract_declaration_2001() and self._extract_declaration_1995():
            if self.data_type != 'Parameter':
                # raise ValueError(f"Both 1995 and 2001 styles of {self.data_type} declaration are used. Please check!")
                print(bcolors.WARNING + f"There might be a mixed of 1995 and 2001 styles. Please check if it is ok!" + bcolors.ENDC)
                return self._extract_declaration_2001(), True
            else:
                return self._extract_declaration_2001(), True
            return self._extract_declaration_2001(), True
        elif self._extract_declaration_2001():
            return self._extract_declaration_2001(), True
        elif self._extract_declaration_1995():
            return self._extract_declaration_1995(), False
        else:
            return None, None

    def _trim_declaration(self, declarations: list):
        trimmed_declarations = []
        for declaration in declarations:
            trimmed_declaration = declaration.strip()
            # ',' for separator b/w each declaration, ')' for end of declaration section
            if trimmed_declaration.endswith(','):
                trimmed_declaration = trimmed_declaration[:-1]
            trimmed_declarations.append(trimmed_declaration)

        return trimmed_declarations


# ============================================================================
# Extended Class: ExtractPort (extends ExtractData)
# ============================================================================
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


# ============================================================================
# Extended Class: ExtractParam (extends ExtractData)
# ============================================================================
class ExtractParam(ExtractData):
    data_type = 'Parameter'
    pattern = r'\bparameter\b.*?(?=\bparameter\b|;|$)'  # parameter

    # "declaration_content" here is different from input/output
    def __init__(self, declaration_content, module_content):
        super().__init__(declaration_content, module_content)

    def _extract_value(self):
        param_list = []
        declarations, _ = super()._extract_declaration_valid()
        param_keyword = re.compile(r'\bparameter\b|\blocalparam\b')
        localparam_keyword = re.compile(r'\blocalparam\b.*?(?=\bparameter\b|$)')    # extra to remove localparam

        if declarations:
            for declaration in declarations:
#                param_assignment = param_keyword.sub('', declaration)
                param_assignment = param_keyword.sub('', localparam_keyword.sub('', declaration))   # extra to remove localparam
                param_assignment = param_assignment.replace(' ', '').replace('\n', '')

                param_assignment_list = param_assignment.split(',')
                for param in param_assignment_list:
                    if param == '':
                        continue
                    match = param.find('=')
                    match_cnt = param.count('=')
                    param_list.append((param[:match].strip(), param[match + 1:].strip()))  # (param_name, value)
                    # if match_cnt == 1:
                    #     param_list.append((param[:match].strip(), param[match + 1:].strip()))  # (param_name, value)
                    # else:
                    #     raise ValueError(f"A unexpected pattern for parameter is found:\n \"{param}\"")
        return param_list   # [...('param_name', param_value)...]

    def _extract_value_local(self):
        param_list = []
        declarations, _ = super()._extract_declaration_valid()
        param_keyword = re.compile(r'\bparameter\b|\blocalparam\b')

        if declarations:
            for declaration in declarations:
                param_assignment = param_keyword.sub('', declaration)
                param_assignment = param_assignment.replace(' ', '')

                param_assignment_list = param_assignment.split(',')

                for param in param_assignment_list:
                    match = param.find('=')
                    match_cnt = param.count('=')
                    param_list.append((param[:match].strip(), param[match + 1:].strip()))  # (param_name, value)
                    # if match_cnt == 1:
                    #     param_list.append((param[:match].strip(), param[match + 1:].strip()))  # (param_name, value)
                    # else:
                    #     raise ValueError(f"A unexpected pattern for parameter is found:\n \"{param}\"")
        return param_list   # [...('param_name', param_value)...]

    # Special function to obtain local parameters
    def _extract_local_declaration(self):
        self.pattern = r'\blocalparam\b.*?(?=\blocalparam\b|;|$)'  # pattern for local parameters
        param_list = self._extract_value()
        self.pattern = r'\bparameter\b.*?(?=\bparameter\b|;|$)'  # original pattern
        return param_list


# ============================================================================
# Extended Class: ExtractInport (extends ExtractPort)
# ============================================================================
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


# ============================================================================
# Extended Class: ExtractOutport (extends ExtractPort)
# ============================================================================
class ExtractOutport(ExtractPort):
    data_type = 'Output'
    pattern = r'\boutput\b.*?(?=\binput\b|\boutput\b|;|$)'  # output

    def __init__(self, declaration_content, module_content):
        super().__init__(declaration_content, module_content)
