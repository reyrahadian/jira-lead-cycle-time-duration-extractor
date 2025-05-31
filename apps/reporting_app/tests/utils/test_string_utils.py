import pandas as pd
from src.utils.string_utils import split_string_array, is_in_array

def test_split_string_array():
    assert split_string_array("API,BFF,BFF-Web,SFCC", ",") == ['API,BFF,BFF-Web,SFCC']
    assert split_string_array("[API]", ",") == ["API"]
    assert split_string_array("[API,BFF,BFF-Web]", ",") == ["API","BFF","BFF-Web"]
    assert split_string_array("[API,BFF,BFF-Web,SFCC]", ",") == ["API","BFF","BFF-Web","SFCC"]
    assert split_string_array('["2025-01-21T23:31:33.421Z"-"2025-02-04T23:59:43.560Z"]', '"-"') == ["2025-01-21T23:31:33.421Z","2025-02-04T23:59:43.560Z"]
    assert split_string_array('["2024-10-01T09:00:00.000Z"-null]', '"-"') == ["2024-10-01T09:00:00.000Z","null"]
    assert split_string_array('[null-"2024-02-21T00:39:33.758Z"-"2023-11-15T03:11:17.715Z"]', '"-"') == ["null","2024-02-21T00:39:33.758Z","2023-11-15T03:11:17.715Z"]
    assert split_string_array('["D.A.W.N - Sprint 10.2.25"-"D.A.W.N - Sprint 11.2.25"]', '"-"') == ["D.A.W.N - Sprint 10.2.25","D.A.W.N - Sprint 11.2.25"]

def test_is_in_array():
    assert is_in_array("[API]") == True
    assert is_in_array("API") == False
    assert is_in_array("API,BFF,BFF-Web,SFCC") == False
    assert is_in_array("API,BFF,BFF-Web,SFCC") == False
    assert is_in_array("API,BFF,BFF-Web,SFCC") == False