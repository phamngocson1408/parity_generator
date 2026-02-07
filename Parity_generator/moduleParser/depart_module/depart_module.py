import re
from Parity_generator.common.find_bracket import find_balance_bracket
from Parity_generator.moduleParser.comment_process import *
from Parity_generator.ClassLocateIP.LocateModule import LocateModule
from Parity_generator.ClassLocateIP.LocateIntanceU import LocateInstanceU


def module_declaration_partition(module_declaration_content, param_usage=True):
    param_declaration = ""
    port_declaration = ""

    # # Pattern for pairs of top-most round brackets
    # pattern = r'\(([^\(\)]*(?:\((?:[^\(\)]*?)\)[^\(\)]*)*)\)'
    # # Find all module_blocks using the pattern
    # module_blocks = re.findall(pattern, module_declaration_content)

    module_blocks = find_balance_bracket(module_declaration_content)

    if param_usage:
#        print("This module use parameters")
        assert len(module_blocks) == 2, f"There should be 2 but found {len(module_blocks)}"
        param_declaration = module_blocks[0]
        port_declaration  = module_blocks[1]
    else:
#        print("This module does not use parameters")
        assert len(module_blocks) == 1, f"There should be 1 but found {len(module_blocks)}"
        port_declaration = module_blocks[0]

    return param_declaration, port_declaration


def module_partition(module_content: str, module_name: str):
    # comment_processor = CommentProcess(module_content)
    # module_content = comment_processor.remove_comments()
    ModuleLocator = LocateModule(module_content, module_name)
    module_start_line = ModuleLocator._find_ip_start()

    if module_start_line is None:
        return None
    module_end_line = ModuleLocator._find_ip_end(module_start_line)
    module_seq_line = ModuleLocator._find_ip_declaration(module_start_line)

    module_whole_content = ''.join(module_content[module_seq_line: module_end_line])
    module_declare_content = ''.join(module_content[module_start_line: module_seq_line])

    return module_declare_content, module_whole_content


# Extended for multi-level
# Search for correct instance name instead of module name
def instance_partition(module_content: str, instance_name: str):
    # comment_processor = CommentProcess(module_content)
    # module_content = comment_processor.remove_comments()
    InstanceLocator = LocateInstanceU(module_content, instance_name)
    module_start_line = InstanceLocator._find_ip_start()

    if module_start_line is None:
        return None
    module_end_line = InstanceLocator._find_ip_end(module_start_line)

    # It cannot be in the first line, so using "\n" is okay
    module_start_line_include_declaration = module_content.rfind('\n', 0, module_start_line)

    module_whole_content = ''.join(module_content[module_start_line_include_declaration+1: module_end_line])
    # print(module_whole_content)

    match = re.search(r'([^\s#]+)', module_whole_content.strip())
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Cannot find the module name of instance {instance_name}")


