import pandas as pd
import os
from src.config.constants import (
    ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS,
    COLUMN_NAME_CREATED_DATE,
    COLUMN_NAME_UPDATED_DATE,
    COLUMN_NAME_COMPONENTS,
    COLUMN_NAME_CALCULATED_COMPONENTS,
    COLUMN_NAME_SPRINT,
    COLUMN_NAME_CALCULATED_SPRINT,
    COLUMN_NAME_NAME,
    COLUMN_NAME_PROJECT,
    COLUMN_NAME_ID
)
from src.utils.stage_utils import StageUtils
from src.utils.jira_utils import JiraTicketHelpers
from src.utils.string_utils import split_string_array
from src.config.app_settings import AppSettings
class JiraData:
    __tickets: pd.DataFrame

    def __init__(self, tickets: pd.DataFrame):
        self.__tickets = tickets

    def get_tickets(self) -> pd.DataFrame:
        return self.__tickets

    def get_projects(self) -> list[str]:
        return sorted(self.__tickets[COLUMN_NAME_PROJECT].unique())

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
        self.csv_data_loader = csv_data_loader

    def __process_jiratickets_dates(self, jira_tickets: pd.DataFrame)->pd.DataFrame:
        jira_tickets[COLUMN_NAME_CREATED_DATE] = pd.to_datetime(jira_tickets[COLUMN_NAME_CREATED_DATE], utc=True)
        jira_tickets[COLUMN_NAME_UPDATED_DATE] = pd.to_datetime(jira_tickets[COLUMN_NAME_UPDATED_DATE], utc=True)

        for days_col in ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS:
            # Handle start date columns
            start_col = StageUtils.to_stage_start_date_column_name(days_col)
            if start_col in jira_tickets.columns:
                jira_tickets[start_col] = pd.to_datetime(jira_tickets[start_col], utc=True, errors='coerce')
            else:
                jira_tickets[start_col] = pd.NaT

            # Handle duration columns
            if days_col not in jira_tickets.columns:
                jira_tickets[days_col] = pd.NA

        return jira_tickets

    # Function to extract components from title prefix
    def __extract_components_from_title(self, title: str)-> list[str]:
        components = JiraTicketHelpers.get_components_from_summary(title)

        # Only keep valid components and map them to their standardized names
        valid_components = [self.VALID_COMPONENTS[comp] for comp in components
                        if comp in self.VALID_COMPONENTS]

        return valid_components

    # Add SFCC components based on COM- ticket prefix
    def __extract_sfcc_component(self, ticket_id: str)-> list[str]:
        if pd.isna(ticket_id):
            return []
        if str(ticket_id).startswith('COM-'):
            return ['SFCC']
        return []

    def __process_jiratickets_components(self, jira_tickets: pd.DataFrame)->pd.DataFrame:
        # Convert components to lists instead of sets
        components = jira_tickets[COLUMN_NAME_COMPONENTS].apply(lambda x: list(split_string_array(x, '-')))
        components_from_title = jira_tickets[COLUMN_NAME_NAME].apply(lambda x: list(self.__extract_components_from_title(x)))
        components_sfcc = jira_tickets[COLUMN_NAME_ID].apply(lambda x: list(self.__extract_sfcc_component(x)))

        # Combine components from title into existing components list for each row
        components = components.combine(components_from_title, lambda x, y: list(set(x + y)))
        components = components.combine(components_sfcc, lambda x, y: list(set(x + y)))
        jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS] = components

        return jira_tickets

    def __process_jiratickets_sprint(self, jira_tickets: pd.DataFrame)->pd.DataFrame:
        jira_tickets[COLUMN_NAME_CALCULATED_SPRINT] = jira_tickets[COLUMN_NAME_SPRINT].apply(lambda x: list(split_string_array(x, '-')))

        return jira_tickets

    def load_data(self, csv_filepath: str) -> JiraData:
        jira_tickets = self.csv_data_loader.load_data(csv_filepath)
        jira_tickets = self.__process_jiratickets_dates(jira_tickets)
        jira_tickets = self.__process_jiratickets_components(jira_tickets)
        jira_tickets = self.__process_jiratickets_sprint(jira_tickets)
        jira_data = JiraData(jira_tickets)

        return jira_data

class JiraDataSingleton:
    _instance = None
    _initialized = False

    def __init__(self, jira_data_loader: JiraDataLoader = None):
        if not self._initialized:
            if jira_data_loader is None:
                csv_data_loader = CsvDataLoader()
                jira_data_loader = JiraDataLoader(csv_data_loader)
            self.jira_data_loader = jira_data_loader
            self.cached_data = None
            self.last_modified_time = None
            self._initialized = True

    def __new__(cls, jira_data_loader: JiraDataLoader = None):
        if cls._instance is None:
            cls._instance = super(JiraDataSingleton, cls).__new__(cls)
        return cls._instance

    def get_csv_filepath(self):
        app_settings = AppSettings()
        return app_settings.REPORTING_CSV_PATH

    def get_jira_data(self) -> JiraData:
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