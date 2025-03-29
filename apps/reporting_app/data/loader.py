import pandas as pd
import os
from config.constants import (
    VALID_COMPONENTS,
    ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS,
    COLUMN_NAME_CREATED_DATE,
    COLUMN_NAME_UPDATED_DATE,
    COLUMN_NAME_COMPONENTS,
    COLUMN_NAME_CALCULATED_COMPONENTS,
    COLUMN_NAME_NAME,
    COLUMN_NAME_PROJECT,
    COLUMN_NAME_SQUAD
)
from utils.stage_utils import (
    to_stage_start_date_column_name
)

def load_data():
    csv_filepath = os.getenv('REPORTING_CSV_PATH', "/mnt/c/workspace/jira-lead-cycle-time-duration-extractor/docker/data/jira_metrics.csv")
    print(f"Loading data from {csv_filepath}")
    print(f"Directory containing CSV file: {os.path.dirname(csv_filepath)}")
    print(f"Files in directory: {os.listdir(os.path.dirname(csv_filepath))}")
    jira_tickets = pd.read_csv(csv_filepath, delimiter=",")
    jira_tickets[COLUMN_NAME_CREATED_DATE] = pd.to_datetime(jira_tickets[COLUMN_NAME_CREATED_DATE], utc=True)
    jira_tickets[COLUMN_NAME_UPDATED_DATE] = pd.to_datetime(jira_tickets[COLUMN_NAME_UPDATED_DATE], utc=True)

    for days_col in ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS:
        # Handle start date columns
        start_col = to_stage_start_date_column_name(days_col)
        if start_col in jira_tickets.columns:
            jira_tickets[start_col] = pd.to_datetime(jira_tickets[start_col], utc=True, errors='coerce')
        else:
            jira_tickets[start_col] = pd.NaT

        # Handle duration columns
        if days_col not in jira_tickets.columns:
            jira_tickets[days_col] = pd.NA

    return jira_tickets

def process_components(jira_tickets):
    # Create CalculatedComponents column starting with existing Components
    jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS] = jira_tickets[COLUMN_NAME_COMPONENTS]

    # Function to extract components from title prefix
    def extract_components_from_title(title):
        if pd.isna(title):
            return set()

        # Split the title by the first occurrence of '-' or '|'
        parts = title.split(' - ', 1)
        if len(parts) == 1:
            parts = title.split('|', 1)

        if len(parts) == 1:
            return set()

        # Process the prefix part
        prefix = parts[0]
        # Split by '|' and clean up each component
        raw_components = {comp.strip().upper() for comp in prefix.split('|') if comp.strip()}

        # Only keep valid components and map them to their standardized names
        valid_components = {VALID_COMPONENTS[comp] for comp in raw_components
                          if comp in VALID_COMPONENTS}
        return valid_components

    # Update CalculatedComponents based on title prefix
    jira_tickets['TitleComponents'] = jira_tickets[COLUMN_NAME_NAME].apply(extract_components_from_title)

    # Merge existing components with title components
    jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS] = jira_tickets.apply(
        lambda row: ','.join(sorted(
            set(filter(None, str(row[COLUMN_NAME_COMPONENTS]).split(','))) | row['TitleComponents']
        )) if pd.notna(row[COLUMN_NAME_COMPONENTS]) or row['TitleComponents']
        else '',
        axis=1
    )

    # Drop the temporary TitleComponents column
    jira_tickets = jira_tickets.drop('TitleComponents', axis=1)

    # Add SFCC components based on COM- ticket prefix
    def extract_sfcc_component(ticket_id):
        if pd.isna(ticket_id):
            return ''
        if str(ticket_id).startswith('COM-'):
            return 'SFCC'
        return ''

    # Add SFCC components to CalculatedComponents
    jira_tickets['SFCCComponent'] = jira_tickets['ID'].apply(extract_sfcc_component)
    jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS] = jira_tickets.apply(
        lambda row: ','.join(filter(None, [row[COLUMN_NAME_CALCULATED_COMPONENTS], row['SFCCComponent']])),
        axis=1
    )

    # Drop temporary column
    jira_tickets = jira_tickets.drop('SFCCComponent', axis=1)
    return jira_tickets

JIRA_TICKETS = load_data()
JIRA_TICKETS = process_components(JIRA_TICKETS)

# Extract unique values
UNIQUE_PROJECTS = sorted(JIRA_TICKETS[COLUMN_NAME_PROJECT].unique().tolist())
UNIQUE_COMPONENTS = sorted(JIRA_TICKETS[COLUMN_NAME_CALCULATED_COMPONENTS].unique().tolist())
UNIQUE_SQUADS = sorted([squad for squad in JIRA_TICKETS[COLUMN_NAME_SQUAD].unique() if pd.notna(squad)]) if COLUMN_NAME_SQUAD in JIRA_TICKETS.columns else []
UNIQUE_TICKET_TYPES = []  # Will be populated by callback