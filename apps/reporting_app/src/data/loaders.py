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
    COLUMN_NAME_ID,
    COLUMN_NAME_SPRINT,
    COLUMN_NAME_TYPE
)
from src.utils.stage_utils import to_stage_start_date_column_name
from src.utils.jira_utils import JiraTicketHelpers
from src.utils.string_utils import split_string_array
from src.utils.sprint_utils import get_sprint_date_range

class JiraData:
    tickets: pd.DataFrame
    projects: list[str]
    squads: list[str]
    sprints: list[str]
    ticket_types: list[str]
    components: list[str]

    def __init__(self):
        self.tickets = pd.DataFrame()
        self.projects = []
        self.sprints = []
        self.components = []
        self.squads = []
        self.ticket_types = []

    def get_squads_by_filters(self, project: str) -> list[str]:
        tickets = self.tickets[self.tickets[COLUMN_NAME_PROJECT] == project]
        if COLUMN_NAME_SQUAD in tickets.columns:
            # Filter out NaN values and convert to list before sorting
            squads = [squad for squad in tickets[COLUMN_NAME_SQUAD].unique() if pd.notna(squad)]
            return sorted(squads)
        else:
            return []

    def get_sprints_by_filters(self, project: str, squad: str) -> list[str]:
        tickets = self.tickets[self.tickets[COLUMN_NAME_PROJECT] == project]
        if squad and COLUMN_NAME_SQUAD in tickets.columns:
            tickets = tickets[tickets[COLUMN_NAME_SQUAD] == squad]

        # Get unique sprints
        sprint_set = set()
        for sprint_str in tickets[COLUMN_NAME_SPRINT].dropna().unique():
            sprints = split_string_array(sprint_str, '"-"')
            sprint_set.update(sprint.strip() for sprint in sprints)

        # Get sprint end dates and sort sprints by end date descending
        sprint_dates = {}
        for sprint in sprint_set:
            # Get one ticket from this sprint to get its dates
            sprint_ticket = tickets[tickets[COLUMN_NAME_SPRINT].str.contains(sprint, na=False)].iloc[0]
            # Convert the Series to a DataFrame with a single row
            sprint_ticket_df = sprint_ticket.to_frame().T
            start_date, _ = get_sprint_date_range(sprint_ticket_df, sprint)
            if start_date and not pd.isna(start_date):
                # Ensure timezone-naive comparison by converting to UTC and removing timezone
                sprint_dates[sprint] = start_date.tz_localize(None) if start_date.tz else start_date
            else:
                # Use timezone-naive minimum timestamp
                sprint_dates[sprint] = pd.Timestamp.min.tz_localize(None)

        # Sort sprints by start date descending
        return sorted(sprint_dates.keys(), key=lambda x: sprint_dates[x], reverse=True)

    def filter_tickets(self, filter_dict: dict[str, str]) -> pd.DataFrame:
        return self.tickets.query(filter_dict)

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
        components = jira_tickets[COLUMN_NAME_COMPONENTS].apply(lambda x: list(split_string_array(x, ',')))
        components_from_title = jira_tickets[COLUMN_NAME_NAME].apply(lambda x: list(self.__extract_components_from_title(x)))
        components_sfcc = jira_tickets[COLUMN_NAME_ID].apply(lambda x: list(self.__extract_sfcc_component(x)))

        # Combine components from title into existing components list for each row
        components = components.combine(components_from_title, lambda x, y: list(set(x + y)))
        components = components.combine(components_sfcc, lambda x, y: list(set(x + y)))
        jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS] = components

        return jira_tickets

    def load_data(self, csv_filepath: str) -> JiraData:
        jira_tickets = self.csv_data_loader.load_data(csv_filepath)
        jira_tickets = self.__process_jiratickets_dates(jira_tickets)
        jira_tickets = self.__process_jiratickets_components(jira_tickets)
        self.jira_data.tickets  = jira_tickets

        self.jira_data.projects = sorted(jira_tickets[COLUMN_NAME_PROJECT].unique())
        # Get all unique components
        unique_components = set().union(*jira_tickets[COLUMN_NAME_CALCULATED_COMPONENTS].dropna())
        # Filter out any non-string values and sort
        self.jira_data.components = sorted(str(comp) for comp in unique_components if isinstance(comp, str))
        self.jira_data.squads = sorted([squad for squad in jira_tickets[COLUMN_NAME_SQUAD].unique() if pd.notna(squad)]) if COLUMN_NAME_SQUAD in jira_tickets.columns else []
        self.jira_data.ticket_types = sorted(jira_tickets[COLUMN_NAME_TYPE].unique()) if COLUMN_NAME_TYPE in jira_tickets.columns else []

        return self.jira_data

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
        return os.getenv('REPORTING_CSV_PATH', "/mnt/c/workspace/jira-lead-cycle-time-duration-extractor/docker/data/jira_metrics.csv")

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