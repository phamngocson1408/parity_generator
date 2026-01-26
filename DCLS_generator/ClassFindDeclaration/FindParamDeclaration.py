import re
from DCLS_generator.ClassFindDeclaration.FindDeclaration import FindDeclaration
from DCLS_generator.verification.pre_process import *


# I forgot why I made this :(((
class FindParamDeclaration(FindDeclaration):
    datatype = 'parameter'
    keyword = r'\b(?:parameter)\s+'

    sub_pattern = r'\blocalparam\b.*?(?=\blocalparam\b|;|$)'
    main_pattern = r'\bparameter\b.*?(?=\bparameter\b|;|$)'

    def __init__(self, file_contents: str):
        super().__init__(file_contents)

    def _find_declaration(self, datatype_name: str):
        declaration_list = super()._find_declaration(datatype_name)
        self.pattern = self.sub_pattern

        # Check if parameter name is declared or used (before or after "=")
        param_valid_list = []
        position_pattern = r'{}(?=\s*=\s*)'.format(re.escape(datatype_name))
        if not declaration_list:
            declaration_list = super()._find_declaration(datatype_name)

        for declaration in declaration_list:
            params = declaration.split(',')
            for param in params:
                if re.search(position_pattern, param):
                    param_valid_list.append(param)
        _ = super()._declaration_valid(param_valid_list, datatype_name)

        self.pattern = self.main_pattern  # Return to original pattern
        return param_valid_list

    def _parse_declaration(self, datatype_name):
        declaration = super()._parse_declaration(datatype_name)
        params = declaration.split(',')

        declared = False
        value = ''
        for param in params:
            if datatype_name in param:
                if not declared:
                    assert len(param.split('=')) == 2
                    name, value = param.split('=')
                    declared = True
                else:
                    raise ValueError(f"{self.datatype} {datatype_name} is defined multiple times.")

        parsed_declaration = (datatype_name, value)
        return parsed_declaration

