def split_string_array(string_array):
    if string_array.startswith('['):
        list_str = string_array.strip('[]')
        sprints = [s.replace('"', '').strip() for s in list_str.split("\"-\"")]
        return sprints

    return [string_array]