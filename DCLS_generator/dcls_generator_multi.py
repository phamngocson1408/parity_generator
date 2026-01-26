import os
import sys
import argparse

from DCLS_generator.ClassLocateIP.LocateIntanceU import LocateInstanceU
from DCLS_generator.common.prettycode import bcolors
from DCLS_generator.common.version_ctrl import md5_of_file
from DCLS_generator.common.find_bracket import remove_after_pattern
from DCLS_generator.moduleParser.recursive_read import *
from DCLS_generator.function_wrapper.dcls_wrappers import *

from DCLS_generator.ClassLocateIP.LocateModule import LocateModule
from DCLS_generator.GenerateVerilog.GenerateDCLS import GenerateDCLS
from DCLS_generator.GenerateEnv.GenerateFM import GenerateFM
from DCLS_generator.RemoveVerilog.RemoveDCLS import RemoveDCLS

from DCLS_generator.ClassExtractData.ExtractPort import ExtractPort
from DCLS_generator.ClassExtractData.ExtractParam import ExtractParam
from DCLS_generator.ClassExtractData.ExtractInport import ExtractInport
from DCLS_generator.ClassExtractData.ExtractOutport import ExtractOutport

from DCLS_generator.ClassStats.StatsClass import StatsClass
from DCLS_generator.ClassExtractINFO.ExtractINFO import ExtractINFO
from DCLS_generator.ClassExtractINFO.ExtractINFO_DCLS import ExtractINFO_DCLS

from DCLS_generator.moduleParser.comment_process import CommentProcess


generatorPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(generatorPath, '../'))

# Get the absolute path to the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory of the script
parent_dir = os.path.dirname(script_dir)

# Add parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    multi=True
    # ---------------------------------------------------------------------------
    # arguments parsing: From 2024/05, use Excel instead of arguments
    # ---------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='DCLS generator v3 by Tho Mai (2024.05.31)')

    # Additional arguments for extra features
    parser.add_argument('-top', '--connect_to_top', action='store_true', help='Connect DCLS to top')
    parser.add_argument("-info", type=str, help="INFO file path")

    args = parser.parse_args()

    # Parsing arguments using Excel INFO file
    INFO_path = args.info
    script_version = "0.1.0"
    file_version = f"// MD5@INFO : {md5_of_file(INFO_path)}\n// Version@Script : {script_version}\n\n"

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
        is_wrap = DCLS_INFOExtractor._is_wrap()
        fault_list = DCLS_INFOExtractor._extract_fault_injection()
        ignore_list = DCLS_INFOExtractor._extract_ignore_list()
        _, gated_list, _ = DCLS_INFOExtractor._extract_gate_list()
        default_list = DCLS_INFOExtractor._extract_default_list()

        # For FM env generation
        fm_design_name = top_module if args.connect_to_top else dup_name
        fm_filelist = file_list_list
        fm_design_path = []


        is_safe = False

        file_list = recursive_find_v(file_list_list)
        file_set = set(file_list)
        file_set_env = path_env(file_set)

        _, dup_file_dir = recursive_read_v(file_set_env, dup_name)
        print(f"Target dc module '{dup_name}' is found at '{dup_file_dir}'")

        _, top_file_dir = recursive_read_v(file_set_env, top_module)
        print(f"Target top module '{top_module}' is found at '{top_file_dir}'")

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
        parsed_param_local = ParamExtractor._extract_value_local()

        # ---------------------------------------------------------------------------
        # Supporting functions
        # ---------------------------------------------------------------------------
        # 2 port declaration styles
        PortExtractor = ExtractPort(port_declaration, module_whole_content)
        port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()

        param_declaration_1995, ANSI_C_param = ParamExtractor._extract_declaration_valid()

        # Generator Class
        DCLS_Generator = GenerateDCLS(dup_name, parsed_param, [clk, rst], parsed_inport, parsed_outport, DCLS_INFOExtractor)
        DCLS_Removal = RemoveDCLS(DCLS_INFOExtractor)

        intro_block = """/*
    BOS Semiconductors
    Tho Mai
    Auto generated DCLS module
*/
    """

        if is_wrap:
            # ---------------------------------------------------------------------------
            # DCLS-ed module generation
            # ---------------------------------------------------------------------------
            valid_parsed_port = [port for port in parsed_inport+parsed_outport if port[1] not in ignore_list]
            ungated_valid_parsed_port = [port for port in valid_parsed_port if port[1] not in gated_list]
            
#            StatsAnalyzer = StatsClass(parsed_param, valid_parsed_port)
            StatsAnalyzer = StatsClass(parsed_param_local, valid_parsed_port)
            print(bcolors.OKBLUE + f"Total added FF for DCLS is: {StatsAnalyzer._count_ff()}" + bcolors.ENDC)
#            UnGatedStatsAnalyzer = StatsClass(parsed_param, ungated_valid_parsed_port)
            UnGatedStatsAnalyzer = StatsClass(parsed_param_local, ungated_valid_parsed_port)
            print(bcolors.OKBLUE + f"Total added Ungated FF for DCLS is: {UnGatedStatsAnalyzer._count_ff()}" + bcolors.ENDC)

            dcls_block = dc_wrapper(dup_name=dup_name, dup_err=dup_error, dup_err_port=dup_err_port, r2d=r2d, fierr=fault_list[0],
                                    ParamExtractor=ParamExtractor, param_declaration=param_declaration,
                                    PortExtractor=PortExtractor, port_declaration=port_declaration,
                                    DCLS_Generator=DCLS_Generator, StatsAnalyzer=StatsAnalyzer)

            # Write to file
            file_name = dup_file_dir.split('/')[-1][:-2] if dup_file_dir.endswith('.v') else dup_file_dir.split('/')[-1][:-3]
            # dc_dir = os.path.join(generatorPath, args.output_path, f"{file_name}_DCLS_NEW_GATE.v")
            dc_dir = remove_after_pattern("/".join(dup_file_dir.split('/')[:-1])) + f"/SAFETY/{file_name}_DCLS_NEW.v"
            dcls_file = open(dc_dir, 'w')
            dcls_file.write(file_version + dcls_block)
            print(bcolors.OKGREEN + f"Finished creating duplicated module {dc_dir}" + bcolors.ENDC)
            # For FM
            fm_design_path.append(dc_dir)

            # ---------------------------------------------------------------------------
            # At TOP, swap the original module with the duplicated veresion
            # ---------------------------------------------------------------------------
            if args.connect_to_top:
                with open(top_file_dir, 'r') as file:
                    top_file_contents_ori = file.read()
                ModuleLocator = LocateModule(top_file_contents_ori, top_module)

                dcls_pattern = r'\b' + ip_err_port + r'\b'
#                print(dcls_pattern)
                if bool(re.search(dcls_pattern, top_file_contents_ori)):
#                    print(re.search(dcls_pattern, top_file_contents_ori))
                    is_safe = True

                top_file_dir_rm = []
                if is_safe:
                    ori_top_file_dir = top_file_dir
                    ori_top_module = top_module
                    ori_dup_name = dup_name

                    print(bcolors.OKGREEN + f"Removing DCLS on {top_module} starting from {top_file_dir}" + bcolors.ENDC)
                    # In the case of multi-level
                    dup_path_ins = dup_path.split(".")
                    if len(dup_path_ins) > 1:
                        print(bcolors.OKBLUE + f"There is hierarchy in Duplication instance path: {dup_path_ins}" + bcolors.ENDC)
                    for level in range(len(dup_path_ins)):
                        multi_level = False
                        # not the lowest
                        if level != len(dup_path_ins) - 1:
                            multi_level = True
                            dup_ins_name = dup_path_ins[level]
                            print(bcolors.OKBLUE + f"[Level {level + 1}] Instance: {dup_ins_name}, Module: {top_module}, File: {top_file_dir}" + bcolors.ENDC)
                        # the lowest (the one that calls dcls module)
                        else:
                            dup_ins_name = dup_path_ins[level]
                            print(bcolors.OKBLUE + f"[Final level] Instance: {dup_ins_name}, Module: {top_module}, File: {top_file_dir}" + bcolors.ENDC)

                        mid_module = instance_partition(top_file_contents_ori, dup_ins_name)
                        print(f"Module name of instance {dup_ins_name} is: {mid_module}")
                        file_list = recursive_find_v(file_list_list)
                        file_set = set(file_list)
                        file_set_env = path_env(file_set)
                        _, top_file_dir = recursive_read_v(file_set_env, top_module, multi_level)

                        with open(top_file_dir, 'r') as file:
                            top_file_contents_ori = file.read()
                        ModuleLocator = LocateModule(top_file_contents_ori, top_module)


                        print(f"Target top module '{top_module}' is found at '{top_file_dir}'")
                        print(f"Removing instance '{dup_ins_name}' from module '{top_module}' in file '{top_file_dir}'")
                        
                        top_file_dir_rm.append(dcls_removal(top_name=top_module, dup_name=dup_ins_name, output_path="/".join(top_file_dir.split('/')[:-1]), 
                                                            ModuleLocator=ModuleLocator, DCLS_Removal=DCLS_Removal, multi_level=multi_level, multi=multi))
                        print(top_file_dir)

                        top_module = mid_module

                    top_file_dir = ori_top_file_dir
                    top_module = ori_top_module
                    dup_name = ori_dup_name
                # For B0 only: Multi-level DCLS
                #              For simplicity, there is no multi-level SAFETY in A0, so is_safe should be False anyway
                # Description: Loop from higher hier to lower hier
                print(bcolors.OKGREEN + f"Adding DCLS to {top_module} starting from {top_file_dir}" + bcolors.ENDC)
                dup_path_ins = dup_path.split(".")
                if len(dup_path_ins) > 1:
                    print("There is hierarchy in Duplication instance path")
                for level in range(len(dup_path_ins)):
                    multi_level = False
                    # not the lowest
                    if level != len(dup_path_ins) - 1:
                        multi_level = True
                        dup_ins_name = dup_path_ins[level]
                        print(bcolors.OKBLUE + f"[Level {level + 1}] Instance: {dup_ins_name}, Module: {top_module}" + bcolors.ENDC)
                    # the lowest (the one that calls dcls module)
                    else:
                        dup_ins_name = dup_name
                        print(bcolors.OKBLUE + f"[Final level] Sub-module: {dup_ins_name}, Top-module: {top_module}" + bcolors.ENDC)



                    if is_safe:
                        top_file_dir = top_file_dir.split('.')[0] + "_REVERT.v"
                        print(f"Target top module '{top_module}' is found at '{top_file_dir}'")
                    else:
                        file_list = recursive_find_v(file_list_list)
                        file_set = set(file_list)
                        file_set_env = path_env(file_set)
                        _, top_file_dir = recursive_read_v(file_set_env, top_module)

                    # For top, this step is actually redundant
                    with open(top_file_dir, 'r') as file:
                        top_file_contents_ori = file.read()
                    ModuleLocator = LocateModule(top_file_contents_ori, top_module)

                    top_dcls_block = top_hier_wrapper(top_name=top_module, dup_name=dup_ins_name, ip_err_port=ip_err_port,
                                                      dup_err_port=dup_err_port, dup_err=dup_error, r2d=r2d,
                                                      fierr=fault_list[0],
                                                      ModuleLocator=ModuleLocator, multi_level=multi_level)

                    file_name = top_file_dir.split('/')[-1][:-2] if top_file_dir.endswith('.v') else \
                    top_file_dir.split('/')[-1][:-3]
                    file_name = file_name.replace("_REVERT", "")
                    # top_dc_dir = os.path.join(generatorPath, args.output_path, f"{file_name}_NEW.v")
                    top_dc_dir = remove_after_pattern("/".join(top_file_dir.split('/')[:-1])) + f"/SAFETY/{file_name}_NEW.v"
                    top_file = open(top_dc_dir, 'w')
                    top_file.write(file_version + top_dcls_block)
                    print(bcolors.OKGREEN + f"Finished swapping original with duplicated module {top_dc_dir}" + bcolors.ENDC)
                    # For FM
                    fm_design_path.append(top_dc_dir)

                    if multi_level and level != len(dup_path_ins) - 1:
                        InstanceLocatorU = LocateInstanceU(top_file_contents_ori, dup_ins_name)
                        instance_content = InstanceLocatorU._separate_ip()
                        match = re.search(r'\b\w+\b', instance_content[1])

                        top_module = match.group(0)
                        dup_ins_name = dup_path_ins[level+1]

            # FM generation
            FMGenrator = GenerateFM(fm_design_name, fm_filelist, fm_design_path)

        else:
            # ---------------------------------------------------------------------------
            # ----------------------------- Flat prototype ------------------------------
            # ---------------------------------------------------------------------------
            dup_path_ins = dup_path.split(".")
            if len(dup_path_ins) > 1:
                print(bcolors.FAIL + "FLAT mode is not supported for multi-level duplication, please re-run with 'dcls_generator'" + bcolors.ENDC)
                quit()
            StatsAnalyzer = StatsClass(parsed_param, parsed_inport + parsed_outport)
            with open(top_file_dir, 'r') as file:
                top_file_contents_ori = file.read()
            ModuleLocator = LocateModule(top_file_contents_ori, top_module)

            dcls_pattern = r'\b' + ip_err_port + r'\b'
            if bool(re.search(dcls_pattern, top_file_contents_ori)):
                is_safe = True

            if is_safe:
                top_file_dir = dcls_removal(top_name=top_module, dup_name=dup_name, output_path="/".join(top_file_dir.split('/')[:-1]), 
                                            ModuleLocator=ModuleLocator, DCLS_Removal=DCLS_Removal)
                with open(top_file_dir, 'r') as file:
                    top_file_contents_ori = file.read()
                os.remove(f"{top_file_dir}")
                ModuleLocator = LocateModule(top_file_contents_ori, top_module)

            top_flat_block = top_flat_wrapper(top_name=top_module, dup_name=dup_name, ip_err_port=ip_err_port, dup_err_port=dup_err_port, dup_err=dup_error, r2d=r2d, fierr=fault_list[0], dup_path=dup_path,
                                              ModuleLocator=ModuleLocator, StatsAnalyzer=StatsAnalyzer, DCLS_Generator=DCLS_Generator)

            file_name = top_file_dir.split('/')[-1][:-2] if top_file_dir.endswith('.v') else top_file_dir.split('/')[-1][:-3]
            file_name = file_name.replace("_REVERT", "")
            # top_dc_dir = os.path.join(generatorPath, args.output_path, f"{file_name}_NEW_FLAT.v")
            top_dc_dir = remove_after_pattern("/".join(top_file_dir.split('/')[:-1])) + f"SAFETY/{file_name}_NEW_FLAT.v"
            top_file = open(top_dc_dir, 'w')
            top_file.write(top_flat_block)
            print(bcolors.OKGREEN + f"Finished swapping original with duplicated module {top_dc_dir}" + bcolors.ENDC)
