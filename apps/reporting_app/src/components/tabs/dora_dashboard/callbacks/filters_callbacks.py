from dash import Input, Output, callback
from src.data.data_dora import JiraDataDoraMetrics, JiraDataDoraMetricsFilter
from src.data.data_filters import JiraDataFilterService, JiraDataFilter
import pandas as pd
from datetime import datetime, timedelta
from pytz import UTC

def init_callbacks(app, jira_tickets: pd.DataFrame):
    @callback(
        Output('dora-tab-squads-dropdown', 'options'),
        Input('dora-tab-project-dropdown', 'value')
    )
    def update_squads_dropdown(projects):
        if not projects:
            return []

        jira_data_filter_service = JiraDataFilterService()
        jira_data_filter = JiraDataFilter(projects=projects)
        jira_data_filter_result = jira_data_filter_service.filter_tickets(jira_tickets, jira_data_filter)
        squads = jira_data_filter_result.squads

        return [
            {'label': squad, 'value': squad} for squad in squads
        ]

    @callback(
        Output('dora-tab-date-range-container', 'style'),
        Input('dora-tab-time-range-dropdown', 'value')
    )
    def update_date_range_visibility(time_range):
        if time_range == 'custom_date_range':
            return {'display': 'block'}
        return {'display': 'none'}
