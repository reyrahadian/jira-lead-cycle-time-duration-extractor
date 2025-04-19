import pandas as pd
from src.data.data_loaders import JiraDataLoader
from src.config.constants import COLUMN_NAME_ID, COLUMN_NAME_NAME, COLUMN_NAME_PROJECT, COLUMN_NAME_COMPONENTS, \
    COLUMN_NAME_SQUAD, COLUMN_NAME_CREATED_DATE, COLUMN_NAME_UPDATED_DATE, COLUMN_NAME_STAGE_IN_DEVELOPMENT_DAYS, \
    COLUMN_NAME_SPRINT, COLUMN_NAME_TYPE

def __get_jira_data():
    return pd.DataFrame({
        COLUMN_NAME_ID: ['COM-123', 'COM-124', 'DAS-125'],
        COLUMN_NAME_NAME: ['[BFF|BFFWeb] - Update product catalog','[SFCC] - Update product catalog', '[FEApp] - Add new feature'],
        COLUMN_NAME_PROJECT: ['Commerce', 'Commerce', 'Commerce'],
        COLUMN_NAME_COMPONENTS: ['["BFF","BFFWeb"]', '["SFCC"]', '["FEApp"]'],
        COLUMN_NAME_SQUAD: ['Team1', None, 'Team2'],
        COLUMN_NAME_CREATED_DATE: ['2024-01-01', '2024-01-02', '2024-01-03'],
        COLUMN_NAME_UPDATED_DATE: ['2024-01-15', '2024-01-16', '2024-01-17'],
        COLUMN_NAME_STAGE_IN_DEVELOPMENT_DAYS: [10, 5, 7],
        COLUMN_NAME_SPRINT: ['LFW 1.2.25', 'LFW 1.1.25', 'LFW 1.2.25'],
        COLUMN_NAME_TYPE: ['Story', 'Task', 'Spike']
    })

def test_jiradataloader_load_data(mocker):
    csv_data_loader = mocker.Mock()
    csv_data_loader.load_data.return_value = __get_jira_data()
    jira_data_loader = JiraDataLoader(csv_data_loader)
    jira_data = jira_data_loader.load_data("test_data/jira_metrics.csv")

    assert jira_data is not None
    assert jira_data.get_projects() == ['Commerce']

