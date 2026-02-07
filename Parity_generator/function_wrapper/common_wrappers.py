from Parity_generator.extract_data_classes import ExtractPort
from Parity_generator.moduleCreator.declare_port import declare_parity_port_2001, declare_parity_port_1995
from Parity_generator.moduleParser.depart_module.depart_module import module_partition, module_declaration_partition


def add_port(declaration_content: str, module_content: str, top_name: str, extra_inport: list, extra_outport: list):
    top_param_declaration, top_port_declaration = module_declaration_partition(declaration_content,
                                                                               param_usage=False)

    PortExtractor = ExtractPort(top_port_declaration, module_content)
    port_declaration_1995, ANSI_C_port = PortExtractor._extract_declaration_valid()
    module_declaration_content = f"module {top_name} "
    if top_param_declaration:
        module_declaration_content += "#(\n" + top_param_declaration + "\n)"
    module_declaration_content += "(\n" + declare_parity_port_2001(port_declaration_2001=top_port_declaration,
                                                                   ANSI_C=ANSI_C_port,
                                                                   extra_inport=extra_inport,
                                                                   extra_outport=extra_outport) + "\n);\n"
    module_declaration_content += "\n" + declare_parity_port_1995(port_declaration_1995=port_declaration_1995,
                                                                  ANSI_C=ANSI_C_port,
                                                                  extra_inport=extra_inport,
                                                                  extra_outport=extra_outport) + "\n"
    return module_declaration_content

