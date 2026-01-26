def find_matching_port(*lists):
    if len(lists) > 4:
        raise ValueError("This function supports at most 4 lists.")

    # Extract middle elements (port name) from each list
    middle_sets = [set(item[1] for item in lst) for lst in lists]
    
    duplicates = set()
    seen = set()

    for s in middle_sets:
        overlap = seen & s
        if overlap:
            duplicates.update(overlap)
        seen.update(s)

    return duplicates

