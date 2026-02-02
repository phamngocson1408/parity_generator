import argparse

from DCLS_generator.common.prettycode import bcolors
from DCLS_generator.common.find_duplicate_port import find_matching_port
from DCLS_generator.ClassExtractData.ExtractPort import ExtractPort
from DCLS_generator.ClassLocateIP.LocateModule import LocateModule
from DCLS_generator.ClassLocateIP.LocateInstance import LocateInstance
from DCLS_generator.GenerateVerilog.GenerateParity.GenerateParity import GenerateParity
from DCLS_generator.GenerateVerilog.GenerateParity.GenerateParityBus import GenerateBus
from DCLS_generator.GenerateVerilog.GenerateParity.GenerateParityRegister import GenerateRegister
from DCLS_generator.GenerateVerilog.GenerateVerilog import GenerateVerilog
from DCLS_generator.RemoveVerilog.RemoveParity import RemoveParity
from DCLS_generator.ClassExtractINFO.ExtractINFO import ExtractINFO
from DCLS_generator.ClassExtractINFO.ExtractINFO_Parity.ExtractINFO_Parity_Signal import ExtractINFO_Parity_Signal
from DCLS_generator.ClassExtractINFO.ExtractINFO_Parity.ExtractINFO_Parity_Bus import ExtractINFO_Parity_Bus
from DCLS_generator.ClassExtractINFO.ExtractINFO_Parity.ExtractINFO_Parity_Register import ExtractINFO_Parity_Register
from collections import defaultdict

from DCLS_generator.instanceModifier.modify_instance import remove_dcls_port
from DCLS_generator.moduleParser.comment_process import CommentProcess

from DCLS_generator.moduleCreator.declare_port import declare_parity_port_2001, declare_parity_port_1995
from DCLS_generator.moduleParser.depart_module.depart_module import module_partition, module_declaration_partition

from DCLS_generator.moduleParser.recursive_read import *
from DCLS_generator.common.find_bracket import remove_after_pattern
from DCLS_generator.function_wrapper.dcls_wrappers import filter_ip_index

import warnings
import os

warnings.simplefilter(action='ignore', category=FutureWarning)

# Set AXICRYPT_HOME if not already set
if 'AXICRYPT_HOME' not in os.environ:
    os.environ['AXICRYPT_HOME'] = os.path.join(os.getcwd(), 'axicrypt')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parity generator v1 by Tho Mai (2024.06)')
    parser.add_argument('-inst', type=str, default='BOS_BUS_PARITY_AXI_M', help='Parity instance name')
    parser.add_argument('-type', type=str, default='SAFETY.PARITY', help='Parity scheme type')
    parser.add_argument("-info", type=str, help="INFO file path")
    parser.add_argument("-group", type=str, default='ALL', help="GROUP filter: comma-separated group names or 'ALL' for all groups")
    parser.add_argument("-gen-top", type=str, default='YES', help="Generate top wrapper module (YES/NO)")
    args = parser.parse_args()

    # file_path = "./DCLS_generator/[INFO]_PARITY_TEMPLATE.xlsx"
    file_path = args.info
    if args.type:
        parity_scheme_list = [args.type]
    else:
        parity_scheme_list = ["SAFETY.PARITY"]
    # parity_scheme = "SAFETY.REGISTER PARITY"

    # Parse group filter
    if args.group.upper() == 'ALL':
        selected_groups = None  # None means all groups
    else:
        selected_groups = set([g.strip() for g in args.group.split(',')])
    
    # Parse gen_top flag
    gen_top = args.gen_top.upper() == 'YES'
    
    def extract_parity_module_ports(ip_name, Parity_generator):
        """Extract port list from generated parity module"""
        import re
        try:
            # Get parity module content
            parity_module_content = Parity_generator._generate_module_ip(ip_name)
            
            # Extract module declaration
            match = re.search(r'module\s+\w+\s*\((.*?)\);', parity_module_content, re.DOTALL)
            if match:
                port_declaration = match.group(1)
                port_names = []
                
                # Extract port names - handle multiple ports per line
                for line in port_declaration.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('//'):
                        # Split by comma to handle multiple ports on same line
                        parts = line.split(',')
                        for part in parts:
                            # Extract port name (identifier after direction keywords)
                            # Remove direction keywords (input/output/inout)
                            part = re.sub(r'^\s*(input|output|inout)\s+', '', part).strip()
                            # Remove bit width specification
                            part = re.sub(r'^\[\d+.*?\]\s+', '', part).strip()
                            # Extract port name
                            match = re.search(r'(\w+)', part)
                            if match:
                                port_name = match.group(1)
                                if port_name and port_name not in port_names:
                                    port_names.append(port_name)
                
                return port_names
        except Exception as e:
            print(f"Error extracting parity module ports: {e}")
        
        return None
    
    def extract_parity_input_ports(ip_name, Parity_generator, top_port_declaration):
        """Extract input ports from parity module with their specifications (excluding ACLK, I_RESETN, and already declared ports)"""
        import re
        try:
            parity_module_content = Parity_generator._generate_module_ip(ip_name)
            
            # Extract module declaration
            match = re.search(r'module\s+\w+\s*\((.*?)\);', parity_module_content, re.DOTALL)
            if match:
                port_declaration = match.group(1)
                extra_inport = []
                seen_ports = set()
                
                # Ports to skip (clock/reset already exist in top module)
                skip_ports = {'ACLK', 'I_CLK', 'I_RESETN', 'RESETN_ACLK'}
                
                # Parse each line to find input ports
                for line in port_declaration.split('\n'):
                    line = line.strip()
                    if line.startswith('input'):
                        # Split by comma to handle multiple inputs on same line
                        parts = line.split(',')
                        for part in parts:
                            part = part.strip()
                            if part.startswith('input') or part:
                                # Parse: input [width] port_name
                                match = re.search(r'input\s+(\[.*?\]\s+)?(\w+)', part)
                                if match:
                                    bit_width = match.group(1).strip() if match.group(1) else ""
                                    port_name = match.group(2)
                                    
                                    # Skip if already in top module declaration or in skip list
                                    if port_name not in seen_ports and port_name not in skip_ports and port_name not in top_port_declaration:
                                        seen_ports.add(port_name)
                                        extra_inport.append([bit_width, port_name, ""])
                
                return extra_inport
        except Exception as e:
            print(f"Error extracting parity input ports: {e}")
        
        return []
    
    def extract_parity_output_ports(ip_name, Parity_generator, top_port_declaration):
        """Extract output ports from parity module with their specifications (excluding already declared ports)"""
        import re
        try:
            parity_module_content = Parity_generator._generate_module_ip(ip_name)
            
            # Extract module declaration
            match = re.search(r'module\s+\w+\s*\((.*?)\);', parity_module_content, re.DOTALL)
            if match:
                port_declaration = match.group(1)
                extra_outport = []
                seen_ports = set()
                
                # Parse each line to find output ports
                for line in port_declaration.split('\n'):
                    line = line.strip()
                    if line.startswith('output'):
                        # Split by comma to handle multiple outputs on same line
                        parts = line.split(',')
                        for part in parts:
                            part = part.strip()
                            if part.startswith('output') or part:
                                # Parse: output [width] port_name
                                match = re.search(r'output\s+(\[.*?\]\s+)?(\w+)', part)
                                if match:
                                    bit_width = match.group(1).strip() if match.group(1) else ""
                                    port_name = match.group(2)
                                    
                                    # Skip if already in top module declaration
                                    if port_name not in seen_ports and port_name not in top_port_declaration:
                                        seen_ports.add(port_name)
                                        extra_outport.append([bit_width, port_name, ""])
                
                return extra_outport
        except Exception as e:
            print(f"Error extracting parity output ports: {e}")
        
        return []
    
    def clean_parity_from_module(module_content, module_name):
        """Remove only parity-related ports (containing 'PARITY') and parity instances from module"""
        import re
        
        lines = module_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Only skip lines that contain "PARITY" in port name (true parity ports)
            # or parity instance (u_*_ip_parity_gen)
            # Do NOT skip other error ports like ENERR_*_CRC or FIERR_*
            
            if 'PARITY' in line or ('u_' in line and 'ip_parity_gen' in line):
                # Skip this line - it's a true parity port or parity instance
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def filter_by_group(info_dict_list, selected_groups):
        """Filter info_dict_list by GROUP column if selected_groups is specified"""
        if selected_groups is None:
            return info_dict_list
        
        filtered_list = []
        for info_dict in info_dict_list:
            group_value = info_dict.get("GROUP", "").strip()
            if group_value in selected_groups:
                filtered_list.append(info_dict)
        
        if not filtered_list:
            print(bcolors.WARNING + f"Warning: No rows found for groups: {selected_groups}" + bcolors.ENDC)
        
        return filtered_list

    for parity_scheme in parity_scheme_list:
        INFOExtractor = ExtractINFO(file_path, parity_scheme)
        info_dict_list = INFOExtractor._read_info_multi()
        info_dict_list = filter_by_group(info_dict_list, selected_groups)
        if parity_scheme == "SAFETY.SIGNAL PARITY":
            ip_filelist_dict_drv = {}
            ip_filelist_dict_rcv = {}
            if info_dict_list:
                for info_dict in info_dict_list:
                    Parity_INFOExtractor = ExtractINFO_Parity_Signal(info_dict)
                    ip_filelist_dict_drv[
                        Parity_INFOExtractor._extract_drv_name()] = Parity_INFOExtractor._extract_filelist_list_drv()
                    ip_filelist_dict_rcv[
                        Parity_INFOExtractor._extract_rcv_name()] = Parity_INFOExtractor._extract_filelist_list_rcv()
                    Parity_generator = GenerateParity(Parity_INFOExtractor)
                    Parity_generator._wrapper_drv()
                    Parity_generator._wrapper_rcv()

                dc_dir = f"./DCLS_generator/module_parity/SIGNAL_DRIVER_PARITY.v"
                dcls_file = open(dc_dir, 'w')
                dcls_file.write(Parity_generator._generate_module_drv())

                dc_dir = f"./DCLS_generator/module_parity/SIGNAL_RECEIVER_PARITY.v"
                dcls_file = open(dc_dir, 'w')
                dcls_file.write(Parity_generator._generate_module_rcv())

                port_list_drv = Parity_generator._list_port_drv()
                port_list_rcv = Parity_generator._list_port_rcv()
                Parity_generator._reset_generator()

                # Driver
                original_inport, original_outport, extra_inport, extra_outport = [], [], [], []
                for ip, lst in port_list_drv.items():
                    print("IP: ", ip)
                    original_inport, original_outport, extra_inport, extra_outport = lst

                    # top_hier_wrapper
                    top_name = ip
                    file_list_list = ip_filelist_dict_drv[ip]
                    file_list = recursive_find_v(file_list_list)
                    file_set = set(file_list)
                    file_set_env = path_env(file_set)
                    _, top_file_dir = recursive_read_v(file_set_env, top_name)
                    print(f"Target top module '{top_name}' is found at '{top_file_dir}'")
                    with open(top_file_dir, 'r') as file:
                        top_file_contents_ori = file.read()

                    ModuleLocator = LocateModule(top_file_contents_ori, top_name)
                    before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

                    # Add error ports to top module
                    top_file_contents_before_safety = top_file_contents
                    _, module_whole_content = module_partition(top_file_contents, top_name)

                    top_module_declaration_content, top_module_whole_content = module_partition(
                        top_file_contents_before_safety,
                        top_name)
                    top_param_declaration, top_port_declaration = module_declaration_partition(
                        top_module_declaration_content,
                        param_usage=False)

                    PortExtractor = ExtractPort(top_port_declaration, top_module_whole_content)
                    port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
                    module_declaration_content = f"module {top_name}_PARITY "
                    if top_param_declaration:
                        module_declaration_content += "#(\n" + top_param_declaration + "\n)"
                    module_declaration_content += "(\n" + declare_parity_port_2001(
                        port_declaration_2001=top_port_declaration,
                        ANSI_C=ANSI_C_port,
                        extra_inport=extra_inport,
                        extra_outport=extra_outport) + "\n);\n"
                    module_declaration_content += "\n" + declare_parity_port_1995(
                        port_declaration_1995=port_declaration_1995,
                        ANSI_C=ANSI_C_port,
                        extra_inport=extra_inport,
                        extra_outport=extra_outport) + "\n"

                    # Add instance
                    all_port = original_inport + original_outport + extra_inport + extra_outport
                    instance_content = f"\n{top_name}_SIGNAL_PARITY_GEN u_{top_name.lower()}_signal_parity_gen ("
                    for port in all_port:
                        instance_content += f"\n    .{port[1]} ({port[1]}),"
                    instance_content = instance_content[:-1] + "\n);\n"

                    module_whole_content = module_whole_content[:-9] + instance_content + "endmodule"
                    top_file_contents = module_declaration_content + module_whole_content
                    par_dir = f"./DCLS_generator/module_parity/SIGNAL_PARITY_DRV_{top_name}_TOP.v"
                    par_file = open(par_dir, 'w')
                    par_file.write(before_top_file_contents + top_file_contents + after_top_file_contents)

                # Receiver
                original_inport, original_outport, extra_inport, extra_outport = [], [], [], []
                for ip, lst in port_list_rcv.items():
                    print("IP: ", ip)
                    original_inport, original_outport, extra_inport, extra_outport = lst

                    # top_hier_wrapper
                    top_name = ip
                    file_list_list = ip_filelist_dict_rcv[ip]
                    file_list = recursive_find_v(file_list_list)
                    file_set = set(file_list)
                    file_set_env = path_env(file_set)
                    _, top_file_dir = recursive_read_v(file_set_env, top_name)
                    print(f"Target top module '{top_name}' is found at '{top_file_dir}'")
                    with open(top_file_dir, 'r') as file:
                        top_file_contents_ori = file.read()

                    ModuleLocator = LocateModule(top_file_contents_ori, top_name)
                    before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

                    # Add error ports to top module
                    top_file_contents_before_safety = top_file_contents
                    _, module_whole_content = module_partition(top_file_contents, top_name)

                    top_module_declaration_content, top_module_whole_content = module_partition(
                        top_file_contents_before_safety,
                        top_name)

#                    hash_indices = [index for index, char in enumerate(top_module_declaration_content) if char == '#']
#                    comment_processor = CommentProcess(top_module_declaration_content)
#                    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
#                    param_usage = filter_ip_index(hash_indices, multi_cmt_indices, single_cmt_indices, 1)
                    top_param_declaration, top_port_declaration = module_declaration_partition(
                        top_module_declaration_content,
                        param_usage=False)

                    PortExtractor = ExtractPort(top_port_declaration, top_module_whole_content)
                    port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
                    module_declaration_content = f"module {top_name}_PARITY "
                    if top_param_declaration:
                        module_declaration_content += "#(\n" + top_param_declaration + "\n)"
                    module_declaration_content += "(\n" + declare_parity_port_2001(
                        port_declaration_2001=top_port_declaration,
                        ANSI_C=ANSI_C_port,
                        extra_inport=extra_inport,
                        extra_outport=extra_outport) + "\n);\n"
                    module_declaration_content += "\n" + declare_parity_port_1995(
                        port_declaration_1995=port_declaration_1995,
                        ANSI_C=ANSI_C_port,
                        extra_inport=extra_inport,
                        extra_outport=extra_outport) + "\n"

                    # Add instance
                    all_port = original_inport + original_outport + extra_inport + extra_outport
                    instance_content = f"\n{top_name}_SIGNAL_PARITY_GEN u_{top_name.lower()}_signal_parity_gen ("
                    for port in all_port:
                        instance_content += f"\n    .{port[1]} ({port[1]}),"
                    instance_content = instance_content[:-1] + "\n);\n"

                    module_whole_content = module_whole_content[:-9] + instance_content + "endmodule"
                    top_file_contents = module_declaration_content + module_whole_content
                    par_dir = f"./DCLS_generator/module_parity/SIGNAL_PARITY_RCV_{top_name}_TOP.v"
                    par_file = open(par_dir, 'w')
                    par_file.write(before_top_file_contents + top_file_contents + after_top_file_contents)

        elif parity_scheme == "SAFETY.PARITY":
            ip_filelist_dict = {}
            if info_dict_list:
                for info_dict in info_dict_list:
                    Parity_INFOExtractor = ExtractINFO_Parity_Bus(info_dict)
                    ip_filelist_dict[
                        Parity_INFOExtractor._extract_ip_name()] = Parity_INFOExtractor._extract_filelist_list_ip()
                    Parity_generator = GenerateBus(Parity_INFOExtractor)
                    Parity_generator._wrapper_ip()

                # par_dir = f"./DCLS_generator/module_parity/IP_PARITY.v"
                # par_file = open(par_dir, 'w')
                # par_file.write(Parity_generator._generate_module_ip())

                port_list = Parity_generator._list_port_ip()
                # Parity_generator._reset_generator()

                original_inport, original_outport, extra_inport, extra_outport = [], [], [], []
                if find_matching_port(original_inport, original_outport, extra_inport, extra_outport):
                    print(find_matching_port(original_inport, original_outport, extra_inport, extra_outport))
                    raise Exception("Defined extra ports already exist in design")
                

                for ip, lst in port_list.items():
                    # print("IP: ", ip)
                    original_inport, original_outport, extra_inport, extra_outport = lst
                    extra_outport_name = [outport[1] for outport in extra_outport]

                    # top_hier_wrapper
                    top_name = ip
                    file_list_list = ip_filelist_dict[ip]
                    file_list = recursive_find_v(file_list_list)
                    file_set = set(file_list)
                    file_set_env = path_env(file_set)
                    _, top_file_dir = recursive_read_v(file_set_env, top_name)
                    print(f"Target top module '{top_name}' is found at '{top_file_dir}'")
                    with open(top_file_dir, 'r') as file:
                        top_file_contents_ori = file.read()

                    # Clean parity ports/instances from original file first
                    top_file_contents_ori = clean_parity_from_module(top_file_contents_ori, top_name)

                    ModuleLocator = LocateModule(top_file_contents_ori, top_name)
                    before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

                    # Add error ports to top module
                    top_file_contents_before_safety = top_file_contents
                    _, module_whole_content = module_partition(top_file_contents, top_name)
                    # InstanceLocator  = LocateInstance(top_file_contents_before_safety, args.inst)
                    InstanceLocator = LocateInstance(module_whole_content, args.inst)
                    try:
                        # before_instance_content, instance_content, after_instance_content = InstanceLocator._separate_ip()
                        # # top_file_contents_before_safety = before_instance_content + "\n" + after_instance_content
                        # module_whole_content = before_instance_content + "\n" + after_instance_content
                        module_whole_content = InstanceLocator._remove_ips()
                        is_safe = True
                    except:
                        is_safe = False

                    is_safe = False # For now, not using removal for parity

                    top_module_declaration_content, top_module_whole_content = module_partition(top_file_contents_before_safety, top_name)
                    ParityRemoval = RemoveParity(top_module_declaration_content)
                    if is_safe:
                        top_module_declaration_content = ParityRemoval._remove_port()
                    module_whole_content = ParityRemoval._remove_assignment(module_whole_content, extra_outport_name)
                    cleaned_top_module_declaration_content = CommentProcess(
                        top_module_declaration_content).remove_comments().strip()
                    if cleaned_top_module_declaration_content.endswith(","):
                        top_module_declaration_content = remove_dcls_port(top_module_declaration_content)

                    hash_indices = [index for index, char in enumerate(top_module_declaration_content) if char == '#']
                    comment_processor = CommentProcess(top_module_declaration_content)
                    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
                    param_usage = filter_ip_index(hash_indices, multi_cmt_indices, single_cmt_indices, 1)
                    top_param_declaration, top_port_declaration = module_declaration_partition(
                        top_module_declaration_content,
#                        param_usage=False)
                        param_usage=param_usage)

                    PortExtractor = ExtractPort(top_port_declaration, top_module_whole_content)
                    port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
                    module_declaration_content = f"module {top_name} "
                    if top_param_declaration:
                        module_declaration_content += "#(\n" + top_param_declaration + "\n)"
                    
                    # Extract input and output ports from parity module to add to top module declaration
                    # Only add ports that are not already declared in top module
                    parity_extra_inports = extract_parity_input_ports(ip, Parity_generator, top_port_declaration)
                    parity_extra_outports = extract_parity_output_ports(ip, Parity_generator, top_port_declaration)
                    
                    # Add parity input/output ports to module declaration
                    module_declaration_content += "(\n" + declare_parity_port_2001(
                        port_declaration_2001=top_port_declaration,
                        ANSI_C=ANSI_C_port,
                        extra_inport=parity_extra_inports,
                        extra_outport=parity_extra_outports) + "\n);\n"
                    # NOTE: declare_parity_port_1995 is deprecated - ANSI-C style (2001) is sufficient

                    # Add instance - only if not already exists
                    instance_name = f"u_{top_name.lower()}_ip_parity_gen"
                    if instance_name not in module_whole_content:
                        # Parse parity module to get ALL ports
                        parity_module_ports = extract_parity_module_ports(ip, Parity_generator)
                        if parity_module_ports:
                            instance_content = f"\n{top_name}_IP_PARITY_GEN u_{top_name.lower()}_ip_parity_gen ("
                            port_connections = []
                            for parity_port_name in parity_module_ports:
                                # Map clock/reset ports from top module
                                if parity_port_name == "I_CLK":
                                    top_port_name = "ACLK"
                                elif parity_port_name == "I_RESETN":
                                    top_port_name = "RESETN_ACLK"
                                else:
                                    top_port_name = parity_port_name
                                port_connections.append(f".{parity_port_name} ({top_port_name})")
                            
                            instance_content += "\n    " + ",\n    ".join(port_connections) + "\n);\n"
                            module_whole_content = module_whole_content[:-9] + instance_content + "endmodule"
                        else:
                            print(f"Warning: Could not extract ports from parity module for IP {ip}")
                            module_whole_content = module_whole_content
                    else:
                        print(f"Instance {instance_name} already exists in {top_name}, skipping instance addition")
                        module_whole_content = module_whole_content
                    top_file_contents = module_declaration_content + module_whole_content

                    # par_dir = f"./DCLS_generator/module_parity/BUS_PARITY_{top_name}_TOP.v"
                    # par_file = open(par_dir, 'w')
                    # par_file.write(before_top_file_contents + top_file_contents + after_top_file_contents)

                    file_name = top_file_dir.split('/')[-1][:-2] if top_file_dir.endswith('.v') else \
                    top_file_dir.split('/')[-1][:-3]
                    extension = top_file_dir.split('.')[-1]
                    
                    # Generate top wrapper only if gen_top flag is set
                    if gen_top:
                        par_dir = remove_after_pattern(
                            "/".join(top_file_dir.split('/')[:-1])) + f"/SAFETY/{file_name}_NEW.{extension}"
                        par_file = open(par_dir, 'w')
                        par_file.write(before_top_file_contents + top_file_contents + after_top_file_contents)
                        print(bcolors.OKGREEN + f"Finished swapping original with paritied module {par_dir}" + bcolors.ENDC)

                    par_dir = remove_after_pattern(
                        "/".join(top_file_dir.split('/')[:-1])) + f"/SAFETY/{file_name}_PARITY_NEW.{extension}"
                    par_file = open(par_dir, 'w')
                    par_file.write(Parity_generator._generate_module_ip(ip))
                    print(bcolors.OKGREEN + f"Finished creating parity module {par_dir}" + bcolors.ENDC)
                Parity_generator._reset_generator()

        elif parity_scheme == "SAFETY.REGISTER PARITY":
            ip_filelist_dict = {}
            if info_dict_list:
                for info_dict in info_dict_list:
                    Parity_INFOExtractor = ExtractINFO_Parity_Register(info_dict)
                    ip_filelist_dict[
                        Parity_INFOExtractor._extract_ip_name()] = Parity_INFOExtractor._extract_filelist_list_ip()
                    Parity_generator = GenerateRegister(Parity_INFOExtractor)
                    Parity_generator._wrapper_reg()

                port_list = Parity_generator._list_port_ip()
                original_inport, extra_inport, extra_outport = [], [], []
                for ip, lst in port_list.items():
                    print("IP: ", ip)
                    original_inport, extra_inport, extra_outport = lst

                    # top_hier_wrapper
                    top_name = ip
                    file_list_list = ip_filelist_dict[ip]
                    file_list = recursive_find_v(file_list_list)
                    file_set = set(file_list)
                    file_set_env = path_env(file_set)
                    _, top_file_dir = recursive_read_v(file_set_env, top_name)
                    print(f"Target top module '{top_name}' is found at '{top_file_dir}'")
                    with open(top_file_dir, 'r') as file:
                        top_file_contents_ori = file.read()

                    ModuleLocator = LocateModule(top_file_contents_ori, top_name)
                    before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

                    # Add error ports to top module
                    top_file_contents_before_safety = top_file_contents
                    _, module_whole_content = module_partition(top_file_contents, top_name)

                    top_module_declaration_content, top_module_whole_content = module_partition(
                        top_file_contents_before_safety,
                        top_name)
                    top_param_declaration, top_port_declaration = module_declaration_partition(
                        top_module_declaration_content,
                        param_usage=False)

                    PortExtractor = ExtractPort(top_port_declaration, top_module_whole_content)
                    port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
                    module_declaration_content = f"module {top_name}_PARITY "
                    if top_param_declaration:
                        module_declaration_content += "#(\n" + top_param_declaration + "\n)"
                    module_declaration_content += "(\n" + declare_parity_port_2001(
                        port_declaration_2001=top_port_declaration,
                        ANSI_C=ANSI_C_port,
                        extra_inport=extra_inport,
                        extra_outport=extra_outport) + "\n);\n"
                    module_declaration_content += "\n" + declare_parity_port_1995(
                        port_declaration_1995=port_declaration_1995,
                        ANSI_C=ANSI_C_port,
                        extra_inport=extra_inport,
                        extra_outport=extra_outport) + "\n"

                    # Add logic
                    parity_content = ""
                    parity_content += GenerateRegister.valid_blk[top_name]

                    instance_content = ""
                    # Add instance
                    all_port = original_inport + extra_inport + extra_outport
                    instance_content += f"{top_name}_REG_PARITY_GEN u_{top_name.lower()}_reg_parity_gen ("
                    for port in all_port:
                        instance_content += f"\n    .{port[1]} ({port[1]}),"
                    instance_content = instance_content[:-1] + "\n);\n"

                    module_whole_content = module_whole_content[
                                           :-9] + instance_content + parity_content + "\n\nendmodule"
                    top_file_contents = module_declaration_content + module_whole_content
                    par_dir = f"./DCLS_generator/module_parity/REGISTER_PARITY_{top_name}_TOP.v"
                    par_file = open(par_dir, 'w')
                    par_file.write(before_top_file_contents + top_file_contents + after_top_file_contents)
                par_dir = f"./DCLS_generator/module_parity/REGISTER_PARITY.v"
                par_file = open(par_dir, 'w')
                par_file.write(Parity_generator._generate_module_reg())

        else:
            raise ValueError("Invalid Parity scheme")
