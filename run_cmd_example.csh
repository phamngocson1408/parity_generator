python3.9 -m DCLS_generator.dcls_generator -info ./DCLS_generator/\[INFO]_DCLS_TEMPLATE_AXIDMA.xlsx

python3.9 -m DCLS_generator.dcls_generator -info ./DCLS_generator/\[INFO]_DCLS_TEMPLATE_SRAMTOP.xlsx

python3.9 -m DCLS_generator.dcls_generator -info ./DCLS_generator/\[INFO]_DCLS_TEMPLATE_DMA.xlsx

python3.9 -m DCLS_generator.dcls_generator -info ./DCLS_generator/\[INFO]_DCLS_TEMPLATE_SIREX.xlsx

<<comment
    Generator execution guide:
        Move to N1 WS; Source N1 environment
        Run the above python (either 3.8 or 3.9) commands at directory: ./DCLS_generator/ (1st DCLS_generator)

    Generator output directory: ./DCLS_generator/module_dcls/
        DC  : *_DCLS_NEW_GATE.v
        WRAP: *_NEW.v
        FLAT: *_NEW_FLAT.v

    INFO file guide:
        Required fields: 
            "IP NAME"                   : Name of the top module that calls the duplicated module
            "DUPLICATION NAME"          : Name of the module that is the targeted of duplication 
            "DUPLICATION INSTANCE PATH" : Hierarchy path of the duplicated module instance
            "CLOCK"                     : Clock name of the "DUPLICATION NAME" module
            "RESET"                     : Reset name of the "DUPLICATION NAME" module
            "IP ERROR PORT"             : Error port name of the DCLS scheme
            "DESIGN FILE LIST"          : Path to the IP's filelists 

        Optional fields: If a field isn't used, it should be left empty
            "DUPLICATION TYPE"   (WRAP) : Whether the duplicated module is at another (WRAP) or the same (FLAT) hierarchy with top module
            "IP ERROR DOUBLE"    (YES)  : Whether the error port is double (YES) or single (NO)
            "RESET_2D"           (NO)   : If the duplication module uses another 2-cycle delayed reset signal or not
            "IGNORE INPUT"              : List of inputs that will not be delayed 2 cycles
            "IGNORE OUTPUT"             : List of outputs that will not be delayed 2 cycles
            "INPUT OUTPUT VALID"        : Clock gating list {list of signals to be gated}@{valid signal}
            "FAULT INJECTION"           : Flip certain output bits to assert error {list of bits to be flipped}@{control signal}

        Not-used fields: "VERSION", "BLOCK NAME", "IP INSTANCE PATH", "DUPLICATION MODULE FILE" (for other usage)

    Sample Formality test directory: /workspace/user/thomh1511/N1_A0/formality/script_formality/

    Notes:
        Fields that are not used should be left empty
comment
