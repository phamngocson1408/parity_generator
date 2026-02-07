from Parity_generator.moduleParser.comment_process import CommentProcess


def add_err_signal(instance_content: str, top_design: str):
    modified_instance_content = instance_content.strip()
    modified_instance_content = modified_instance_content[:-2].strip()
    modified_instance_content += "," + "\n\n"
    modified_instance_content += (
        f"    .ERR_{top_design}_DCLS  \t(ERR_{top_design}_DCLS  ),\n"
        f"    .ERR_{top_design}_DCLS_B\t(ERR_{top_design}_DCLS_B)\n"
    )
    modified_instance_content += ");" + "\n"

    return modified_instance_content


def add_err_port(port_content: str, top_design: str):
    modified_port_content = port_content.strip()
    modified_port_content = modified_port_content[:-2].strip()
    modified_port_content += "," + "\n\n"
    modified_port_content += (
        f"    output ERR_{top_design}_DCLS  ,\n"
        f"    output ERR_{top_design}_DCLS_B\n"
    )
    modified_port_content += ");" + "\n"

    return modified_port_content


def change_instance_name(instance_content: str, top_design: str):
    top_design_dc = f"{top_design}_DCLS"
    return instance_content.replace(top_design, top_design_dc, 1)


# Just testing
def add_dcls_signal(dup_design: str, top_design: str, instance_content: str, rst_2d: str, fierr: str, dup_err: bool) -> str:
    port_block = instance_content.rstrip()[:-2].rstrip()

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

    # In case of using 2-cycle delay reset
    if rst_2d:
        port_block += f"\n    .{rst_2d}({rst_2d}),"
    port_block += '\n'

    # declare error port
    if fierr:
        port_block += f"    .{fierr}    ({fierr}      ),\n"
    port_block += f"    .EN{dup_design}    (EN{top_design}      ),\n"

    port_block += f"    .{dup_design}    ({top_design}      ),\n"
    if dup_err:
        port_block += f"    .{dup_design}_B  ({top_design}_B    )"
    
    port_block += "\n);"

    return port_block


# Not actual remove function
def remove_dcls_signal(instance_content: str) -> str:
    port_block = instance_content.rstrip()[:-2].rstrip()

    # In case the last part of port declaration is a comment
    comment_processor = CommentProcess(port_block)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    if multi_cmt_indices and len(port_block) == multi_cmt_indices[-1][1]:
        end_index = find_last_valid_index(port_block, multi_cmt_indices)
        end_index_wo_space = len(port_block[:end_index + 1].rstrip())
        port_block = port_block[:end_index_wo_space] + port_block[end_index_wo_space:].replace(",", "", 1)
    elif single_cmt_indices and len(port_block) == single_cmt_indices[-1][1]:
        end_index = find_last_valid_index(port_block, single_cmt_indices)
        end_index_wo_space = len(port_block[:end_index + 1].rstrip())
        port_block = port_block[:end_index_wo_space] + port_block[end_index_wo_space:].replace(",", "", 1)
    else:
        port_block = port_block.strip()[:-1]
    port_block += '\n'

    return port_block


def find_last_valid_index(port_declaration: str, cmt_indices: list):
    valid_index = None
    for b_i in reversed(range(len(port_declaration))):
        valid_flag = True
        for c_i in cmt_indices:
            if c_i[0] <= b_i <= c_i[1]:
                valid_flag = False

        if valid_flag and port_declaration[b_i] == ')':
            valid_index = b_i

        if valid_index:
            break

    if valid_index is None:
        raise ValueError("Instance either does not start or does not end?")

    return valid_index


def remove_dcls_port(instance_content: str) -> str:
    port_block = instance_content.rstrip()

    # In case the last part of port declaration is a comment
    comment_processor = CommentProcess(port_block)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    if multi_cmt_indices and len(port_block) == multi_cmt_indices[-1][1]:
        end_index = find_last_valid_comma(port_block, multi_cmt_indices)
        end_index_wo_space = len(port_block[:end_index + 1].rstrip())
        port_block = port_block[:end_index_wo_space] + port_block[end_index_wo_space:].replace(",", "", 1)
    elif single_cmt_indices and len(port_block) == single_cmt_indices[-1][1]:
        end_index = find_last_valid_comma(port_block, single_cmt_indices)
        end_index_wo_space = len(port_block[:end_index + 1].rstrip())
        port_block = port_block[:end_index_wo_space-1] + port_block[end_index_wo_space:].replace(",", "", 1)
    else:
        port_block = port_block.strip()[:-1]
    port_block += '\n'

    return port_block


def find_last_valid_comma(port_declaration: str, cmt_indices: list):
    # print(port_declaration)
    valid_index = None
    for b_i in reversed(range(len(port_declaration))):
        valid_flag = True
        for c_i in cmt_indices:
            if c_i[0] <= b_i <= c_i[1]:
                valid_flag = False

        if valid_flag and port_declaration[b_i] == ',':
            valid_index = b_i

        if valid_index:
            break

    if valid_index is None:
        raise ValueError("Instance either does not start or does not end?")

    return valid_index


def add_last_valid_comma(port_declaration: str):
    comment_processor = CommentProcess(port_declaration)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    if multi_cmt_indices and len(port_declaration) == multi_cmt_indices[-1][1]:
        cmt_indices = multi_cmt_indices
    elif single_cmt_indices and len(port_declaration) == single_cmt_indices[-1][1]:
        cmt_indices = single_cmt_indices
    else:
        return port_declaration + ','
    # print(port_declaration)
    valid_index = None
    for b_i in reversed(range(len(port_declaration))):
        valid_flag = True
        for c_i in cmt_indices:
            if c_i[0] <= b_i <= c_i[1]:
                valid_flag = False

        if valid_flag and port_declaration[b_i] != ' ':
            valid_index = b_i

        if valid_index:
            break

    if valid_index is None:
        raise ValueError("Instance either does not start or does not end?")

    return port_declaration[:valid_index+1] + ',' + port_declaration[valid_index+1:]


