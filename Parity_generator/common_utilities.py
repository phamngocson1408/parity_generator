import hashlib


# ============================================================================
# Color Formatting Utilities
# ============================================================================
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m<Info> '
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m<Warning> '
    FAIL = '\033[91m<Failed> '
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ============================================================================
# Bracket Finding Utilities
# ============================================================================
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
    # Lazy import to avoid circular dependency
    from Parity_generator.module_parser_utilities import CommentProcess
    
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


def dimension2underscore(dimension: str):
    if ']' in dimension:
        return dimension.replace('[', '_').replace(']', '_').replace(':', '_').replace('-', '_')[:-1]
    else:
        return dimension


def remove_after_pattern(text, pattern="/RTL/"):
    index = text.find(pattern)
    if index != -1:
        return text[:index + len(pattern)]
    return text


def remove_from_pattern(text, pattern="/RTL/"):
    index = text.find(pattern)
    if index != -1:
        return text[:index]
    return text


# ============================================================================
# Port Matching Utilities
# ============================================================================
def find_matching_port(*lists):
    if len(lists) > 4:
        raise ValueError("This function supports at most 4 lists.")

    # Extract middle elements (port name) from each list
    middle_sets = [set(item[1] for item in lst) for lst in lists]
    
    duplicates = set()
    seen = set()

    for s in middle_sets:
        overlap = seen & s
        if overlap:
            duplicates.update(overlap)
        seen.update(s)

    return duplicates


# ============================================================================
# File Utilities
# ============================================================================
def md5_of_file(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()  # Returns string
