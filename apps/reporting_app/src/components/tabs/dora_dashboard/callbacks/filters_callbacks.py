from dash import Input, Output, callback
from src.data.data_dora import JiraDataDoraMetrics, JiraDataDoraMetricsFilter
import pandas as pd
from datetime import datetime, timedelta
from pytz import UTC

def init_callbacks(app, jira_tickets: pd.DataFrame):
    def _get_dates_from_time_range(time_range: str) -> tuple[datetime, datetime]:
        start_date = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now(UTC).replace(hour=23, minute=59, second=59, microsecond=999999)

        if time_range == 'last_6_months':
            return (start_date - timedelta(days=180), end_date)
        elif time_range == 'last_3_months':
            return (start_date - timedelta(days=90), end_date)
        elif time_range == 'last_2_weeks':
            return (start_date - timedelta(days=14), end_date)
        elif time_range == 'last_week':
            return (start_date - timedelta(days=7), end_date)
        elif time_range == 'today':
            return (start_date, end_date)
        else:
            return None, None

    def _get_dates(time_range: str, start_date: str, end_date: str)->tuple[datetime, datetime]:
        start_date_result: datetime
        end_date_result: datetime

        if time_range != 'custom_date_range':
            start_date_result, end_date_result = _get_dates_from_time_range(time_range)
        else:
            start_date_result = pd.Timestamp(start_date).tz_localize('UTC')
            end_date_result = pd.Timestamp(end_date).tz_localize('UTC')

        return start_date_result, end_date_result

    @callback(
        Output('lead-time-to-change-badge', 'children'),
        Output('lead-time-to-change-badge', 'color'),
        Output('lead-time-to-change-value', 'children'),
        Input('dora-tab-project-dropdown', 'value'),
        Input('dora-tab-time-range-dropdown', 'value'),
        Input('dora-tab-date-range', 'start_date'),
        Input('dora-tab-date-range', 'end_date')
    )
    def update_lead_time_to_change_tile(projects, time_range, start_date, end_date):
        start_date, end_date = _get_dates(time_range, start_date, end_date)

        jira_data_dora_metrics = JiraDataDoraMetrics(jira_tickets)
        lead_time_to_change = jira_data_dora_metrics.get_lead_time_for_changes(JiraDataDoraMetricsFilter(projects=projects, start_date=start_date, end_date=end_date))

        if lead_time_to_change.value < 1:
            badge_text = 'Elite'
            badge_color = 'primary'
        elif lead_time_to_change.value >= 1 and lead_time_to_change.value <= 5:
            badge_text = 'High'
            badge_color = 'success'
        elif lead_time_to_change.value >= 5 and lead_time_to_change.value <= 20:
            badge_text = 'Medium'
            badge_color = 'warning'
        else:
            badge_text = 'Low'
            badge_color = 'danger'

        return badge_text, badge_color, lead_time_to_change.format_days_duration(lead_time_to_change.value)

    @callback(
        Output('deployment-frequency-badge', 'children'),
        Output('deployment-frequency-badge', 'color'),
        Output('deployment-frequency-value', 'children'),
        Input('dora-tab-project-dropdown', 'value'),
        Input('dora-tab-time-range-dropdown', 'value'),
        Input('dora-tab-date-range', 'start_date'),
        Input('dora-tab-date-range', 'end_date')
    )
    def update_deployment_frequency_tile(projects, time_range, start_date, end_date):
        start_date, end_date = _get_dates(time_range, start_date, end_date)

        jira_data_dora_metrics = JiraDataDoraMetrics(jira_tickets)
        deployment_frequency = jira_data_dora_metrics.get_deployment_frequency(JiraDataDoraMetricsFilter(projects=projects, start_date=start_date, end_date=end_date))

        if deployment_frequency.value > 1:
            badge_text = 'Elite'
            badge_color = 'primary'
        elif deployment_frequency.value >= 1 and deployment_frequency.value <= 5:
            badge_text = 'High'
            badge_color = 'success'
        elif deployment_frequency.value >=5 and deployment_frequency.value <= 20:
            badge_text = 'Medium'
            badge_color = 'warning'
        else:
            badge_text = 'Low'
            badge_color = 'danger'

        return badge_text, badge_color, deployment_frequency.format_days_duration(deployment_frequency.value)

    @callback(
        Output('change-failure-rate-badge', 'children'),
        Output('change-failure-rate-badge', 'color'),
        Output('change-failure-rate-value', 'children'),
        Input('dora-tab-project-dropdown', 'value'),
        Input('dora-tab-time-range-dropdown', 'value'),
        Input('dora-tab-date-range', 'start_date'),
        Input('dora-tab-date-range', 'end_date')
    )
    def update_change_failure_rate_tile(projects, time_range, start_date, end_date):
        start_date, end_date = _get_dates(time_range, start_date, end_date)

        jira_data_dora_metrics = JiraDataDoraMetrics(jira_tickets)
        change_failure_rate = jira_data_dora_metrics.get_change_failure_rate(JiraDataDoraMetricsFilter(projects=projects, start_date=start_date, end_date=end_date))

        if change_failure_rate.value <= 5:
            badge_text = 'Elite'
            badge_color = 'primary'
        elif change_failure_rate.value >= 5 and change_failure_rate.value <= 10:
            badge_text = 'High'
            badge_color = 'success'
        elif change_failure_rate.value >= 10 and change_failure_rate.value <= 15:
            badge_text = 'Medium'
            badge_color = 'warning'
        else:
            badge_text = 'Low'
            badge_color = 'danger'

        return badge_text, badge_color, change_failure_rate.format_percentage(change_failure_rate.value)

    @callback(
        Output('time-to-restore-service-badge', 'children'),
        Output('time-to-restore-service-badge', 'color'),
        Output('time-to-restore-service-value', 'children'),
        Input('dora-tab-project-dropdown', 'value'),
        Input('dora-tab-time-range-dropdown', 'value'),
        Input('dora-tab-date-range', 'start_date'),
        Input('dora-tab-date-range', 'end_date')
    )
    def update_time_to_restore_service_tile(projects, time_range, start_date, end_date):
        start_date, end_date = _get_dates(time_range, start_date, end_date)

        jira_data_dora_metrics = JiraDataDoraMetrics(jira_tickets)
        time_to_restore_service = jira_data_dora_metrics.get_mean_time_to_recovery(JiraDataDoraMetricsFilter(projects=projects, start_date=start_date, end_date=end_date))

        if time_to_restore_service.value <= 0.1:
            badge_text = 'Elite'
            badge_color = 'primary'
        elif time_to_restore_service.value >= 0.1 and time_to_restore_service.value <= 1:
            badge_text = 'High'
            badge_color = 'success'
        elif time_to_restore_service.value >= 1 and time_to_restore_service.value <= 2:
            badge_text = 'Medium'
            badge_color = 'warning'
        else:
            badge_text = 'Low'
            badge_color = 'danger'

        return badge_text, badge_color, time_to_restore_service.format_days_duration(time_to_restore_service.value)

    @callback(
        Output('dora-tab-date-range-container', 'style'),
        Input('dora-tab-time-range-dropdown', 'value')
    )
    def update_date_range_visibility(time_range):
        if time_range == 'custom_date_range':
            return {'display': 'block'}
        return {'display': 'none'}



