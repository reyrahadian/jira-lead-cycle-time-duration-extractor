from src.utils.jira_utils import JiraTicketHelpers

def test_get_components_from_summary():
    assert JiraTicketHelpers.get_components_from_summary("[BFF|BFFWeb] - Update product catalog") == ["BFF", "BFFWeb"]
    assert JiraTicketHelpers.get_components_from_summary("[SFCC] - Update product catalog") == ["SFCC"]
    assert JiraTicketHelpers.get_components_from_summary("Update product catalog") == []
    assert JiraTicketHelpers.get_components_from_summary(None) == []
    assert JiraTicketHelpers.get_components_from_summary("") == []

