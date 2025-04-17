def split_string_array(string_array):
    # example values
    # ["2025-01-21T23:31:33.421Z"-"2025-02-04T23:59:43.560Z"]
    # ["2024-10-01T09:00:00.000Z"-null]
    # [null-"2024-02-21T00:39:33.758Z"-"2023-11-15T03:11:17.715Z"]
    if string_array.startswith('['):
        list_str = string_array.strip('[]').replace("null","\"null\"")
        sprints = [s.replace('"', '').strip() for s in list_str.split("\"-\"")]
        return sprints

    return [string_array]

def is_multiple_values(value):
        if '[' in value:
            return True
        return False