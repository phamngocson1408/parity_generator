import re

from DCLS_generator.common.prettycode import bcolors
from DCLS_generator.moduleParser.depart_module.depart_module import *

from DCLS_generator.moduleParser.extract_list_multipurpose import is_tie_float


def extract_port_signal_direction(port_connection: str):
    # Regular expression pattern for pattern ".port (signal)"
    pattern = r'\.(\w+).*?\((.*?)\)'

    port_signal_dict = {}   # Used to generate instance ".key(value)"

    # Match the pattern in port_connection
    matches = re.findall(pattern, port_connection)

    # If there is a match, port and signal and check if they are valid before adding to dictionary
    for match in matches:
        assert len(match) == 2, f"Unexpected port connection pattern: {match}"
        port, signal = match
        port = port.strip()
        signal = signal.strip()

        if port:
            if port not in port_signal_dict:
                port_signal_dict[port] = signal
                if signal == '':
                    print(bcolors.WARNING + f"Port '{port}' is left floating." + bcolors.ENDC)
                elif is_tie_float(signal):
                    print(bcolors.WARNING + f"Port '{port}' is tied to {signal}." + bcolors.ENDC)
            else:
                raise ValueError(f"Port {port} has already been defined before.")

    return port_signal_dict


def separate_instance(instance: str, module_name: str, ins_name: str):
    instance_match = []

    top_name = ins_name.split('.')[0]
    instance_name = ins_name.split('.')[-1]

    instance_pattern = r'\b' + module_name + r'\b\s*(#\s*\(.*?\))?\s*' + instance_name + r'\b.*?\('

    param_override = ''

    for match in re.finditer(instance_pattern, instance, flags=re.DOTALL):
        if '#' in instance:
            param_override = re.sub(r'\b' + module_name + r'\b', '', instance[match.start(): match.end()], flags=re.DOTALL)
            param_override = re.sub(r'\b' + instance_name + r'\b.*?\(', '', param_override, flags=re.DOTALL)
        instance_match.append(match.end())

    assert len(instance_match) == 1, f"Found {len(instance_match)} instances {instance_name} of {module_name}."

    port_connection = instance[instance_match[0]:]

    return param_override, port_connection


