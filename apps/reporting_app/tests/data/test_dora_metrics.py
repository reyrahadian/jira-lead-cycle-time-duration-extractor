import pandas as pd
from src.data.data_dora import JiraDataDoraMetrics, JiraDataDoraMetricsFilter
from tests.test_helpers import TestHelpers

def test_jiradatadorametrics_getleadtimeforchanges():
    jira_data = TestHelpers.get_jira_data()
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data)
    result = jira_data_dora_metrics.get_lead_time_for_changes(JiraDataDoraMetricsFilter(projects=None, start_date=None, end_date=None))
    assert result.category == 'Lead Time for Changes'
    assert result.value == 34.83617021276596

    result = jira_data_dora_metrics.get_lead_time_for_changes(JiraDataDoraMetricsFilter(projects=['Digital MECCA App'], start_date=None, end_date=None))
    assert result.value == 25.304140127388536

def test_jiradorametrics_deploymentfrequency():
    jira_data = TestHelpers.get_jira_data()
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data)
    result = jira_data_dora_metrics.get_deployment_frequency(JiraDataDoraMetricsFilter(projects=None, start_date=None, end_date=None))
    assert result.category == 'Deployment Frequency'
    assert result.value == 0.0

    result = jira_data_dora_metrics.get_deployment_frequency(JiraDataDoraMetricsFilter(projects=['Digital MECCA App'], start_date=None, end_date=None))
    assert result.value == 0.0


def test_jiradorametrics_changefailurerate():
    jira_data = TestHelpers.get_jira_data()
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data)
    result = jira_data_dora_metrics.get_change_failure_rate(JiraDataDoraMetricsFilter(projects=None, start_date=None, end_date=None))
    assert result.category == 'Change Failure Rate'
    assert result.value == 0.0

    result = jira_data_dora_metrics.get_change_failure_rate(JiraDataDoraMetricsFilter(projects=['Digital MECCA App'], start_date=None, end_date=None))
    assert result.value == 0.0

def test_jiradorametrics_meantimetorecovery():
    jira_data = TestHelpers.get_jira_data()
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data)
    result = jira_data_dora_metrics.get_mean_time_to_recovery(JiraDataDoraMetricsFilter(projects=None, start_date=None, end_date=None))
    assert result.category == 'Mean Time to Recovery'
    assert result.value == 0

    result = jira_data_dora_metrics.get_mean_time_to_recovery(JiraDataDoraMetricsFilter(projects=['Digital MECCA App'], start_date=None, end_date=None))
    assert result.value == 0.0