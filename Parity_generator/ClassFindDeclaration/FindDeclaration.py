import re
from Parity_generator.extract_data_classes import ExtractPort


class FindDeclaration:
    datatype = 'declaration'
    keyword = r''

    sub_pattern = r''
    main_pattern = r''
    
    def __init__(self, file_contents: str):
        self.file_contents = file_contents
        self.pattern = self.main_pattern
        
    def _find_declaration(self, datatype_name: str) -> list:
        declaration_list = []

        # Check in whole module content (using self.pattern)
        for match in re.finditer(self.pattern, self.file_contents, flags=re.DOTALL):
            if re.search(r"\b" + re.escape(datatype_name) + r"\b", self.file_contents[match.start():match.end()]):
                declaration_list.append(self.file_contents[match.start():match.end()])

        return declaration_list

    def _parse_declaration(self, datatype_name: str):
        declaration_list = self._find_declaration(datatype_name)
        declaration = self._declaration_valid(declaration_list, datatype_name)
        signal_keywords = re.compile(self.keyword)
        declaration = signal_keywords.sub('', declaration).replace(' ', '')
        return declaration

    def _declaration_valid(self, declaration_list: list, datatype_name: str) -> str:
        assert len(declaration_list) == 1, f"Expected 1 but found {len(declaration_list)} declaration(s) of {datatype_name}"
        return declaration_list[0]

