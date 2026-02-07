from Parity_generator.moduleParser.depart_module.depart_module import *

from Parity_generator.extract_data_classes import ExtractParam
from Parity_generator.extract_data_classes import ExtractInport
from Parity_generator.extract_data_classes import ExtractOutport

from Parity_generator.ClassLocateIP.LocateModule import LocateModule
from Parity_generator.ClassLocateIP.LocateInstance import LocateInstance


def coarse_grained_process_dc(dc_file_path: str, dc_module: str):
    with open(dc_file_path, 'r') as file:
        file_contents = file.read()

    module_declaration_content, module_whole_content = module_partition(file_contents, dc_module)
    assert module_declaration_content is not None
    assert module_whole_content is not None

    param_usage = True if '#' in module_declaration_content else False

    param_declaration, port_declaration = module_declaration_partition(module_declaration_content, param_usage=param_usage)

    return module_declaration_content, module_whole_content, param_declaration, port_declaration


def fine_grained_process_dc(dc_file_path: str, dc_module: str, clk: str, rst: str):
    # coarsed-grained process
    module_declaration_content, module_whole_content, param_declaration, port_declaration = coarse_grained_process_dc(dc_file_path, dc_module)
    # Input
    InPutExtractor = ExtractInport(port_declaration, module_whole_content)
    parsed_inport, parsed_clk_rst = InPutExtractor._extract_clk_rst(clk, rst)
    # Output
    OutPutExtractor = ExtractOutport(port_declaration, module_whole_content)
    parsed_outport = OutPutExtractor._extract_dimension()
    # Param
    ParamExtractor = ExtractParam(param_declaration, module_whole_content)
    parsed_param = ParamExtractor._extract_value()

    return parsed_param, parsed_clk_rst, parsed_inport, parsed_outport


def coarse_grained_process_top(top_file_path: str, top_module: str):
    with open(top_file_path, 'r') as file:
        top_file_contents_ori = file.read()

    ModuleLocator = LocateModule(top_file_contents_ori, top_module)
    before_top_file_contents, top_file_contents, after_top_file_contents = ModuleLocator._separate_ip()

    return before_top_file_contents, top_file_contents, after_top_file_contents


def fine_grained_process_top(top_file_path: str, top_module: str, dc_module: str):
    before_top_file_contents, top_file_contents, after_top_file_contents = coarse_grained_process_top(top_file_path, top_module)

    InstanceLocator = LocateInstance(top_file_contents, dc_module)
    before_instance_content, instance_content, after_instance_content = InstanceLocator._separate_ip()

    return before_instance_content, instance_content, after_instance_content


# Sample usage
if __name__ == "__main__":

