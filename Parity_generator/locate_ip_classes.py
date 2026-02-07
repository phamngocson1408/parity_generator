import re
from Parity_generator.moduleParser.comment_process import CommentProcess


# ============================================================================
# Base Class: LocateIP
# ============================================================================
class LocateIP:
    ip_level = 'IP'
    ip_start_pattern: str
    ip_end_pattern: str

    def __init__(self, content, ip_name):
        self.content = content
        self.ip_name = ip_name

    def _find_ip_start(self):
        comment_processor = CommentProcess(self.content)
        multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
        ip_start_indices = []

        for match in re.finditer(self.ip_start_pattern, self.content, re.DOTALL):
            ip_start_indices.append(match.start())

        if ip_start_indices:
            ip_start_index = self._filter_ip_index(ip_start_indices, multi_cmt_indices, single_cmt_indices, 1)
            return ip_start_index[0]
        else:
            return None        

    def _find_ip_end(self, ip_start_index: int):
        if not isinstance(ip_start_index, int):
            raise ValueError(f"Could not find {self.ip_name} using pattern {self.ip_start_pattern} ({ip_start_index})")
        comment_processor = CommentProcess(self.content)
        multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
        match_indices = []
        closest_index = None

        for match in re.finditer(self.ip_end_pattern, self.content):
            match_indices.append(match.end())

        match_indices.sort()
        for i in match_indices:
            if i > ip_start_index:
                if self._filter_ip_index([i], multi_cmt_indices, single_cmt_indices):
                    closest_index = i
                    break

        if closest_index is None:
            raise ValueError(f"Cannot find where the {self.ip_level} {self.ip_name} ends.")

        return closest_index

    def _separate_ip(self):
        ip_start_index = self._find_ip_start()
        ip_end_index = self._find_ip_end(ip_start_index)

        before_ip_content = ''.join(self.content[: ip_start_index])
        ip_content = ''.join(self.content[ip_start_index: ip_end_index])
        after_ip_content = ''.join(self.content[ip_end_index:])

        return before_ip_content, ip_content, after_ip_content

    def _filter_ip_index(self, match_indices: list, multi_cmt_indices: list, single_cmt_indices: list, match_no=None):
        filtered_match_index = []
        for index in match_indices:
            valid_instance = True
            for start_multi_cmt, end_multi_cmt in multi_cmt_indices:
                if start_multi_cmt < index < end_multi_cmt:
                    valid_instance = False

            for start_cmt, end_cmt in single_cmt_indices:
                if start_cmt < index < end_cmt:
                    valid_instance = False

            if valid_instance:
                filtered_match_index.append(index)

        if match_no:
            assert len(filtered_match_index) == match_no, f"Expected exactly {match_no} match(es) for {self.ip_name} but found {len(filtered_match_index)}."

        return filtered_match_index

    # Extension for find multiple IPs
    def _find_ips_start(self):
        comment_processor = CommentProcess(self.content)
        multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
        ip_start_indices = []

        for match in re.finditer(self.ip_start_pattern, self.content, re.DOTALL):
            ip_start_indices.append(match.start())

        if ip_start_indices:
            ip_start_index = self._filter_ip_index(ip_start_indices, multi_cmt_indices, single_cmt_indices)
            return ip_start_index
        else:
            return None        

    def _find_ips_end(self, ip_start_index: list):
        comment_processor = CommentProcess(self.content)
        multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
        match_indices = []
        ip_index_pair = []

        for match in re.finditer(self.ip_end_pattern, self.content):
            match_indices.append(match.end())

        match_indices.sort()
        for ip_start_idx in ip_start_index:
            for i in match_indices:
                if i > ip_start_idx:
                    if self._filter_ip_index([i], multi_cmt_indices, single_cmt_indices):
                        ip_index_pair += [[ip_start_idx, i]]
                        break

        if ip_index_pair is None:
            raise ValueError(f"Cannot find where the {self.ip_level} {self.ip_name} ends.")

        return ip_index_pair

    def _remove_ips(self):
        ip_start_index = self._find_ips_start()
        index_pairs = self._find_ips_end(ip_start_index)

        s = self.content
        # Sort the list of index pairs by start index in reverse order
        index_pairs.sort(key=lambda x: x[0], reverse=True)
        
        # Iterate over the pairs and remove the substrings from the string
        for start, end in index_pairs:
            # Remove the substring from start to end (end is exclusive)
            s = s[:start] + s[end:]
    
        return s


# ============================================================================
# Extended Class: LocateModule (extends LocateIP)
# ============================================================================
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


# ============================================================================
# Extended Class: LocateInstance (extends LocateIP)
# ============================================================================
class LocateInstance(LocateIP):
    ip_level = 'Instance'

    def __init__(self, content, ip_name):
        super().__init__(content, ip_name)
        self.ip_start_pattern = r'\b' + self.ip_name + r'(?:\s*#|\s+\w+\b)'
        self.ip_end_pattern   = r';'


# ============================================================================
# Extended Class: LocateInstanceU (extends LocateIP)
# ============================================================================
class LocateInstanceU(LocateIP):
    ip_level = 'InstanceU'

    def __init__(self, content, ip_name):
        super().__init__(content, ip_name)
        self.ip_start_pattern = r'\b\w+\b' + r'(?:\s*#\s*\([^;]*?\)\s*\b' + self.ip_name + r'\b\s*\(' + r'|\s+\b' + self.ip_name + r'\b\s*\()'
        self.ip_end_pattern   = r';'
