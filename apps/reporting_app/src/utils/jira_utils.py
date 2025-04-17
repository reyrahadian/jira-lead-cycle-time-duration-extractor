import re

def create_jira_link(key):
        return f'https://mecca-brands.atlassian.net/browse/{key}'

class JiraTicketHelpers:
    @staticmethod
    def get_components_from_summary(summary: str)->list[str]:
        if summary is None:
            return []

        # Extract content between square brackets if present
        matches = re.findall(r'\[(.*?)\]', summary)

        if not matches:
                return []

        # Get first match and split on pipe
        components = matches[0].split('|')

        # Clean and return components
        return [comp.strip() for comp in components]