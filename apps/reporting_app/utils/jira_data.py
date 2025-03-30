import pandas as pd

class JiraTickets:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.load_data()

    def load_data(self):
        self.df = pd.read_csv(self.csv_path)
        # ... any other data processing ...

    def reload_data(self):
        """Reload data from the CSV file"""
        self.load_data()

    def get_tickets_data(self):
        """Return the data in a format suitable for the data store"""
        return self.df.to_dict('records')