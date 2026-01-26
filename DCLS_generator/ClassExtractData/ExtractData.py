import re
from DCLS_generator.common.prettycode import bcolors
from dataclasses import dataclass
from DCLS_generator.moduleParser.comment_process import CommentProcess


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
