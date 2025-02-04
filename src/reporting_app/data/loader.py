import pandas as pd
from src.reporting_app.config.constants import VALID_COMPONENTS

def load_data():
    csv_filepath = "output-static.csv"
    return pd.read_csv(csv_filepath, delimiter=",")

def process_components(jira_tickets):
    # Create CalculatedComponents column starting with existing Components
    jira_tickets['CalculatedComponents'] = jira_tickets['Components']

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
    jira_tickets['TitleComponents'] = jira_tickets['Name'].apply(extract_components_from_title)

    # Merge existing components with title components
    jira_tickets['CalculatedComponents'] = jira_tickets.apply(
        lambda row: ','.join(sorted(
            set(filter(None, str(row['Components']).split(','))) | row['TitleComponents']
        )) if pd.notna(row['Components']) or row['TitleComponents']
        else '',
        axis=1
    )

    # Drop the temporary TitleComponents column
    jira_tickets = jira_tickets.drop('TitleComponents', axis=1)
    return jira_tickets

JIRA_TICKETS = load_data()
JIRA_TICKETS = process_components(JIRA_TICKETS)

# Extract unique values
UNIQUE_PROJECTS = sorted(JIRA_TICKETS['Project'].unique().tolist())
UNIQUE_COMPONENTS = sorted(JIRA_TICKETS['CalculatedComponents'].unique().tolist())
UNIQUE_SQUADS = sorted([squad for squad in JIRA_TICKETS['Squad'].unique() if pd.notna(squad)]) if 'Squad' in JIRA_TICKETS.columns else []
UNIQUE_TICKET_TYPES = []  # Will be populated by callback