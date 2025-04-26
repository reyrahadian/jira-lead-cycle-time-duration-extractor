import os

class AppSettings:
    @property
    def DORA_DASHBOARD_VALID_PROJECT_NAMES(self) -> list[str]:
        return os.getenv('DORA_DASHBOARD_VALID_PROJECT_NAMES', '').split(',') or []

    @property
    def REPORTING_CSV_PATH(self) -> str:
        return os.getenv('REPORTING_CSV_PATH', '')

    @property
    def SPRINT_DASHBOARD_VALID_PROJECT_NAMES(self) -> list[str]:
        return os.getenv('SPRINT_DASHBOARD_VALID_PROJECT_NAMES', '').split(',') or []
