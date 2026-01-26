import re
from DCLS_generator.ClassLocateIP.LocateIP import LocateIP
from DCLS_generator.moduleParser.comment_process import CommentProcess


class LocateModule(LocateIP):
    ip_level = 'Module'

    def __init__(self, content, ip_name):
        super().__init__(content, ip_name)
        self.ip_start_pattern = r'module\s+' + (r'\b' + re.escape(self.ip_name) + r'\b')
        self.ip_end_pattern   = r'\bendmodule\b'
        self.ip_declr_pattern = r';'

    def _find_ip_declaration(self, ip_start_index: int):
        comment_processor = CommentProcess(self.content)
        multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
        match_indices = []
        closest_index = None

        for match in re.finditer(self.ip_declr_pattern, self.content):
            match_indices.append(match.end())

        match_indices.sort()
        for i in match_indices:
            if i > ip_start_index:
                if self._filter_ip_index([i], multi_cmt_indices, single_cmt_indices):
                    closest_index = i
                    break

        if closest_index is None:
            raise ValueError(f"Cannot find where the declaration of {self.ip_name} ends.")

        return closest_index


