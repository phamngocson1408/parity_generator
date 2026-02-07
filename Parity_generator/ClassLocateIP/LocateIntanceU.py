import re
from Parity_generator.ClassLocateIP.LocateIP import LocateIP


class LocateInstanceU(LocateIP):
    ip_level = 'InstanceU'

    def __init__(self, content, ip_name):
        super().__init__(content, ip_name)
        self.ip_start_pattern = r'\b\w+\b' + r'(?:\s*#\s*\([^;]*?\)\s*\b' + self.ip_name + r'\b\s*\(' + r'|\s+\b' + self.ip_name + r'\b\s*\()'
        self.ip_end_pattern   = r';'

