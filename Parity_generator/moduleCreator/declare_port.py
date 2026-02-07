from Parity_generator.moduleParser.comment_process import CommentProcess


# Need to consider both 1995 & 2001 styles to make this work
def declare_dcls_port(top: str, port_declaration: str, r2d: str) -> str:
    port_block = port_declaration.rstrip()

    # In case the last part of port declaration is a comment
    comment_processor = CommentProcess(port_block)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    if multi_cmt_indices and len(port_block) == multi_cmt_indices[-1][1]:
        end_index = find_last_valid_index(port_block, multi_cmt_indices)
        end_index_wo_space = len(port_block[:end_index].rstrip())
        port_block = port_block[:end_index_wo_space + 1] + ',' + port_block[end_index_wo_space + 1:]
    elif single_cmt_indices and len(port_block) == single_cmt_indices[-1][1]:
        end_index = find_last_valid_index(port_block, single_cmt_indices)
        end_index_wo_space = len(port_block[:end_index].rstrip())
        port_block = port_block[:end_index_wo_space + 1] + ',' + port_block[end_index_wo_space + 1:]
    else:
        port_block += ','
    port_block += '\n'

    # In case of using 2-cycle delay reset
    if r2d:
        port_block += f"\n    input {r2d},"
    
    if fierr:
            port_block += f"\n    input {fierr},"
    # ML3_DEV02
    port_block += f"\n    input ENERR_{top}_DCLS,"

    port_block += '\n'
    # declare error port
    port_block += (
        f"    output ERR_{top}_DCLS,\n"
        f"    output ERR_{top}_DCLS_B"
    )
    port_block += "\n"

    return port_block


# ANSI_C ~ 2001
def declare_dcls_port_2001(top: str, port_declaration_2001: str, dup_err_port: str, r2d: str, ANSI_C: bool, dup_err=True, fierr=None) -> str:
    port_block = port_declaration_2001.rstrip()

    # In case the last part of port declaration is a comment
    comment_processor = CommentProcess(port_block)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    if multi_cmt_indices and len(port_block) == multi_cmt_indices[-1][1]:
        end_index = find_last_valid_index(port_block, multi_cmt_indices)
        end_index_wo_space = len(port_block[:end_index + 1].rstrip())
        port_block = port_block[:end_index_wo_space] + ',' + port_block[end_index_wo_space:]
    elif single_cmt_indices and len(port_block) == single_cmt_indices[-1][1]:
        end_index = find_last_valid_index(port_block, single_cmt_indices)
        end_index_wo_space = len(port_block[:end_index + 1].rstrip())
        port_block = port_block[:end_index_wo_space] + ',' + port_block[end_index_wo_space:]
    else:
        port_block += ','
    port_block += '\n'

    port_block += f"\n    // Auto-generated DCLS error ports"
    if ANSI_C:
        # In case of using 2-cycle delay reset
        if r2d:
            port_block += f"\n    input {r2d},"

        if fierr:
            port_block += f"\n    input {fierr},"
        # ML3_DEV02
        port_block += f"\n    input EN{dup_err_port},"

        port_block += '\n'
        # declare error port
        if dup_err:
            port_block += (
                f"    output {dup_err_port},\n"
                f"    output {dup_err_port}_B"
            )
        else:
            port_block += (
                f"    output {dup_err_port}"
            )
        port_block += '\n'
    else:
        # In case of using 2-cycle delay reset
        if r2d:
            port_block += f"\n    {r2d},"

        if fierr:
            port_block += f"\n    {fierr},"
        # ML3_DEV02
        port_block += f"\n    EN{dup_err_port},"

        port_block += '\n'
        # declare error port
        if dup_err:
            port_block += (
                f"    {dup_err_port},\n"
                f"    {dup_err_port}_B"
            )
        else:
            port_block += (
                f"    {dup_err_port}"
            )
        port_block += '\n'

    return port_block


def declare_dcls_port_1995(top: str, port_declaration_1995: list, dup_err_port: str, r2d: str, ANSI_C: bool, dup_err=True, fierr=None) -> str:
    port_block = ""
    if not ANSI_C:
        port_block += f"\n    // Auto-generated DCLS error ports"
        port_block += ';\n'.join(port_declaration_1995) + ';\n'
        # In case of using 2-cycle delay reset
        if r2d:
            port_block += f"\n    input {r2d};"

        if fierr:
            port_block += f"\n    input {fierr};"
        # ML3_DEV02
        port_block += f"\n    input EN{dup_err_port},"

        port_block += '\n'
        # declare error port
        if dup_err:
            port_block += (
                f"    output {dup_err_port};\n"
                f"    output {dup_err_port}_B;\n"
            )
        else:
            port_block += (
                f"    output {dup_err_port};\n"
            )
        port_block += "\n"

    return port_block


def find_last_valid_index(port_declaration: str, cmt_indices: list):
    valid_index = None
    for b_i in reversed(range(len(port_declaration))):
        valid_flag = True
        for c_i in cmt_indices:
            if c_i[0] <= b_i <= c_i[1]:
                valid_flag = False

        if valid_flag and port_declaration[b_i].isalnum():
            valid_index = b_i

        if valid_index:
            break

    if valid_index is None:
        raise ValueError("Port declaration either does not start or does not end?")

    return valid_index


def declare_parity_port_2001(port_declaration_2001: str, ANSI_C: bool, extra_inport: list, extra_outport: list) -> str:
    port_block = port_declaration_2001.rstrip()
    
    # Remove trailing comma from original port list if present
    if port_block.endswith(','):
        port_block = port_block[:-1].rstrip()

    # In case the last part of port declaration is a comment
    comment_processor = CommentProcess(port_block)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    if multi_cmt_indices and len(port_block) == multi_cmt_indices[-1][1]:
        end_index = find_last_valid_index(port_block, multi_cmt_indices)
        end_index_wo_space = len(port_block[:end_index + 1].rstrip())
        port_block = port_block[:end_index_wo_space] + ',' + port_block[end_index_wo_space:]
    elif single_cmt_indices and len(port_block) == single_cmt_indices[-1][1]:
        end_index = find_last_valid_index(port_block, single_cmt_indices)
        end_index_wo_space = len(port_block[:end_index + 1].rstrip())
        port_block = port_block[:end_index_wo_space] + ',' + port_block[end_index_wo_space:]
    else:
        # Only add comma if not already present
        if not port_block.rstrip().endswith(','):
            port_block += ','

    if ANSI_C:
        # Ensure we start with clean state (remove any trailing comma/whitespace)
        port_block = port_block.rstrip()
        if port_block.endswith(','):
            port_block = port_block[:-1]
        
        # If there are extra ports, ensure original ports end with comma
        if extra_inport or extra_outport:
            if not port_block.endswith(','):
                port_block += ','
        
        if extra_inport:
            for inport in extra_inport:
                port_block += f"\n    input {inport[0]} {inport[1]} {inport[2]},"
        if extra_outport:
            for outport in extra_outport:
                port_block += f"\n    output {outport[0]} {outport[1]} {outport[2]},"

        # Always remove trailing comma at the end
        port_block = port_block.rstrip()
        if port_block.endswith(','):
            port_block = port_block[:-1]
    else:
        # Ensure we start with clean state
        port_block = port_block.rstrip()
        if port_block.endswith(','):
            port_block = port_block[:-1]
        
        # If there are extra ports, ensure original ports end with comma
        if extra_inport or extra_outport:
            if not port_block.endswith(','):
                port_block += ','
        
        if extra_inport:
            for inport in extra_inport:
                port_block += f"\n    {inport[1]},"
        if extra_outport:
            for outport in extra_outport:
                port_block += f"\n    {outport[1]},"

        # Always remove trailing comma at the end
        port_block = port_block.rstrip()
        if port_block.endswith(','):
            port_block = port_block[:-1]

    return port_block


def declare_parity_port_1995(port_declaration_1995: list, ANSI_C: bool, extra_inport: list, extra_outport: list) -> str:
    port_block = ""
    if not ANSI_C:
        port_block += ';\n'.join(port_declaration_1995) + ';\n'
        if extra_inport:
            for inport in extra_inport:
                port_block += f"\n    input {inport[0]} {inport[1]} {inport[2]};"

        if extra_outport:
            for outport in extra_outport:
                port_block += f"\n    output {outport[0]} {outport[1]} {outport[2]};"

        port_block += "\n"

    return port_block


