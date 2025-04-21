import pandas as pd

class TestHelpers:
    @staticmethod
    def get_jira_data()->pd.DataFrame:
        return pd.read_csv("/mnt/c/workspace/jira-lead-cycle-time-duration-extractor/apps/reporting_app/tests/jira_metrics_mock.csv")