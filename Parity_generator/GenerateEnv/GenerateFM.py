import os
import sys
import subprocess


class GenerateFM:

    def __init__(self, ip_name: str, filelist: list, top_path: list):
        self.ip_name = ip_name
        self.filelist = " ".join(filelist.split(","))
        self.top_path = " ".join(top_path)

        self._copy_fm_workspace()
        self._replace_placeholder()
#        self._run_fm()


    def _copy_fm_workspace(self):
        subprocess.run(["rm", "-rf", "DCLS_FM"])
        subprocess.run(["cp", "-r", "Parity_generator/FM_template", "DCLS_FM"])
        return None

    def _replace_placeholder(self):
        # Read
        with open("DCLS_FM/formal_cmd_script.tcl", "r") as file:
            filedata = file.read()
        # Replace
        filedata = filedata.replace("TOP_NAME_PLACEHOLDER", self.ip_name)
        filedata = filedata.replace("TOP_NAME_NEW_PLACEHOLDER", f"{self.ip_name}_NEW")

        filelist_r = "read_sverilog -r -libname work -vcs " + f"\"-f {self.filelist}\"" + " -define SYNTHESIS"
        filelist_i = "read_sverilog -i -libname work -vcs " + f"\"{self.top_path} -f {self.filelist}\"" + " -define SYNTHESIS" 

        filedata = filedata.replace("READ_SVERILOG_R_TEMPLATE", filelist_r)
        filedata = filedata.replace("READ_SVERILOG_I_TEMPLATE", filelist_i)
        # Re-Write
        with open("DCLS_FM/formal_cmd_script.tcl", "w") as file:
            file.write(filedata)
        return None

    def _run_fm(self):
#        subprocess
        return None


