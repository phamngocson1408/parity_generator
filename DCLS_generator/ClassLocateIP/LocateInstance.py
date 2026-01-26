import re
from DCLS_generator.ClassLocateIP.LocateIP import LocateIP


class LocateInstance(LocateIP):
    ip_level = 'Instance'

    def __init__(self, content, ip_name):
        super().__init__(content, ip_name)
        self.ip_start_pattern = r'\b' + self.ip_name + r'(?:\s*#|\s+\w+\b)'
        self.ip_end_pattern   = r';'

