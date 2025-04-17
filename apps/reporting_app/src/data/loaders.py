import pandas as pd
import os
from src.config.constants import (
    ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS,
    COLUMN_NAME_CREATED_DATE,
    COLUMN_NAME_UPDATED_DATE,
    COLUMN_NAME_COMPONENTS,
    COLUMN_NAME_CALCULATED_COMPONENTS,
    COLUMN_NAME_NAME,
    COLUMN_NAME_PROJECT,
    COLUMN_NAME_SQUAD,
    COLUMN_NAME_ID
)
from src.utils.stage_utils import to_stage_start_date_column_name
from src.utils.jira_utils import JiraTicketHelpers
from src.utils.string_utils import split_string_array
class JiraData:
    tickets: pd.DataFrame
    projects: set[str]
    components: set[str]
    squads: set[str]
    ticket_types: set[str]

    def __init__(self):
        self.tickets = pd.DataFrame()
        self.projects = set()
        self.components = set()
        self.squads = set()
        self.ticket_types = set()
class CsvDataLoader:
    def load_data(self, csv_filepath: str) -> pd.DataFrame:
        print(f"Loading data from {csv_filepath}")
        print(f"Directory containing CSV file: {os.path.dirname(csv_filepath)}")
        print(f"Files in directory: {os.listdir(os.path.dirname(csv_filepath))}")
        jira_tickets = pd.read_csv(csv_filepath, delimiter=",")

        return jira_tickets

class JiraDataLoader:
    # Valid Components
    VALID_COMPONENTS = {
        'FEWeb': 'FEWeb',
        'FEApp': 'FEApp',
        'BFFWeb': 'BFFWeb',
        'BFFApp': 'BFFApp',
        'BFF': 'BFF',
        'FED': 'FED',
        'SFCC': 'SFCC',
        'XM': 'XM',
        'SITECORE': 'Sitecore',
        'CONTENTHUB': 'Content Hub'
    }

    def __init__(self, csv_data_loader: CsvDataLoader):
        self.jira_data = JiraData()
        self.csv_data_loader = csv_data_loader

    def __process_jiratickets_dates(self, jira_tickets: pd.DataFrame)->pd.DataFrame:
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

    # Function to extract components from title prefix
    def __extract_components_from_title(self, title: str)-> set[str]:
        components = JiraTicketHelpers.get_components_from_summary(title)

        # Only keep valid components and map them to their standardized names
        valid_components = {self.VALID_COMPONENTS[comp] for comp in components
                        if comp in self.VALID_COMPONENTS}

        return valid_components

    # Add SFCC components based on COM- ticket prefix
    def __extract_sfcc_component(self, ticket_id: str)-> set[str]:
        if pd.isna(ticket_id):
            return set()
        if str(ticket_id).startswith('COM-'):
            return {'SFCC'}
        return set()

    def __process_jiratickets_components(self, jira_tickets: pd.DataFrame)->pd.DataFrame:
        components = jira_tickets[COLUMN_NAME_COMPONENTS].apply(lambda x: set(split_string_array(x, ',')))
        components_from_title = jira_tickets[COLUMN_NAME_NAME].apply(self.__extract_components_from_title)
        components_sfcc = jira_tickets[COLUMN_NAME_ID].apply(self.__extract_sfcc_component)

        # Combine components from title into existing components set for each row
        components = components.combine(components_from_title, lambda x, y: x.union(y))
        components = components.combine(components_sfcc, lambda x, y: x.union(y))
        jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS] = components

        return jira_tickets

    def load_data(self, csv_filepath: str) -> JiraData:
        jira_tickets = self.csv_data_loader.load_data(csv_filepath)
        jira_tickets = self.__process_jiratickets_dates(jira_tickets)
        jira_tickets = self.__process_jiratickets_components(jira_tickets)
        self.jira_data.tickets  = jira_tickets

        self.jira_data.projects = sorted(jira_tickets[COLUMN_NAME_PROJECT].unique())
        # Flatten the series of sets and get unique values
        unique_components = set().union(*jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS].dropna())
        self.jira_data.components = sorted(unique_components)
        self.jira_data.squads = sorted([squad for squad in jira_tickets[COLUMN_NAME_SQUAD].unique() if pd.notna(squad)]) if COLUMN_NAME_SQUAD in jira_tickets.columns else set()
        self.jira_data.ticket_types = set()

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