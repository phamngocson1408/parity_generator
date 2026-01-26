python3.9 -m DCLS_generator.parity_generator -info ./DCLS_generator/\[INFO]_PARITY_TEMPLATE.xlsx

<<comment
    Generator execution guide:
        Move to N1 WS; Source N1 environment
        Run the above python (either 3.8 or 3.9) commands at directory: ./DCLS_generator/ (1st DCLS_generator)

    Generator output directory: ./DCLS_generator/module_parity/
        SIGNAL  : 
            SIGNAL_PARITY_DRV_*.v   : Driver modules with their parity instances
            SIGNAL_PARITY_RCV_*.v   : Receiver modules with their parity instances
            SIGNAL_DRIVER_PARITY.v  : Parity modules for drivers
            SIGNAL_RECEIVER_PARITY.v: Parity modules for receivers
        BUS     : 
            BUS_PARITY_*.v          : Top module with an instance of the Parity module
            IP_PARITY.v             : Parity module for bus
        REGISTER:
            REGISTER_PARITY_*_TOP.v : Top module with an instance of the Parity module
            REGISTER_PARITY.v       : Parity module for registers

    INFO file guide:
        Required fields: 
            "DRIVER/RECEIVER/IP/BUS NAME": Name of the targeted module
            "* PORT/REGISTER NAME"      : Name of the targeted signal
            "* PARITY * NAME"           : Parity name for the corresponding signals
            "* CLOCK"                   : Clock name of the corresponding module
            "* RESET"                   : Reset name of the corresponding module
            "BIT WIDTH"                 : Widths of the signals that is used to calculate parity
            "PARITY SOURCE BIT WIDTH"   : Widths of the parity after calculating (slicing)
            "* FILE LIST"               : Path to the corresponding module's filelists 
            "* ERROR PORT"              : Error port name of the corresponding module            

        Optional fields: If a field isn't used, it should be left empty
            "* ERROR DOUBLE"    (YES)   : Whether the error port is double (YES) or single (NO)
            "FAULT INJECTION"           : Flip certain output bits to assert error {list of bits to be flipped}@{control signal}

        Not-used fields: "VERSION", "BLOCK NAME", "* INSTANCE PATH" (for other usage)

    Sample Formality test directory: /workspace/user/thomh1511/N1_A0/formality/script_formality/parity/

    Notes:
        Fields that are not used should be left empty
        There should not be more than 1 target module in 1 verilog file
        In BUS, "IP ERROR PORT" is also used to determine the directions of parity signals
comment
