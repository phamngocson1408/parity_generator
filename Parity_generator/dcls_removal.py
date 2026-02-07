import os
import sys
import argparse

from Parity_generator.common.prettycode import bcolors
from Parity_generator.moduleParser.recursive_read import *
from Parity_generator.function_wrapper.dcls_wrappers import *

from Parity_generator.ClassLocateIP.LocateModule import LocateModule
from Parity_generator.GenerateVerilog.GenerateDCLS import GenerateDCLS
from Parity_generator.RemoveVerilog.RemoveDCLS import RemoveDCLS

from Parity_generator.ClassExtractData.ExtractPort import ExtractPort
from Parity_generator.ClassExtractData.ExtractParam import ExtractParam
from Parity_generator.ClassExtractData.ExtractInport import ExtractInport
from Parity_generator.ClassExtractData.ExtractOutport import ExtractOutport

from Parity_generator.ClassStats.StatsClass import StatsClass
from Parity_generator.ClassExtractINFO.ExtractINFO import ExtractINFO
from Parity_generator.ClassExtractINFO.ExtractINFO_DCLS import ExtractINFO_DCLS

import re

from Parity_generator.ClassLocateIP.LocateInstance import LocateInstance
from Parity_generator.instanceModifier.modify_instance import remove_dcls_signal, remove_dcls_port
from Parity_generator.moduleCreator.declare_port import declare_dcls_port_2001, declare_dcls_port_1995
from Parity_generator.moduleParser.depart_module.depart_module import module_partition, module_declaration_partition

generatorPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(generatorPath, '../'))


if __name__ == "__main__":
    # ---------------------------------------------------------------------------
    # arguments parsing: From 2023/05, use Excel instead of arguments
    # ---------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='DCLS removal v1 by Tho Mai (2024.07)')

    # Additional arguments for extra features
    parser.add_argument('-op', '--output_path'  , type=str, default='module_dcls', help='Path to output files')
    parser.add_argument("-info", type=str, help="INFO file path")

    args = parser.parse_args()

    # Parsing arguments using Excel INFO file
    # INFO_path = './Parity_generator/[INFO]_DCLS_TEMPLATE.xlsx'
    if args.info:
        INFO_path = args.info
    else:
        INFO_path = './[INFO]_DCLS_TEMPLATE_AXIDMA_single.xlsx'

    INFOExtractor = ExtractINFO(INFO_path, "SAFETY.DCLS")
    info_dict_list = INFOExtractor._read_info_multi()

    for info_dict in info_dict_list:
        DCLS_INFOExtractor = ExtractINFO_DCLS(info_dict)
        DCLS_Removal = RemoveDCLS(DCLS_INFOExtractor)
        file_list_list = DCLS_INFOExtractor._extract_filelist_list()
        top_name, dup_name, _ = DCLS_INFOExtractor._extract_ip()

        # top_file_dir = '../module_dcls/BOS_AXIDMA_NEW.v'
        file_list = recursive_find_v(file_list_list)
        file_set = set(file_list)
        file_set_env = path_env(file_set)
        _, top_file_dir = recursive_read_v(file_set_env, top_name)
        print(f"Target top module '{top_name}' is found at '{top_file_dir}'")

        with open(top_file_dir, 'r') as file:
            top_file_contents = file.read()

        ModuleLocator = LocateModule(top_file_contents, top_name)

        top_file_dir = dcls_removal(top_name=top_name, dup_name=dup_name, output_path="/".join(top_file_dir.split('/')[:-1]),
                                    ModuleLocator=ModuleLocator, DCLS_Removal=DCLS_Removal)

"""
        before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

        # top_file_contents_before_safety = top_file_contents
        module_declaration_content, module_whole_content = module_partition(top_file_contents, top_name)
        top_module_declaration_content, top_module_whole_content = module_partition(top_file_contents, top_name)
        top_param_declaration, top_port_declaration = module_declaration_partition(top_module_declaration_content,
                                                                                   param_usage=False)


        # PortExtractor = ExtractPort(top_port_declaration, top_module_whole_content)
        # port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
        module_declaration_content = f"module {top_name}_NEW "
        if top_param_declaration:
            module_declaration_content += "#(\n" + top_param_declaration + "\n)"

        module_declaration_content += "\n(\n" + DCLS_Removal._remove_port_declaration(top_port_declaration) + "\n);\n"

        top_file_contents = module_declaration_content + module_whole_content
        # print(top_file_contents)

        # Add error connections to instance
        InstanceLocator = LocateInstance(top_file_contents, f"{dup_name}_DCLS")
        before_instance_content, instance_content, after_instance_content = InstanceLocator._separate_ip()
        # print(instance_content)
        modified_instance_content = DCLS_Removal._remove_instance_declaration(dup_name, instance_content)
        top_file_contents_ori = before_instance_content + modified_instance_content + after_instance_content
        top_file_contents_ori = DCLS_Removal._remove_assignment(top_file_contents_ori)
        # print(before_top_file_contents + before_instance_content + modified_instance_content + after_instance_content + after_top_file_contents)
        top_dc_dir = os.path.join(generatorPath, args.output_path, f"{top_name}_REVERT.v")
        print(top_dc_dir)
        top_file = open(top_dc_dir, 'w')
        top_file.write(before_top_file_contents + top_file_contents_ori + after_top_file_contents)
"""
