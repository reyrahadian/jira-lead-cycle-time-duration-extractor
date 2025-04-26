import pandas as pd
from src.data.data_dora import JiraDataDoraMetrics, JiraDataDoraMetricsFilter
from src.data.data_loaders import JiraDataLoader, CsvDataLoader
from tests.test_helpers import TestHelpers
from datetime import datetime, timezone

def test_jiradatadorametrics_getleadtimeforchanges(mocker):
    mock_csv_data_loader = mocker.Mock(spec=CsvDataLoader)
    mock_csv_data_loader.load_data.return_value = TestHelpers.get_jira_data()
    jira_data_loader = JiraDataLoader(mock_csv_data_loader)
    jira_data = jira_data_loader.load_data("jira_metrics.csv")
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data.get_tickets())
    result = jira_data_dora_metrics.get_lead_time_for_changes(JiraDataDoraMetricsFilter(projects=None, start_date=None, end_date=None))
    assert result.category == 'Lead Time for Changes'
    assert result.value == 34.83617021276596

    result = jira_data_dora_metrics.get_lead_time_for_changes(JiraDataDoraMetricsFilter(projects=['Digital MECCA App'], start_date=None, end_date=None))
    assert result.value == 25.304140127388536

def test_jiradorametrics_deploymentfrequency(mocker):
    mock_csv_data_loader = mocker.Mock(spec=CsvDataLoader)
    mock_csv_data_loader.load_data.return_value = TestHelpers.get_jira_data()
    jira_data_loader = JiraDataLoader(mock_csv_data_loader)
    jira_data = jira_data_loader.load_data("jira_metrics.csv")
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data.get_tickets())

    result = jira_data_dora_metrics.get_deployment_frequency(JiraDataDoraMetricsFilter(projects=None, start_date=None, end_date=None))
    assert result.category == 'Deployment Frequency'
    assert result.value == 0.6235186873290793

    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 3, 31, tzinfo=timezone.utc)
    result = jira_data_dora_metrics.get_deployment_frequency(JiraDataDoraMetricsFilter(projects=None, start_date=start_date, end_date=end_date))
    assert result.category == 'Deployment Frequency'
    assert result.value == 4.625

    result = jira_data_dora_metrics.get_deployment_frequency(JiraDataDoraMetricsFilter(projects=['Digital MECCA App'], start_date=start_date, end_date=end_date))
    assert result.value == 1.65625


def test_jiradorametrics_changefailurerate(mocker):
    mock_csv_data_loader = mocker.Mock(spec=CsvDataLoader)
    mock_csv_data_loader.load_data.return_value = TestHelpers.get_jira_data()
    jira_data_loader = JiraDataLoader(mock_csv_data_loader)
    jira_data = jira_data_loader.load_data("jira_metrics.csv")
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data.get_tickets())
    result = jira_data_dora_metrics.get_change_failure_rate(JiraDataDoraMetricsFilter(projects=None, start_date=None, end_date=None))
    assert result.category == 'Change Failure Rate'
    assert result.value == 0.0

    result = jira_data_dora_metrics.get_change_failure_rate(JiraDataDoraMetricsFilter(projects=['Digital MECCA App'], start_date=None, end_date=None))
    assert result.value == 0.0

def test_jiradorametrics_meantimetorecovery(mocker):
    mock_csv_data_loader = mocker.Mock(spec=CsvDataLoader)
    mock_csv_data_loader.load_data.return_value = TestHelpers.get_jira_data()
    jira_data_loader = JiraDataLoader(mock_csv_data_loader)
    jira_data = jira_data_loader.load_data("jira_metrics.csv")
    jira_data_dora_metrics = JiraDataDoraMetrics(jira_data.get_tickets())
    result = jira_data_dora_metrics.get_mean_time_to_recovery(JiraDataDoraMetricsFilter(projects=None, start_date=None, end_date=None))
    assert result.category == 'Mean Time to Recovery'
    assert result.value == 0

    result = jira_data_dora_metrics.get_mean_time_to_recovery(JiraDataDoraMetricsFilter(projects=['Digital MECCA App'], start_date=None, end_date=None))
    assert result.value == 0.0