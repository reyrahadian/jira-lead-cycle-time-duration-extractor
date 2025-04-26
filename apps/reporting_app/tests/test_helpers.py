import pandas as pd
from pathlib import Path
class TestHelpers:
    @staticmethod
    def get_jira_data()->pd.DataFrame:
        # Get the absolute path to the CSV file
        basepath = Path()
        basedir = str(basepath.cwd())
        return pd.read_csv(f"{basedir}/apps/reporting_app/tests/jira_metrics_mock.csv")