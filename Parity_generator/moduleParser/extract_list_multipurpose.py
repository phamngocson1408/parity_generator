from Parity_generator.common_utilities import bcolors


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

