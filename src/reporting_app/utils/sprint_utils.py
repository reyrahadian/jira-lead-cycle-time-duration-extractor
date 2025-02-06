import pandas as pd

def get_sprint_date_range(df, sprint_name):
    def is_multiple_values(value):
        if isinstance(value, str) and '[' in value:
            return True
        return False
    def get_sprint_value_index(value, list):
        # example value: ["LFW 1.1.25"-"LFW 2.1.25"]
        if is_multiple_values(list):
            list_str = list.strip('[]').replace('"', '')
            list = [s.strip() for s in list_str.split('-')]
            return list.index(value)
        return 0
    def get_date_from_multiple_values(index, list):
        # example value: ["2025-01-21T23:31:33.421Z"-"2025-02-04T23:59:43.560Z"]
        if is_multiple_values(list):
            list_str = list.strip('[]')
            list = [s.replace('"', '').strip() for s in list_str.split("\"-\"")]
            return list[index]
        return list

    start_date = None
    end_date = None
    # Get sprint dates
    if not df.empty and 'SprintStartDate' in df.columns and 'SprintEndDate' in df.columns:
        first_ticket = df.iloc[0]
        sprints = first_ticket['Sprint']

        if is_multiple_values(sprints):
            sprint_index = get_sprint_value_index(sprint_name, sprints)
            start_date = get_date_from_multiple_values(sprint_index, first_ticket['SprintStartDate'])
            end_date = get_date_from_multiple_values(sprint_index, first_ticket['SprintEndDate'])
        else:
            start_date = first_ticket['SprintStartDate']
            end_date = first_ticket['SprintEndDate']

        if pd.notna(start_date) and pd.notna(end_date):
            # Convert to datetime if they're strings
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)

    return start_date, end_date