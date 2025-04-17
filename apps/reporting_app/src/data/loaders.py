import pandas as pd
import os
from src.config.constants import (
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
from src.utils.stage_utils import (
    to_stage_start_date_column_name
)
class JiraData:
    tickets: pd.DataFrame
    projects: list[str]
    components: list[str]
    squads: list[str]
    ticket_types: list[str]

    def __init__(self):
        self.tickets = pd.DataFrame()
        self.projects = []
        self.components = []
        self.squads = []
        self.ticket_types = []
class CsvDataLoader:
    def load_data(self, csv_filepath: str) -> pd.DataFrame:
        print(f"Loading data from {csv_filepath}")
        print(f"Directory containing CSV file: {os.path.dirname(csv_filepath)}")
        print(f"Files in directory: {os.listdir(os.path.dirname(csv_filepath))}")
        jira_tickets = pd.read_csv(csv_filepath, delimiter=",")

        return jira_tickets
class JiraDataLoader:
    def __init__(self, csv_data_loader: CsvDataLoader):
        self.jira_data = JiraData()
        self.csv_data_loader = csv_data_loader

    def __process_jiratickets(self, jira_tickets):
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

    def __process_jiratickets_components(self, jira_tickets):
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

    def load_data(self, csv_filepath: str) -> JiraData:
        jira_tickets = self.csv_data_loader.load_data(csv_filepath)
        jira_tickets = self.__process_jiratickets(jira_tickets)
        jira_tickets = self.__process_jiratickets_components(jira_tickets)
        self.jira_data.tickets  = jira_tickets

        # Extract unique values
        self.jira_data.projects = sorted(jira_tickets[COLUMN_NAME_PROJECT].unique().tolist())
        self.jira_data.components = sorted(jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS].unique().tolist())
        self.jira_data.squads = sorted([squad for squad in jira_tickets[COLUMN_NAME_SQUAD].unique() if pd.notna(squad)]) if COLUMN_NAME_SQUAD in jira_tickets.columns else []
        self.jira_data.ticket_types = []

        return self.jira_data

class JiraDataLoaderWithCache:
    _instance = None
    _initialized = False

    def __new__(cls, jira_data_loader: JiraDataLoader = None):
        if cls._instance is None:
            cls._instance = super(JiraDataLoaderWithCache, cls).__new__(cls)
        return cls._instance

    def __init__(self, jira_data_loader: JiraDataLoader = None):
        if not self._initialized:
            if jira_data_loader is None:
                csv_data_loader = CsvDataLoader()
                jira_data_loader = JiraDataLoader(csv_data_loader)
            self.jira_data_loader = jira_data_loader
            self.cached_data = None
            self.last_modified_time = None
            self._initialized = True

    def get_csv_filepath(self):
        return os.getenv('REPORTING_CSV_PATH', "/mnt/c/workspace/jira-lead-cycle-time-duration-extractor/docker/data/jira_metrics.csv")

    def load_data(self) -> JiraData:
        # Check if file has been modified since last load
        current_modified_time = os.path.getmtime(self.get_csv_filepath())

        # Return cached data if file hasn't changed
        if (self.cached_data is not None and
            self.last_modified_time is not None and
            current_modified_time <= self.last_modified_time):
            return self.cached_data

        # Load fresh data if cache invalid
        self.cached_data = self.jira_data_loader.load_data(self.get_csv_filepath())
        self.last_modified_time = current_modified_time
        return self.cached_data