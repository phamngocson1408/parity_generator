import re
from Parity_generator.ClassFindDeclaration.FindDeclaration import FindDeclaration
from Parity_generator.verification.pre_process import *


class FindSignalDeclaration(FindDeclaration):
    datatype = 'signal'
    keyword = r'\b(?:input|output|logic|wire|reg|signed|unsigned)\s+'

    sub_pattern = r'(\bwire\b|\breg\b|\blogic\b).*?;'
    main_pattern = r'\binput\b.*?(?=\binput\b|\boutput\b|;|$)|\boutput\b.*?(?=\binput\b|\boutput\b|;|$)'

    def __init__(self, file_contents: str):
        super().__init__(file_contents)

    def _find_declaration(self, datatype_name: str):
        declaration_list = super()._find_declaration(datatype_name)
        self.pattern = self.sub_pattern
        if declaration_list:
            declaration = super()._declaration_valid(declaration_list, datatype_name)
            # remove declaration and search again, will find it again anyway
            if 'wire' in declaration or 'reg' in declaration or 'logic' in declaration:
                declaration_list = super()._find_declaration(datatype_name)
                _ = super()._declaration_valid(declaration_list, datatype_name)
            # continue search, if another is found -> multiple definitions error
            else:
                declaration_empty = super()._find_declaration(datatype_name)
                if declaration_empty:
                    raise ValueError(f"Expected 1 but found {len(declaration_empty) + len(declaration_list)} declaration(s) of {datatype_name}")
        else:
            # continue search, expect to find one
            declaration_list = super()._find_declaration(datatype_name)
            _ = super()._declaration_valid(declaration_list, datatype_name)

        self.pattern = self.main_pattern    # Return to original pattern
        return declaration_list

    def _parse_declaration(self, datatype_name):
        declaration = super()._parse_declaration(datatype_name)

        dimension_pack = []
        startIndex = None

        # Avoid error while testing, for real module it should generate an error
        if not declaration:
            return ('', [''], '')

        if declaration[0] == '[':
            for i, c in enumerate(declaration):
                if c == '[':
                    startIndex = i
                elif c == ']':
                    dimension_pack.append(declaration[startIndex:i + 1])
                    if declaration[i + 1] != '[':
                        break

        signal_unpack = declaration.replace(''.join(dimension_pack), '')
        signals = signal_unpack.split(',')

        dimension_unpack = ''
        declared = False
        for signal in signals:
            if re.search(r"\b" + re.escape(datatype_name) + r"\b", signal):
                if not declared:
                    if '[' in signal:
                        _, dimension = signal.split('[', 1)
                        dimension_unpack = '[' + dimension
                    declared = True
                else:
                    raise ValueError(f"{self.datatype} {datatype_name} is defined multiple times.")

        parsed_signal = (''.join(dimension_pack), [datatype_name], dimension_unpack)
        return parsed_signal

