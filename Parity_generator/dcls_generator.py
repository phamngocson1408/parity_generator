import os
import sys
import argparse

from Parity_generator.common.prettycode import bcolors
from Parity_generator.common.find_bracket import remove_after_pattern, remove_from_pattern
from Parity_generator.moduleParser.recursive_read import *
from Parity_generator.function_wrapper.dcls_wrappers import *

from Parity_generator.GenerateVerilog.GenerateDCLS import GenerateDCLS

from Parity_generator.ClassExtractData.ExtractPort import ExtractPort
from Parity_generator.ClassExtractData.ExtractParam import ExtractParam
from Parity_generator.ClassExtractData.ExtractInport import ExtractInport
from Parity_generator.ClassExtractData.ExtractOutport import ExtractOutport

from Parity_generator.ClassStats.StatsClass import StatsClass
from Parity_generator.ClassExtractINFO.ExtractINFO import ExtractINFO
from Parity_generator.ClassExtractINFO.ExtractINFO_DCLS import ExtractINFO_DCLS

from Parity_generator.moduleParser.comment_process import CommentProcess


generatorPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(generatorPath, '../'))


if __name__ == "__main__":
    # ---------------------------------------------------------------------------
    # arguments parsing: From 2023/05, use Excel instead of arguments
    # ---------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='DCLS generator v3 by Tho Mai (2024.05.31)')

    # Additional arguments for extra features
    parser.add_argument("-info", type=str, help="INFO file path")

    args = parser.parse_args()

    # Parsing arguments using Excel INFO file
    INFO_path = args.info

    INFOExtractor = ExtractINFO(INFO_path, "SAFETY.DCLS")
    info_dict_list = INFOExtractor._read_info_multi()

    for info_dict in info_dict_list:
        print("----------------------------------------------------")
        DCLS_INFOExtractor = ExtractINFO_DCLS(info_dict)
        clk, rst, r2d = DCLS_INFOExtractor._extract_clk_rst()
        file_list_list = DCLS_INFOExtractor._extract_filelist_list()
        top_module, dup_name, dup_path = DCLS_INFOExtractor._extract_ip()
        dup_error = DCLS_INFOExtractor._is_error_double()
        ip_err_port, dup_err_port = DCLS_INFOExtractor._extract_err_port()
        fault_list = DCLS_INFOExtractor._extract_fault_injection()
        ignore_list = DCLS_INFOExtractor._extract_ignore_list()
        _, gated_list, _ = DCLS_INFOExtractor._extract_gate_list()

        file_list = recursive_find_v(file_list_list)
        file_set = set(file_list)
        file_set_env = path_env(file_set)

        _, dup_file_dir = recursive_read_v(file_set_env, dup_name)
        print(f"Target dc module '{dup_name}' is found at '{dup_file_dir}'")

        # ---------------------------------------------------------------------------
        # Parsing data in the targeted module for duplication
        # ---------------------------------------------------------------------------
        with open(dup_file_dir, 'r') as file:
            file_contents = file.read()

        # Separate module into multiple parts
        module_declaration_content, module_whole_content = module_partition(file_contents, dup_name)
        assert module_declaration_content is not None and module_whole_content is not None

        hash_indices = [index for index, char in enumerate(module_declaration_content) if char == '#']
        comment_processor = CommentProcess(module_declaration_content)
        multi_cmt_indices, single_cmt_indices = comment_processor.find_comments()
        param_usage = filter_ip_index(hash_indices, multi_cmt_indices, single_cmt_indices, 1)
        # param_usage = True if '#' in module_declaration_content else False
        param_declaration, port_declaration = module_declaration_partition(module_declaration_content, param_usage=param_usage)

        # ---------------------------------------------------------------------------
        # Extract information from the departed parts: Param, Input, Output
        # ---------------------------------------------------------------------------
        # Input
        InPutExtractor = ExtractInport(port_declaration, module_whole_content)
        parsed_inport, parsed_clk_rst = InPutExtractor._extract_clk_rst(clk, rst)
        # Output
        OutPutExtractor = ExtractOutport(port_declaration, module_whole_content)
        parsed_outport = OutPutExtractor._extract_dimension()
        # Param
        ParamExtractor = ExtractParam(param_declaration, module_whole_content)
        parsed_param = ParamExtractor._extract_value()

        # ---------------------------------------------------------------------------
        # Supporting functions
        # ---------------------------------------------------------------------------
        # 2 port declaration styles
        PortExtractor = ExtractPort(port_declaration, module_whole_content)
        port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()

        param_declaration_1995, ANSI_C_param = ParamExtractor._extract_declaration_valid()

        # Generator Class
        DCLS_Generator = GenerateDCLS(dup_name, parsed_param, [clk, rst], parsed_inport, parsed_outport, DCLS_INFOExtractor)

        intro_block = """/*
    BOS Semiconductors
    Tho Mai
    Auto generated DCLS module
*/
    """

        # ---------------------------------------------------------------------------
        # DCLS-ed module generation
        # ---------------------------------------------------------------------------
        valid_parsed_port = [port for port in parsed_inport+parsed_outport if port[1] not in ignore_list]
        ungated_valid_parsed_port = [port for port in valid_parsed_port if port[1] not in gated_list]

        StatsAnalyzer = StatsClass(parsed_param, valid_parsed_port)
        print(bcolors.OKBLUE + f"Total added FF for DCLS is: {StatsAnalyzer._count_ff()}" + bcolors.ENDC)
        UnGatedStatsAnalyzer = StatsClass(parsed_param, ungated_valid_parsed_port)
        print(bcolors.OKBLUE + f"Total added Ungated FF for DCLS is: {UnGatedStatsAnalyzer._count_ff()}" + bcolors.ENDC)

        dcls_block = dc_wrapper(dup_name=dup_name, dup_err=dup_error, dup_err_port=dup_err_port, r2d=r2d, fierr=fault_list[0],
                                ParamExtractor=ParamExtractor, param_declaration=param_declaration,
                                PortExtractor=PortExtractor, port_declaration=port_declaration,
                                DCLS_Generator=DCLS_Generator, StatsAnalyzer=StatsAnalyzer)

        # Write to file
        file_name = dup_file_dir.split('/')[-1][:-2] if dup_file_dir.endswith('.v') else dup_file_dir.split('/')[-1][:-3]
        extension = dup_file_dir.split('.')[-1]
        dc_dir = remove_after_pattern("/".join(dup_file_dir.split('/')[:-1])) + f"/SAFETY/{file_name}_DCLS_NEW.{extension}"
        try:
            dcls_file = open(dc_dir, 'w')
        except:
            subprocess.run(["mkdir", f"{dc_dir.replace(f'{file_name}_DCLS_NEW.v', '')}"])
            dcls_file = open(dc_dir, 'w')
        dcls_file.write(dcls_block)
        print(bcolors.OKGREEN + f"Finished creating duplicated module {dc_dir}" + bcolors.ENDC)

