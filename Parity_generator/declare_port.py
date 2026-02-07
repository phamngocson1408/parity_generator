from Parity_generator.module_parser_utilities import CommentProcess


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


