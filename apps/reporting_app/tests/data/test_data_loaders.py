import pandas as pd
from src.data.data_loaders import JiraDataLoader
from src.data.data_loaders import CsvDataLoader
from tests.test_helpers import TestHelpers

def test_jiradataloader_load_data(mocker):
    mock_csv_loader = mocker.Mock(spec=CsvDataLoader)
    mock_csv_loader.load_data.return_value = TestHelpers.get_jira_data()
    jira_data_loader = JiraDataLoader(mock_csv_loader)
    jira_data = jira_data_loader.load_data("jira_metrics.csv")

    assert jira_data is not None
    assert jira_data.get_projects() == [
        'BFF Chapter',
        'Commerce.Cloud',
        'Digital App Services',
        'Digital MECCA App',
        'Dory Squad',
        'Sitecore',
        'SuperHost App',
        'Tieramisu'
        ]

