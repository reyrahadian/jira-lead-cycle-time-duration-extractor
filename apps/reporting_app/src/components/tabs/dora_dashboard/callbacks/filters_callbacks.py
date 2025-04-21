from dash import Input, Output, callback
from src.data.data_dora import JiraDataDoraMetrics
import pandas as pd

def init_callbacks(app, jira_tickets: pd.DataFrame):
    @callback(
        Output('lead-time-to-change-badge', 'children'),
        Output('lead-time-to-change-badge', 'color'),
        Output('lead-time-to-change-value', 'children'),
        Input('dora-tab-project-dropdown', 'value')
    )
    def update_lead_time_to_change_tile(projects):
        jira_data_dora_metrics = JiraDataDoraMetrics(jira_tickets)
        lead_time_to_change = jira_data_dora_metrics.get_lead_time_for_changes()

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
        Input('dora-tab-project-dropdown', 'value')
    )
    def update_deployment_frequency_tile(projects):
        jira_data_dora_metrics = JiraDataDoraMetrics(jira_tickets)
        deployment_frequency = jira_data_dora_metrics.get_deployment_frequency()

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
        Input('dora-tab-project-dropdown', 'value')
    )
    def update_change_failure_rate_tile(projects):
        jira_data_dora_metrics = JiraDataDoraMetrics(jira_tickets)
        change_failure_rate = jira_data_dora_metrics.get_change_failure_rate()

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
        Input('dora-tab-project-dropdown', 'value')
    )
    def update_time_to_restore_service_tile(projects):
        jira_data_dora_metrics = JiraDataDoraMetrics(jira_tickets)
        time_to_restore_service = jira_data_dora_metrics.get_mean_time_to_recovery()

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


