import pandas as pd

def get_sprint_date_range(df):
    # Get sprint dates
    if not df.empty and 'SprintStartDate' in df.columns and 'SprintEndDate' in df.columns:
        first_ticket = df.iloc[0]
        start_date = first_ticket['SprintStartDate']
        end_date = first_ticket['SprintEndDate']

        if pd.notna(start_date) and pd.notna(end_date):
            # Convert to datetime if they're strings
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)

                return start_date, end_date

    return None, None