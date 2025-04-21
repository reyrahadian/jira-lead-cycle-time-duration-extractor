import pandas as pd
from src.data.data_dora import JiraDataDoraMetrics
from tests.test_helpers import TestHelpers

def test_jiradatadorametrics_getleadtimeforchanges():
    jira_data = TestHelpers.get_jira_data()
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data)
    result = jira_data_dora_metrics.get_lead_time_for_changes()
    assert result.category == 'Lead Time for Changes'
    assert result.value == 34.83617021276596

def test_jiradorametrics_changefailurerate():
    jira_data = TestHelpers.get_jira_data()
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data)
    result = jira_data_dora_metrics.get_change_failure_rate()
    assert result.category == 'Change Failure Rate'
    assert result.value == 0.0

def test_jiradorametrics_meantimetorecovery():
    jira_data = TestHelpers.get_jira_data()
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data)
    result = jira_data_dora_metrics.get_mean_time_to_recovery()
    assert result.category == 'Mean Time to Recovery'
    assert result.value == 0