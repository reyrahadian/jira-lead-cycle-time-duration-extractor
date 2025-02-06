import pandas as pd
from src.reporting_app.config.constants import (
    THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS,
    ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS
)
from src.reporting_app.utils.sprint_utils import get_sprint_date_range

def calculate_tickets_duration_in_sprint(df, sprint_name):
    """
    Calculate stage metrics for tickets within a sprint's date range.

    Args:
        df (pd.DataFrame): DataFrame containing ticket data
        sprint_start_date (datetime): Start date of the sprint
        sprint_end_date (datetime): End date of the sprint

    Returns:
        pd.DataFrame: DataFrame with stage metrics for the sprint period
    """

    sprint_start_date, sprint_end_date = get_sprint_date_range(df, sprint_name)

    if sprint_start_date is None or sprint_end_date is None:
        return df  # Return original dataframe if no sprint dates

    # Filter tickets that were active before the sprint ended
    sprint_tickets = df[
        (df['CreatedDate'] <= sprint_end_date)
    ].copy()

    # Calculate stage end dates based on start dates and durations
    for stage in ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS:
        start_col = to_stage_start_date_column_name(stage)
        end_col = to_stage_end_date_column_name(stage)
        days_col = to_stage_duration_days_column_name(stage)

        # Calculate end date by adding days to start date, handling null values
        mask = sprint_tickets[start_col].notna()  # Only calculate for non-null start dates

        # Convert days to numeric and create timedelta
        days_numeric = pd.to_numeric(sprint_tickets.loc[mask, days_col], errors='coerce')
        delta = pd.to_timedelta(days_numeric, unit='D')

        # Add the timedelta to start dates
        sprint_tickets.loc[mask, end_col] = sprint_tickets.loc[mask, start_col] + delta

    # Filter tickets that were active during the sprint
    active_mask = pd.Series(True, index=sprint_tickets.index)
    for col in ['Stage Done end', 'Stage Closed end', 'Stage Rejected end']:
        if col in sprint_tickets.columns:
            active_mask &= (sprint_tickets[col].isna() | (sprint_tickets[col] >= sprint_start_date))

    sprint_tickets = sprint_tickets[active_mask]

    # Calculate days spent in each stage during the sprint period
    for stage in THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS:
        start_col = to_stage_start_date_column_name(stage)
        end_col = to_stage_end_date_column_name(stage)
        sprint_days_col = to_stage_in_sprint_duration_days_column_name(stage)

        # Calculate overlapping days between stage period and sprint period, excluding weekends
        sprint_tickets[sprint_days_col] = sprint_tickets.apply(
            lambda row: len([
                d for d in pd.date_range(
                    max(sprint_start_date, row[start_col]),
                    min(sprint_end_date, row[end_col]),
                    freq='D'
                ) if d.weekday() < 5  # 0-4 are Monday-Friday
            ]) if pd.notna(row[start_col]) and pd.notna(row[end_col]) else 0,
            axis=1
        )

    return sprint_tickets

def to_stage_name(stage_series):
    """Convert stage column names to clean stage names."""
    if isinstance(stage_series, pd.Series):
        return stage_series.str.replace('Stage ', '').str.replace(' days in sprint', '').str.replace(' days', '')
    if isinstance(stage_series, pd.Index):
        return stage_series.str.replace('Stage ', '').str.replace(' days in sprint', '').str.replace(' days', '')
    return stage_series.replace('Stage ', '').replace(' days in sprint', '').replace(' days', '')

def to_stage_start_date_column_name(stage_series):
    """Convert stage column names to clean stage names in stage start date."""
    return f"Stage {to_stage_name(stage_series)} start"

def to_stage_end_date_column_name(stage_series):
    """Convert stage column names to clean stage names in stage end date."""
    return f"Stage {to_stage_name(stage_series)} end"

def to_stage_duration_days_column_name(stage_series):
    """Convert stage column names to clean stage names in sprint duration days."""
    return f"Stage {to_stage_name(stage_series)} days"

def to_stage_in_sprint_duration_days_column_name(stage_series):
    """Convert stage column names to clean stage names in sprint duration days."""
    return f"Stage {to_stage_name(stage_series)} days in sprint"