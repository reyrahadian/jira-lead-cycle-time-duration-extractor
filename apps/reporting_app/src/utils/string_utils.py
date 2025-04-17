import pandas as pd
def split_string_array(value:str, separator:str)->list[str]:
    if is_in_array(value):
        list_str = value.strip('[]').replace("null","\"null\"")
        values = [s.replace('"', '').strip() for s in list_str.split(separator)]
        return values

    return [value]

def is_in_array(value:str)->bool:
    if pd.isna(value):
        return False

    if '[' in value:
        return True
    return False