import re
from DCLS_generator.ClassExtractData.ExtractPort import ExtractPort


class ExtractOutport(ExtractPort):
    data_type = 'Output'
    pattern = r'\boutput\b.*?(?=\binput\b|\boutput\b|;|$)'  # output

    def __init__(self, declaration_content, module_content):
        super().__init__(declaration_content, module_content)

