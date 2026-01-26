def gated_register_cnt(file_dir: str):
    reg_cnt = 0
    reg_list = []

    with open(file_dir, 'r') as file:
        for line in file:
            line = line.strip()
            if '|' in line:
                splitted_line = line.split('|')
                if len(splitted_line) == 2:
                    reg = splitted_line[1]
                    if reg.strip() and ' ' not in reg.strip():
                        reg_cnt = reg_cnt + 1
                        reg_list.append(reg.strip())
    print("Total number of gated register: ", reg_cnt)
    return reg_cnt, reg_list


def ungated_register_cnt(file_dir: str):
    reg_cnt = 0
    reg_list = []

    with open(file_dir, 'r') as file:
        for line in file:
            line = line.strip()
            if '|' in line:
                splitted_line = line.split('|')
                if len(splitted_line) == 3:
                    reg = splitted_line[0]
                    if reg.strip() and ' ' not in reg.strip():
                        reg_cnt = reg_cnt + 1
                        reg_list.append(reg.strip())
    print("Total number of ungated register: ", reg_cnt)
    return reg_cnt, reg_list


