import pandas as pd
from src.data.data_loaders import JiraDataLoader, CsvDataLoader
from src.data.data_filters import JiraDataFilter, JiraDataFilterService
from src.config.constants import COLUMN_NAME_ID
from tests.test_helpers import TestHelpers

def test_jiradataloader_filter_tickets(mocker):
    mock_csv_loader = mocker.Mock(spec=CsvDataLoader)
    mock_csv_loader.load_data.return_value = TestHelpers.get_jira_data()
    jira_data_loader = JiraDataLoader(mock_csv_loader)
    jira_data = jira_data_loader.load_data("jira_metrics.csv")

    filter = JiraDataFilter(project='Digital MECCA App')
    jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_data.get_tickets(), filter)
    assert jira_data_filter_result.squads == ['LFApp','UFApp','Website Experience', 'eCommerce']

    filter = JiraDataFilter(project='Digital MECCA App', squad='LFApp')
    jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_data.get_tickets(), filter)
    assert jira_data_filter_result.squads == ['LFApp']
    expected_sprints = [
        'LFW 7.2.25',
        'MOB - Sprint 1',
        'LFA - Sprint 31',
        'LFA - Sprint 30',
        'LFA - Sprint 29',
        'LFA - Sprint 28',
        'LFA - Sprint 27',
        'LFA - Sprint 26',
        'LFA - Sprint 25',
        'LFA - Sprint 24',
        'LFA - Sprint 23',
        'LFA - Sprint 22',
        'LFA - Sprint 20',
        'LFA - Sprint 17',
        'Shaping',
        'LFA - Sprint 7',
        'Dandelion - Refined',
        'Dandelion - Sprint 88',
        'Mecca App - Sprint 62',
        'MECCA App- Sprint 60',
        'MECCA App - Sprint 59',
        'MECCA App - Sprint 57',
        'MOB - Sprint 2',
        'LFA - Sprint 2',
        'MOB - Sprint 3',
        'MOB - Ready for Development'
    ]
    assert set(jira_data_filter_result.sprints) == set(expected_sprints)

    filter = JiraDataFilter(project='Digital MECCA App', squad='LFApp', sprint='MOB - Sprint 1')
    jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_data.get_tickets(), filter)
    assert jira_data_filter_result.squads == ['LFApp']
    assert jira_data_filter_result.sprints == ['MOB - Sprint 1','LFA - Sprint 31','LFA - Sprint 30']
    assert jira_data_filter_result.ticket_types == ['Bug','Story','Task']

    filter = JiraDataFilter(project='Digital MECCA App', squad='LFApp', sprint='MOB - Sprint 1', ticket_types=['Story'])
    jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_data.get_tickets(), filter)
    assert jira_data_filter_result.squads == ['LFApp']
    assert jira_data_filter_result.sprints == ['MOB - Sprint 1']
    assert jira_data_filter_result.ticket_types == ['Story']
    assert jira_data_filter_result.components == ['Frontend']

    filter = JiraDataFilter(project='Digital MECCA App', squad='LFApp', sprint='MOB - Sprint 1', ticket_types=['Story'], components=['Frontend'])
    jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_data.get_tickets(), filter)
    assert jira_data_filter_result.squads == ['LFApp']
    assert jira_data_filter_result.sprints == ['MOB - Sprint 1']
    assert jira_data_filter_result.ticket_types == ['Story']
    assert jira_data_filter_result.components == ['Frontend']

    filter = JiraDataFilter(project='Digital MECCA App', squad='LFApp', sprint='MOB - Sprint 1', ticket_types=['Story'],  components=['Frontend'], ticketId='DMA-1462')
    jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_data.get_tickets(), filter)
    assert jira_data_filter_result.squads == ['LFApp']
    assert jira_data_filter_result.sprints == ['MOB - Sprint 1']
    assert jira_data_filter_result.ticket_types == ['Story']
    assert jira_data_filter_result.components == ['Frontend']
    assert jira_data_filter_result.tickets[COLUMN_NAME_ID].iloc[0] == 'DMA-1462'

