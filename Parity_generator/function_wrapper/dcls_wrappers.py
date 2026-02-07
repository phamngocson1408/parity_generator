import os
from typing import Optional

from Parity_generator.RemoveVerilog.RemoveDCLS import RemoveDCLS
from Parity_generator.moduleParser.depart_module.depart_module import *

from Parity_generator.instanceModifier.modify_instance import *
from Parity_generator.moduleCreator.declare_param import *
from Parity_generator.moduleCreator.declare_port import *

from Parity_generator.moduleCreator.insert_verification import insert_error_connection

from Parity_generator.GenerateVerilog.GenerateDCLS import GenerateDCLS
from Parity_generator.ClassStats.StatsClass import StatsClass

from Parity_generator.ClassExtractData.ExtractPort import ExtractPort
from Parity_generator.ClassExtractData.ExtractParam import ExtractParam

from Parity_generator.ClassLocateIP.LocateModule import LocateModule
from Parity_generator.ClassLocateIP.LocateInstance import LocateInstance
from Parity_generator.ClassLocateIP.LocateIntanceU import LocateInstanceU

from Parity_generator.moduleParser.comment_process import CommentProcess

from Parity_generator.moduleParser.parse_module.extract_port_from_instance import separate_instance, extract_port_signal_direction


def dc_wrapper(dup_name: str, dup_err: bool, dup_err_port: str, r2d: str, fierr: str,
               ParamExtractor: ExtractParam, param_declaration: str,
               PortExtractor: ExtractPort, port_declaration: str,
               DCLS_Generator: GenerateDCLS, StatsAnalyzer: Optional[StatsClass] = None) -> str:

    port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
    param_declaration_1995, ANSI_C_param = ParamExtractor._extract_declaration_valid()

    dcls_block = "`timescale 1ns/1ps"
    # Module declaration
    dcls_block += f"\nmodule {dup_name}_DCLS "
    # Module parameter if available
    if ANSI_C_param:
        dcls_block += "#(" + param_declaration + ")"
    # Module port declaration
    dcls_block += "(" + "\n"
    dcls_block += declare_dcls_port_2001(top=dup_name, port_declaration_2001=port_declaration, dup_err_port=dup_err_port, r2d=r2d, fierr=fierr, ANSI_C=ANSI_C_port, dup_err=dup_err)
    dcls_block += ");" + "\n"
    # Param and port 1995 styles
    dcls_block += declare_param_1995(param_declaration_1995=param_declaration_1995, ANSI_C=ANSI_C_param) + '\n'
    dcls_block += declare_dcls_port_1995(top=dup_name, port_declaration_1995=port_declaration_1995, dup_err_port=dup_err_port, r2d=r2d, fierr=fierr, ANSI_C=ANSI_C_port, dup_err=dup_err)
    # Wire and reg declaration
    dcls_block += DCLS_Generator._generate_wire() + "\n"
    dcls_block += DCLS_Generator._generate_reg(level=2) + "\n"
    # Delay
    dcls_block += DCLS_Generator._generate_delay(level=2)
    # Module instances
    dcls_block += "\n" + DCLS_Generator._generate_instance(rst_2d=r2d) + "\n"
    dcls_block += "\n" + DCLS_Generator._generate_instance(rst_2d=r2d, duplicate=True) + "\n"
    # Error check
    dcls_block += DCLS_Generator._inject_error() + "\n\n"
    dcls_block += DCLS_Generator._generate_error_check() + DCLS_Generator._generate_error_mask()
    # Module end
    dcls_block += "endmodule"

    return dcls_block


def top_hier_wrapper(top_name: str, dup_name: str, ip_err_port: str, dup_err_port: str, dup_err: bool, r2d: str, fierr: str,
                     ModuleLocator: LocateModule, multi_level=False) -> str:
    before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

    # Add error ports to top module
    top_file_contents_before_safety = top_file_contents
    module_declaration_content, module_whole_content = module_partition(top_file_contents, top_name)

    top_module_declaration_content, top_module_whole_content = module_partition(top_file_contents_before_safety,
                                                                                top_name)
    assert top_module_declaration_content is not None and top_module_whole_content is not None
    hash_indices = [index for index, char in enumerate(top_module_declaration_content) if char == '#']
    comment_processor = CommentProcess(top_module_declaration_content)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    param_usage = filter_ip_index(hash_indices, multi_cmt_indices, single_cmt_indices, 1)
    # param_usage = True if '#' in top_module_declaration_content else False
    
    top_param_declaration, top_port_declaration = module_declaration_partition(top_module_declaration_content,
                                                                               param_usage)

    PortExtractor = ExtractPort(top_port_declaration, top_module_whole_content)
    port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
    module_declaration_content = f"module {top_name}"
    if top_param_declaration:
#        module_declaration_content += "#(\n" + top_param_declaration + "\n)"
        module_declaration_content += "#(" + top_param_declaration + ")"

    if multi_level:
        intermediate_err_port = ip_err_port
    else:
        intermediate_err_port = dup_err_port

    module_declaration_content += "(\n" + declare_dcls_port_2001(top=top_name, dup_err_port=intermediate_err_port,
                                                                 port_declaration_2001=top_port_declaration, r2d=r2d, fierr=fierr, 
                                                                 ANSI_C=ANSI_C_port, dup_err=dup_err) + "\n);\n"
    module_declaration_content += "\n" + declare_dcls_port_1995(top=top_name, dup_err_port=intermediate_err_port,
                                                                port_declaration_1995=port_declaration_1995, r2d=r2d, fierr=fierr,
                                                                ANSI_C=ANSI_C_port, dup_err=dup_err) + "\n"

    top_file_contents = module_declaration_content + module_whole_content
    # print(top_file_contents)

    # Add error connections to instance
    if multi_level:
        InstanceLocator = LocateInstanceU(top_file_contents, dup_name)
    else:
        InstanceLocator = LocateInstance(top_file_contents, dup_name)
    before_instance_content, instance_content, after_instance_content = InstanceLocator._separate_ip()

    modified_instance_content = add_dcls_signal(dup_design=dup_err_port, top_design=intermediate_err_port, instance_content=instance_content, rst_2d=r2d, fierr=fierr, dup_err=dup_err)

    if multi_level is False:
        modified_instance_content = change_instance_name(modified_instance_content, dup_name)

    return before_top_file_contents + before_instance_content + modified_instance_content + after_instance_content + after_top_file_contents


def top_flat_wrapper(top_name: str, dup_name: str, ip_err_port: str, dup_err_port: str, dup_err: bool, r2d: str, fierr: str, dup_path: str,
                     ModuleLocator: LocateModule, StatsAnalyzer: StatsClass, DCLS_Generator: GenerateDCLS) -> str:
    before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

    # Add error ports to top module
    top_file_contents_before_safety = top_file_contents
    module_declaration_content, module_whole_content = module_partition(top_file_contents, top_name)

    InstanceLocator = LocateInstance(top_file_contents, dup_name)
    before_instance_content, instance_content, after_instance_content = InstanceLocator._separate_ip()
    param_override, port_connection = separate_instance(instance_content, dup_name, dup_path)
    port_signal_dict = extract_port_signal_direction(port_connection)

    top_module_declaration_content, top_module_whole_content = module_partition(top_file_contents_before_safety,
                                                                                top_name)
    top_param_declaration, top_port_declaration = module_declaration_partition(top_module_declaration_content,
                                                                               param_usage=False)

    PortExtractor = ExtractPort(top_port_declaration, top_module_whole_content)
    port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
    module_declaration_content = f"module {top_name}_FLAT "
    if top_param_declaration:
        module_declaration_content += "#(\n" + top_param_declaration + "\n)"
    module_declaration_content += "(\n" + declare_dcls_port_2001(top=top_name, dup_err_port=ip_err_port,
                                                                 port_declaration_2001=top_port_declaration, r2d=r2d, fierr=fierr, 
                                                                 ANSI_C=ANSI_C_port, dup_err=dup_err) + "\n);\n"
    module_declaration_content += "\n" + declare_dcls_port_1995(top=top_name, dup_err_port=ip_err_port,
                                                                port_declaration_1995=port_declaration_1995, r2d=r2d, fierr=fierr,
                                                                ANSI_C=ANSI_C_port, dup_err=dup_err) + "\n"

    top_file_contents = module_declaration_content + module_whole_content
    # print(top_file_contents)

    # Add error connections to instance
    InstanceLocator = LocateInstance(top_file_contents, dup_name)
    before_instance_content, instance_content, after_instance_content = InstanceLocator._separate_ip()

    mapped_wire_block = DCLS_Generator._generate_wire(StatsAnalyzer=StatsAnalyzer, port_sig_dict=port_signal_dict)
    mapped_reg_block = DCLS_Generator._generate_reg(StatsAnalyzer=StatsAnalyzer, port_sig_dict=port_signal_dict)
    mapped_delay_block = DCLS_Generator._generate_delay(level=2, port_sig_dict=port_signal_dict)

    mapped_instance_block = DCLS_Generator._generate_instance(rst_2d=r2d, param_override=param_override,
                                                              port_sig_dict=port_signal_dict) + "\n"
    mapped_instance_block += "\n"
    mapped_instance_block += DCLS_Generator._generate_instance(rst_2d=r2d, param_override=param_override,
                                                               port_sig_dict=port_signal_dict, duplicate=True) + "\n"
    mapped_instance_block += "\n"
    mapped_error_block = DCLS_Generator._inject_error(StatsAnalyzer=StatsAnalyzer, port_sig_dict=port_signal_dict) + "\n\n"
    # mapped_error_block += DCLS_Generator._generate_error_check(port_sig_dict=port_signal_dict) \
    #                      + DCLS_Generator._generate_error_mask(port_sig_dict=port_signal_dict) \
    #                      + insert_error_connection(instance_name=dup_err_port, top_name=ip_err_port) + '\n'
    mapped_error_block += DCLS_Generator._generate_error_check(port_sig_dict=port_signal_dict) \
                         + DCLS_Generator._generate_error_mask(port_sig_dict=port_signal_dict) + '\n'
    

    modified_instance_content = mapped_wire_block + mapped_reg_block + mapped_delay_block + mapped_instance_block + mapped_error_block

    return before_top_file_contents + before_instance_content + modified_instance_content + after_instance_content + after_top_file_contents


def dcls_removal(top_name: str, dup_name: str, output_path: str,
                 ModuleLocator: LocateModule, DCLS_Removal: RemoveDCLS, multi_level=False, multi=False):
    before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

    module_declaration_content, module_whole_content = module_partition(top_file_contents, top_name)
    top_module_declaration_content, top_module_whole_content = module_partition(top_file_contents, top_name)
    assert top_module_declaration_content is not None and top_module_whole_content is not None
    hash_indices = [index for index, char in enumerate(top_module_declaration_content) if char == '#']
    comment_processor = CommentProcess(top_module_declaration_content)
    multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
    param_usage = filter_ip_index(hash_indices, multi_cmt_indices, single_cmt_indices, 1)
    top_param_declaration, top_port_declaration = module_declaration_partition(top_module_declaration_content,
                                                                               param_usage)

    # PortExtractor = ExtractPort(top_port_declaration, top_module_whole_content)
    # port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
    module_declaration_content = f"module {top_name}"
    if top_param_declaration:
        module_declaration_content += "#(\n" + top_param_declaration + "\n)"

    module_declaration_content += "\n(\n" + DCLS_Removal._remove_port_declaration(top_port_declaration) + "\n);\n"

    top_file_contents = module_declaration_content + module_whole_content
    # print(top_file_contents)

    # Remove error connections from instance
    if multi_level:
        InstanceLocator = LocateInstanceU(top_file_contents, f"{dup_name}")
    else:
        if multi:
            InstanceLocator = LocateInstanceU(top_file_contents, f"{dup_name}")
        else:
            InstanceLocator = LocateInstance(top_file_contents, f"{dup_name}_DCLS")
    before_instance_content, instance_content, after_instance_content = InstanceLocator._separate_ip()
    # Rename instance (dcls -> original)
    modified_instance_content = DCLS_Removal._remove_instance_declaration(dup_name, instance_content)
    top_file_contents_ori = before_instance_content + modified_instance_content + after_instance_content
    top_file_contents_ori = DCLS_Removal._remove_assignment(top_file_contents_ori)
    # print(before_top_file_contents + before_instance_content + modified_instance_content + after_instance_content + after_top_file_contents)
    top_dc_dir = os.path.join(output_path, f"{top_name}_REVERT.v")
    # print(top_dc_dir)
    top_file = open(top_dc_dir, 'w')
    top_file.write(before_top_file_contents + top_file_contents_ori + after_top_file_contents)
    print("Revert file is written to ", top_dc_dir)
    return top_dc_dir


def filter_ip_index(match_indices: list, multi_cmt_indices: list, single_cmt_indices: list, match_no=None):
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

    if match_no and filtered_match_index:
        assert len(filtered_match_index) == match_no, f"Expected exactly {match_no} match(es) but found {len(filtered_match_index)}."
    
    if len(filtered_match_index) == 0:
        return False
    else:
        return True

