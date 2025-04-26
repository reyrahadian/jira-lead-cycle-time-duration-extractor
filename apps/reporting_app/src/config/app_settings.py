import os
from dotenv import load_dotenv

class AppSettings:
    @property
    def DORA_VALID_PROJECT_NAMES(self) -> list[str]:
        load_dotenv()
        return os.getenv('DORA_VALID_PROJECT_NAMES', '').split(',') or []

    @property
    def REPORTING_CSV_PATH(self) -> str:
        load_dotenv()
        return os.getenv('REPORTING_CSV_PATH', '')
