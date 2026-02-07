import re


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


