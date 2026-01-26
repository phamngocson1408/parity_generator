from DCLS_generator.moduleParser.comment_process import CommentProcess


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


