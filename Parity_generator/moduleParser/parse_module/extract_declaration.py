import re
from Parity_generator.moduleParser.depart_module.depart_module import *


# For RTL coding, parameter (that can be overidden) should only appear inside module declaration
def extract_param_declaration_1995(module_content: str):
    # Pattern to match whole word "parameter" following by ";"
    # In real practice, "module_content" can include declaration without effecting results
    # since it is illegal to have both type of declaration (1995 & 2001) in the same module
    pattern_param = r'\bparameter\b.*?;'

    param_declaration = re.findall(pattern_param, module_content, flags=re.DOTALL)

    return param_declaration


def extract_param_declaration_2001(module_declaration_content: str):
    # Pattern to match whole word "parameter"
    pattern_param = re.compile(r'\bparameter\b')

    # Extract lines containing "parameter"
    param_lines = [line.strip() for line in module_declaration_content.split('\n') if pattern_param.search(line)]
    return param_lines


# Port (detailed) information could be inside or outside module declaration scope,
# so processing for this information is made separated
# For outside module declaration scope, port declaration could be in multiple lines
def extract_port_declaration_2001(module_declaration_content: str):
    # Pattern to match whole words "input" or "output"
    pattern_input = re.compile(r'\binput\b')
    pattern_output = re.compile(r'\boutput\b')

    # Extract lines containing "input" or "output"
    input_lines = [line.strip() for line in module_declaration_content.split('\n') if pattern_input.search(line)]
    output_lines = [line.strip() for line in module_declaration_content.split('\n') if pattern_output.search(line)]
    return input_lines, output_lines


def extract_port_declaration_1995(module_content: str):
    # Pattern to match whole words "input" or "output" following by ";"
    # In real practice, "module_content" can include declaration without effecting results
    # since it is illegal to have both type of declaration (1995 & 2001) in the same module
    pattern_input = r'\binput\b.*?;'
    pattern_output = r'\boutput\b.*?;'

    inport_declaration = re.findall(pattern_input, module_content, flags=re.DOTALL)
    outport_declaration = re.findall(pattern_output, module_content, flags=re.DOTALL)

    return inport_declaration, outport_declaration


# Works for both 1995 and 2001 styles
def extract_port_declaration(module_declaration_content: str):
    # Pattern to match whole words "input" or "output" until another "input","output", or ";"
    pattern_input = r'(\binput\b.*?(?=\binput\b|\boutput\b|;))'
    pattern_output = r'(\boutput\b.*?(?=\binput\b|\boutput\b|;))'

    inport_declaration = re.findall(pattern_input, module_declaration_content, flags=re.DOTALL)
    inport_declaration = trim_port_declaration(inport_declaration)
    outport_declaration = re.findall(pattern_output, module_declaration_content, flags=re.DOTALL)
    outport_declaration = trim_port_declaration(outport_declaration)

    return inport_declaration, outport_declaration


def trim_port_declaration(port_declarations: list):
    trimmed_port_declarations = []
    for port_declaration in port_declarations:
        trimmed_port_declaration = port_declaration.strip()
        if trimmed_port_declaration.endswith(',') or trimmed_port_declaration.endswith(')'):
            trimmed_port_declaration = trimmed_port_declaration[:-1]
        trimmed_port_declarations.append(trimmed_port_declaration)

    return trimmed_port_declarations


