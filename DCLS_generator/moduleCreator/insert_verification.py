def insert_error_connection(instance_name: str, top_name: str) -> str:
    error_connection_block = ""
    error_connection_block += (
        f"assign {top_name}   = {instance_name};\n"
        f"assign {top_name}_B = {instance_name}_B;\n"
    )

    return error_connection_block

