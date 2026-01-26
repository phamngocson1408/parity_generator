def declare_param(parsed_param_list: list):
    param_block = ""

    for parsed_param in parsed_param_list:
        parsed_value = parsed_param[1]
        parsed_name = parsed_param[0]
        param_block += f"\n    parameter {parsed_name} = {parsed_value},"

    param_block = param_block[:-1] + '\n'

    return param_block


# ANSI_C ~ 2001
def declare_param_2001(param_declaration_2001: str, ANSI_C: bool) -> str:
    # if param_declaration_2001:
    if ANSI_C:
        return param_declaration_2001
    else:
        return ''


def declare_param_1995(param_declaration_1995: list, ANSI_C: bool) -> str:
    # if param_declaration_2001:
    if param_declaration_1995 and not ANSI_C:
        return ';\n'.join(param_declaration_1995) + ';\n'
    else:
        return ''

