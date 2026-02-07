import re
from Parity_generator.ClassExtractData.ExtractData import ExtractData


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

