"""
Consolidated module parser utilities.
Merged from: comment_process.py, extract_list_multipurpose.py, recursive_read.py, depart_module.py
"""
import re
import os
import subprocess


# ==================== CommentProcess Class ====================
class CommentProcess:
    pattern_multi_line_comment = r'/\*.*?\*/'
    pattern_single_line_comment = r'//.*?(\n|$)'

    def __init__(self, content):
        self.content = content

    def remove_comments(self):
        # Remove multi-line comments
        clean_content = re.sub(self.pattern_multi_line_comment, '', self.content, flags=re.DOTALL)

        # Remove single-line comments
        clean_content = re.sub(self.pattern_single_line_comment, '\n', clean_content)

        return clean_content

    def find_comments(self):
        instance_multi_cmt_index = []
        for match in re.finditer(self.pattern_multi_line_comment, self.content, flags=re.DOTALL):
            instance_multi_cmt_index.append((match.start(), match.end()))

        instance_single_cmt_index = []
        for match in re.finditer(self.pattern_single_line_comment, self.content):
            instance_single_cmt_index.append((match.start(), match.end()))

        return instance_multi_cmt_index, instance_single_cmt_index


# ==================== Bracket Utilities ====================
def filter_ip_index(index: int, multi_cmt_indices: list, single_cmt_indices: list):
    valid_instance = True
    for start_multi_cmt, end_multi_cmt in multi_cmt_indices:
        if start_multi_cmt < index < end_multi_cmt:
            valid_instance = False

    for start_cmt, end_cmt in single_cmt_indices:
        if start_cmt < index < end_cmt:
            valid_instance = False

    return valid_instance


def find_balance_bracket(string: str):
    comment_processor = CommentProcess(string)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    stack = 0
    startIndex = None
    results = []
    for i, c in enumerate(string):
        if c == '(' and filter_ip_index(i, multi_cmt_indices, single_cmt_indices):
            if stack == 0:
                startIndex = i + 1
            # push to stack
            stack += 1
        elif c == ')' and filter_ip_index(i, multi_cmt_indices, single_cmt_indices):
            # pop stack
            stack -= 1
            if stack == 0:
                results.append(string[startIndex:i])
    return results


def find_balance_square_bracket(string: str):
    stack = 0
    startIndex = None
    results = []
    for i, c in enumerate(string):
        if c == '[':
            if stack == 0:
                startIndex = i + 1
            # push to stack
            stack += 1
        elif c == ']':
            # pop stack
            stack -= 1
            if stack == 0:
                results.append(string[startIndex:i])
    return results


# ==================== List Multipurpose Utilities ====================
# FLAT MODE
# List elements should be filtered from the original list base on the purpose
def is_tie_float(mapped_port_name: str):
    if mapped_port_name.startswith("{") and mapped_port_name.endswith("}"):
        bit_group = mapped_port_name[1:-1]
        const_flag = True
        for bit in bit_group.split(','):
            if "'b" in bit or "'h" in bit or "'d" in bit or bit.isnumeric():
                continue
            else:
                const_flag = False
        return const_flag
    # Tied
    elif "'b" in mapped_port_name or "'h" in mapped_port_name or "'d" in mapped_port_name or mapped_port_name.isnumeric():
        return True
    # Float
    elif mapped_port_name == "":
        return True
    else:
        return False


# ==================== Recursive Read Utilities ====================
def recursive_find_v(file_paths):
    file_path_list = file_paths.split(",")
    file_list = []
    for file_path in file_path_list:
        environmentVariables = getEnvironmentVariables()
        file_path = re.sub(r'\$\{(\w+)\}', lambda m: environmentVariables.get(m.group(1), m.group(0)), file_path)    # .f format with brackets
        file_path = re.sub(r'\$(.*?)(?=\/)', lambda m: environmentVariables.get(m.group(1), m.group(0)), file_path)  # positive lookahead for missing brackets
        if not (file_path.startswith('#') or file_path.startswith('//')):
            with open(file_path) as file:
                file_dir = '/'.join(file_path.split('/')[:-1])
                for line in file:
                    line = line.strip()
                    if line.startswith('+incdir') or line.startswith('+libext'):
                        pass
                    else:
                        if line.endswith('.f'):
                            # Find .v files in another filelist
                            file_abs_path = find_abs_path(file_dir, line)
                            file_list += recursive_find_v(file_abs_path)
                        elif line.endswith('.v') or line.endswith('.sv'):
                            # Get the absolute path of all the files pointed to by this filelist
                            # Make sure that we are not reading a file twice
                            file_abs_path = find_abs_path(file_dir, line)
                            file_list.append(file_abs_path)
                        else:
                            # print(f'Unexpected line pattern: {line}')
                            # print(f'Skip reading {line} due to its name :)')
                            pass
    return file_list


def recursive_read_v(file_set, module_name: str, multi_level=False):
    file_dir = None
    module_location = []
    for file_path in file_set:
        if file_path.strip().startswith("-v"):
            file_path = file_path.replace("-v", "", 1).strip()
        environmentVariables = getEnvironmentVariables()
        file_path = re.sub(r'\$\{(\w+)\}', lambda m: environmentVariables.get(m.group(1), m.group(0)), file_path)    # .f format with brackets
        file_path = re.sub(r'\$(.*?)(?=\/)', lambda m: environmentVariables.get(m.group(1), m.group(0)), file_path)  # positive lookahead for missing brackets

        with open(file_path, 'r') as file:
            file_contents = file.read()
        if multi_level is False:
            if module_partition(file_contents, module_name) is not None:
                file_dir = file_path
                module_location.append(module_partition(file_contents, module_name))
        else:
            if instance_partition(file_contents, module_name) is not None:
                file_dir = file_path
                module_location.append(instance_partition(file_contents, module_name))

    assert len(module_location) == 1, f"Expected exactly one matched module/instance {module_name} but found {len(module_location)}."
    
    return module_location, file_dir


def find_abs_path(file_dir, line):
    line = line.replace('-f', '', 1).replace('-F', '', 1).strip()
    if '$' in line:
        return line     # Already absolute path
    else:
        return os.path.abspath(os.path.join(file_dir, line))


# Get env variables
def getEnvironmentVariables():
    result = subprocess.run(['printenv'], capture_output=True, text=True)
    envVars = {}
    for line in result.stdout.splitlines():
        match = re.match(r'.*?=.*?', line, re.DOTALL)
        if match:
            name, value = line.split('=', 1)
            envVars[name] = value
    return envVars


def path_env(file_set: set):
    resultFiles = set()
    environmentVariables = getEnvironmentVariables()

    for line in file_set:
        # skip commented lines
        if line.startswith('#') or line.startswith('//'):
            continue

        line = re.sub(r'\$\{(\w+)\}', lambda m: environmentVariables.get(m.group(1), m.group(0)), line)
        resultFiles.add(line)

    return resultFiles


# ==================== Module Depart Utilities ====================
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
    # Lazy import to avoid circular dependency
    from Parity_generator.locate_ip_classes import LocateModule
    
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
    # Lazy import to avoid circular dependency
    from Parity_generator.locate_ip_classes import LocateInstanceU
    
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
