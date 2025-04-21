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
    COLUMN_NAME_PRIORITY
)
from src.utils.stage_utils import StageUtils

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
    _start_date: datetime
    _end_date: datetime

    @property
    def projects(self) -> list[str]:
        return self._projects

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @property
    def end_date(self) -> datetime:
        return self._end_date

    def __init__(self, projects: list[str], start_date: datetime, end_date: datetime):
        self._projects = projects
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
        #TODO: we need to capture exact day when a prod deployment was done as part of the JIRA metrics

        return JiraDataDoraMetricsResult(category='Deployment Frequency', value=0)

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