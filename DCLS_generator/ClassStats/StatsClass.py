import re
import math
from dataclasses import dataclass
from DCLS_generator.common.find_bracket import find_balance_square_bracket


# For now, a class is not necessary since we're only tracking ff
# It is just in case more measurements needed in the future
@dataclass
class StatsClass:

    def __init__(self, param_list: list, parsed_port_list: list):
        self.param_dict = self._create_param_dict(param_list)
        self.parsed_port_list = parsed_port_list

    def _count_ff(self) -> int:
        total_ff = 0
        for port in self.parsed_port_list:
            packed_dimension_size = self._calculate_size(port[0])
            unpacked_dimension_size = self._calculate_size(port[2])
            total_ff += packed_dimension_size*unpacked_dimension_size
        return total_ff*2 + 2 + 1 + 2   # d1 + d2 + r_cnt + r_ERROR_DETECTION + ERR_*_DCLS

    def _calculate_size(self, dimension_2d: str) -> int:
        dimension_list = find_balance_square_bracket(dimension_2d)
        dimension_size = 1
        for dimension in dimension_list:
            dimension_size *= self._calculate_dimension(dimension)
        return dimension_size

    def _calculate_dimension(self, dimension: str) -> int:
        if dimension:
            bit_width = dimension.split(':')
            assert len(bit_width) == 2
            msb = self._convert_dimension(bit_width[0])
            lsb = bit_width[1]
            return eval(f"{msb} - {lsb} + 1")
        else:
            return 1

    # Swap parameters' names with values
    def _convert_dimension(self, msb: str) -> str:
        if self.param_dict:
            for param, value in self.param_dict.items():
                pattern = r'\b{}\b'.format(param)   # match exact word of param
                msb = re.sub(pattern, str(value), msb)
        return msb

    # Map parameter names with their values
    def _create_param_dict(self, param_list: list) -> dict:
        param_list_copy = param_list.copy()
        param_dict = {}
        unfinished = True
        cnt = 0
        while unfinished:
            unfinished = False
            for i, param_value in enumerate(param_list_copy):
                # print(value)
                param, value = param_value
                if "==" in str(value) or "?" in str(value):
                    value_exec = "if " + value.replace("\n", " ").replace(":", "\nelif ").replace("?", ":\n    param_tmp = ")
                    pos = value_exec.rfind("elif")
                    value_exec = value_exec[:pos] + "else:\n    param_tmp = " + value_exec[pos + len("elif"):]
                    value_exec = convert_to_decimal(value_exec)
                    for k, v in param_dict.items():
                        pattern = r'\b{}\b'.format(k)
                        value_exec = re.sub(pattern, str(v), value_exec)
                    value_exec = "global param_tmp;\n" + value_exec
                    exec(value_exec)
                    value = param_tmp
                    param_dict[param] = value
                    param_list_copy[i] = (param, value)
                elif "\"" in str(value) or "'" in str(value):
                    value = convert_to_decimal(value)
                    param_dict[param] = value
                    param_list_copy[i] = (param, value)
                else:
                    if str(value).isdigit():
                        value = int(value)
                        param_dict[param] = value
                        param_list_copy[i] = (param, value)
                    else:   # value is calculated using previous parameter assignment
                        value = value.replace('$clog2', 'math.log2')
                        value = convert_to_decimal(value)
                        for k, v in param_dict.items():
                            # if k == 'P_RF_DATA_WIDTH' and param == "P_RF_ADDR_SHIFT":
                            #     print("it's here")
                            #     print(k, v, value)
                            pattern = r'\b{}\b'.format(k)
                            value = re.sub(pattern, str(v), value)
                            # if param == "P_RF_ADDR_SHIFT":
                            #     print(value)
                        # Make sure everything is converted
                        try:
                            value = int(eval(value))
                            param_dict[param] = value
                            param_list_copy[i] = (param, value)
                        except:
                            cnt += 1
                            unfinished = True
                            if cnt == 26:
                                print(param, value)
                                print(param_dict)
                                raise ValueError("Infinite loop at converting parameter to real numbers")
        return param_dict


def convert_to_decimal(value: str):
    binary_pattern = r'\d+\'b([01]+)'
    value = re.sub(binary_pattern, lambda m: str(int(m.group(1), 2)), value)
    decimal_pattern = r'\d+\'d(\d+)'
    value = re.sub(decimal_pattern, r'\1', value)
    decimal_pattern = r'\'d(\d+)'
    value = re.sub(decimal_pattern, r'\1', value)
    return value
                    

