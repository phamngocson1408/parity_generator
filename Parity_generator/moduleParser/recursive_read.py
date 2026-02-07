import re
import os
import subprocess
from Parity_generator.moduleParser.depart_module.depart_module import module_partition, instance_partition


def recursive_find_v(file_paths):
    file_path_list = file_paths.split(",")
    file_list = []
    for file_path in file_path_list:
        environmentVariables = getEnvironmentVariables()
        file_path = re.sub(r'\$\{(\w+)\}', lambda m: environmentVariables.get(m.group(1), m.group(0)), file_path)    # .f format with brackets
        file_path = re.sub(r'\$(.*?)(?=\/)', lambda m: environmentVariables.get(m.group(1), m.group(0)), file_path)  # positive lookahead for missing brackets
        if not (file_path.startswith('#') or file_path.startswith('//')):
            with open(file_path) as file:
                file_dir = '/'.join(file_path.split('/')[:-1])
                for line in file:
                    line = line.strip()
                    if line.startswith('+incdir') or line.startswith('+libext'):
                        pass
                    else:
                        if line.endswith('.f'):
                            # Find .v files in another filelist
                            file_abs_path = find_abs_path(file_dir, line)
                            file_list += recursive_find_v(file_abs_path)
                        elif line.endswith('.v') or line.endswith('.sv'):
                            # Get the absolute path of all the files pointed to by this filelist
                            # Make sure that we are not reading a file twice
                            file_abs_path = find_abs_path(file_dir, line)
                            file_list.append(file_abs_path)
                        else:
                            # print(f'Unexpected line pattern: {line}')
                            # print(f'Skip reading {line} due to its name :)')
                            pass
    return file_list


def recursive_read_v(file_set, module_name: str, multi_level=False):
    file_dir = None
    module_location = []
    for file_path in file_set:
        if file_path.strip().startswith("-v"):
            file_path = file_path.replace("-v", "", 1).strip()
        environmentVariables = getEnvironmentVariables()
        file_path = re.sub(r'\$\{(\w+)\}', lambda m: environmentVariables.get(m.group(1), m.group(0)), file_path)    # .f format with brackets
        file_path = re.sub(r'\$(.*?)(?=\/)', lambda m: environmentVariables.get(m.group(1), m.group(0)), file_path)  # positive lookahead for missing brackets

        with open(file_path, 'r') as file:
            file_contents = file.read()
        if multi_level is False:
            if module_partition(file_contents, module_name) is not None:
                file_dir = file_path
                module_location.append(module_partition(file_contents, module_name))
        else:
            if instance_partition(file_contents, module_name) is not None:
                file_dir = file_path
                module_location.append(instance_partition(file_contents, module_name))

    assert len(module_location) == 1, f"Expected exactly one matched module/instance {module_name} but found {len(module_location)}."
    
    return module_location, file_dir


def find_abs_path(file_dir, line):
    line = line.replace('-f', '', 1).replace('-F', '', 1).strip()
    if '$' in line:
        return line     # Already absolute path
    else:
        return os.path.abspath(os.path.join(file_dir, line))


# Get env variables
def getEnvironmentVariables():
    result = subprocess.run(['printenv'], capture_output=True, text=True)
    envVars = {}
    for line in result.stdout.splitlines():
        match = re.match(r'.*?=.*?', line, re.DOTALL)
        if match:
            name, value = line.split('=', 1)
            envVars[name] = value
    return envVars


def path_env(file_set: set):
    resultFiles = set()
    environmentVariables = getEnvironmentVariables()

    for line in file_set:
        # skip commented lines
        if line.startswith('#') or line.startswith('//'):
            continue

        line = re.sub(r'\$\{(\w+)\}', lambda m: environmentVariables.get(m.group(1), m.group(0)), line)
        resultFiles.add(line)

    return resultFiles


