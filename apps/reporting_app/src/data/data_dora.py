import pandas as pd
from datetime import datetime
from src.config.constants import (
    STAGE_NAME_BACKLOG,
    STAGE_NAME_DELIVERY_BACKLOG,
    STAGE_NAME_REJECTED,
    STAGE_NAME_ON_HOLD,
    STAGE_NAME_OPEN,
    STAGE_NAME_FAILED_TEST,
    STAGE_NAME_IDEAS_INTAKE,
    STAGE_NAME_DISCOVERY,
    STAGE_NAME_READY_FOR_DEVELOPMENT,
    STAGE_NAME_DONE,
    STAGE_NAME_CLOSED,
    STAGE_NAME_BUG_FIXED,
    ALL_STAGE_NAMES,
    COLUMN_NAME_PROJECT,
    COLUMN_NAME_CREATED_DATE,
    COLUMN_NAME_FIX_VERSIONS,
    COLUMN_NAME_PRIORITY,
    COLUMN_NAME_SPRINT,
    COLUMN_NAME_STAGE,
    STAGE_NAME_DEPLOYED_TO_PROD,
    STAGE_NAME_IN_PRODUCTION,
    COLUMN_NAME_SQUAD
)
from src.utils.stage_utils import StageUtils
from src.utils.string_utils import split_string_array
from src.utils.sprint_utils import get_sprint_date_range
class JiraDataDoraMetricsResult:
    _category: str
    _value: str

    @property
    def category(self) -> str:
        return self._category

    @property
    def value(self) -> float:
        return self._value

    def __init__(self, category: str, value: str):
        self._category = category
        self._value = value

    def format_days_duration(self, duration: float) -> str:
        weeks = duration // 5
        days = duration % 5
        if weeks == 0:
            return f"{days:.0f}d"
        return f"{weeks:.0f}w {days:.0f}d"

    def format_percentage(self, percentage: float) -> str:
        return f"{percentage:.2f}%"

class JiraDataDoraMetricsFilter:
    _projects: list[str]
    _squads: list[str]
    _start_date: datetime
    _end_date: datetime

    @property
    def projects(self) -> list[str]:
        return self._projects

    @property
    def squads(self) -> list[str]:
        return self._squads

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @property
    def end_date(self) -> datetime:
        return self._end_date

    def __init__(self, projects: list[str], squads: list[str], start_date: datetime, end_date: datetime):
        self._projects = projects
        self._squads = squads
        self._start_date = start_date
        self._end_date = end_date

class JiraDataDoraMetrics:
    _tickets: pd.DataFrame

    def __init__(self, tickets: pd.DataFrame):
        self._tickets = tickets

    def __get_avg_duration_timespent_in_progress(self, tickets: pd.DataFrame) -> float:
        if(tickets.empty):
            return 0

        invalid_stage_names = [
            STAGE_NAME_BACKLOG,
            STAGE_NAME_DELIVERY_BACKLOG,
            STAGE_NAME_REJECTED,
            STAGE_NAME_ON_HOLD,
            STAGE_NAME_OPEN,
            STAGE_NAME_FAILED_TEST,
            STAGE_NAME_IDEAS_INTAKE,
            STAGE_NAME_DISCOVERY,
            STAGE_NAME_READY_FOR_DEVELOPMENT,
            #STAGE_NAME_READY_FOR_RELEASE,
            #STAGE_NAME_PRE_PRODUCTION,
            #STAGE_NAME_AWAITING_PROD_DEPLOYMENT,
            #STAGE_NAME_PROD_PRE_CHECK_DEPLOYMENT,
            #STAGE_NAME_IN_PRODUCTION,
            #STAGE_NAME_DEPLOYED_TO_PROD,
            #STAGE_NAME_IN_PROD_TEST,
            STAGE_NAME_DONE,
            STAGE_NAME_CLOSED,
            STAGE_NAME_BUG_FIXED
        ]
        valid_stage_names = [stage for stage in ALL_STAGE_NAMES if stage not in invalid_stage_names]
        valid_stage_names = [StageUtils.to_stage_duration_days_column_name(stage) for stage in valid_stage_names]

        # Filter tickets that have at least one valid stage with duration > 0
        valid_tickets = tickets[tickets[valid_stage_names].gt(0).any(axis=1)]

        # Sum the values of all valid stage duration columns for valid tickets
        total_duration = valid_tickets[valid_stage_names].sum().sum()
        average_duration = total_duration / len(valid_tickets)

        return average_duration

    def __get_filtered_tickets(self, filter: JiraDataDoraMetricsFilter) -> pd.DataFrame:
        if filter.projects:
            self._tickets = self._tickets[self._tickets[COLUMN_NAME_PROJECT].isin(filter.projects)]

        if filter.squads:
            self._tickets = self._tickets[self._tickets[COLUMN_NAME_SQUAD].isin(filter.squads)]

        if filter.start_date:
            self._tickets = self._tickets[self._tickets[COLUMN_NAME_CREATED_DATE] >= filter.start_date]

        if filter.end_date:
            self._tickets = self._tickets[self._tickets[COLUMN_NAME_CREATED_DATE] <= filter.end_date]

        return self._tickets

    def get_lead_time_for_changes(self, filter: JiraDataDoraMetricsFilter) -> JiraDataDoraMetricsResult:
        filtered_tickets = self.__get_filtered_tickets(filter)
        average_duration = self.__get_avg_duration_timespent_in_progress(filtered_tickets)

        return JiraDataDoraMetricsResult(category='Lead Time for Changes', value=average_duration)

    def get_deployment_frequency(self, filter: JiraDataDoraMetricsFilter) -> JiraDataDoraMetricsResult:
        filtered_tickets = self.__get_filtered_tickets(filter)
        tickets_assigned_to_sprints = filtered_tickets[filtered_tickets[COLUMN_NAME_SPRINT].notna()]
        # we assume that all tickets that has fix version and is set to done has been deployed to prod
        done_stage_names = [
            STAGE_NAME_DONE,
            STAGE_NAME_CLOSED,
            STAGE_NAME_BUG_FIXED,
            STAGE_NAME_DEPLOYED_TO_PROD,
            STAGE_NAME_IN_PRODUCTION
        ]
        tickets_deployed_to_prod = tickets_assigned_to_sprints[
            (tickets_assigned_to_sprints[COLUMN_NAME_FIX_VERSIONS].notna()) &
            (tickets_assigned_to_sprints[COLUMN_NAME_STAGE].isin(done_stage_names))
        ]
        total_tickets_deployed_to_prod = len(tickets_deployed_to_prod)

        start_date = None
        end_date = None
        if filter.start_date is None or filter.end_date is None:
            # Get unique sprints
            sprint_set = set()
            for sprint_str in tickets_assigned_to_sprints[COLUMN_NAME_SPRINT].dropna().unique():
                sprints = split_string_array(sprint_str, '"-"')
                sprint_set.update(sprint.strip() for sprint in sprints)

            # Get the oldest sprint start date and most recent end date from the sprint set
            for sprint in sprint_set:
                # Get one ticket from this sprint to get its dates
                sprint_ticket = tickets_assigned_to_sprints[tickets_assigned_to_sprints[COLUMN_NAME_SPRINT].str.contains(sprint, na=False)].iloc[0]
                # Convert the Series to a DataFrame with a single row
                sprint_ticket_df = sprint_ticket.to_frame().T
                sprint_start_date, sprint_end_date = get_sprint_date_range(sprint_ticket_df, sprint)

                if sprint_start_date and not pd.isna(sprint_start_date):
                    # Initialize start_date if not set, otherwise take the earlier date
                    if start_date is None or sprint_start_date < start_date:
                        start_date = sprint_start_date

                if sprint_end_date and not pd.isna(sprint_end_date):
                    # Initialize end_date if not set, otherwise take the later date
                    if end_date is None or sprint_end_date > end_date:
                        end_date = sprint_end_date
        else:
            start_date = filter.start_date
            end_date = filter.end_date

        total_working_days = len(pd.date_range(start=start_date, end=end_date, freq='B'))
        deployment_frequency = total_tickets_deployed_to_prod / total_working_days if total_working_days > 0 else 0

        return JiraDataDoraMetricsResult(category='Deployment Frequency', value=deployment_frequency)

    def get_change_failure_rate(self, filter: JiraDataDoraMetricsFilter) -> JiraDataDoraMetricsResult:
        filtered_tickets = self.__get_filtered_tickets(filter)
        # we assume that all tickets that has fix version has been deployed to prod
        ticket_deployed_to_prod = filtered_tickets[filtered_tickets[COLUMN_NAME_FIX_VERSIONS].notna()]
        # we assume tickets that are set with priority P1 or P2 are incident tickets
        incident_tickets = filtered_tickets[
            (filtered_tickets[COLUMN_NAME_FIX_VERSIONS].notna()) &
            (filtered_tickets[COLUMN_NAME_PRIORITY].isin(['P1', 'P2']))
        ]
        change_failure_rate = (len(incident_tickets) / len(ticket_deployed_to_prod)) * 100 if len(ticket_deployed_to_prod) > 0 else 0

        return JiraDataDoraMetricsResult(category='Change Failure Rate', value=change_failure_rate)

    def get_mean_time_to_recovery(self, filter: JiraDataDoraMetricsFilter) -> JiraDataDoraMetricsResult:
        filtered_tickets = self.__get_filtered_tickets(filter)
        # we assume tickets that are set with priority P1 or P2 are incident tickets
        incident_tickets = filtered_tickets[
            (filtered_tickets[COLUMN_NAME_FIX_VERSIONS].notna()) &
            (filtered_tickets[COLUMN_NAME_PRIORITY].isin(['P1', 'P2']))
        ]

        # get average time spent to recover from an incident
        average_duration = self.__get_avg_duration_timespent_in_progress(incident_tickets)

        return JiraDataDoraMetricsResult(category='Mean Time to Recovery', value=average_duration)