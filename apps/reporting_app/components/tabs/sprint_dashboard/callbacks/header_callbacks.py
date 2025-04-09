from dash import Input, Output, callback, State
import dash_bootstrap_components as dbc  # Import dash-bootstrap-components
from dash.exceptions import PreventUpdate
from data.loader import load_data, process_components

def init_callbacks(app, jira_tickets):
    @callback(
        [Output('refresh-data-button', 'children'),
         Output('jira-data-store', 'data'),
         Output('notification', 'children')],
        Input('refresh-data-button', 'n_clicks'),
        State('jira-data-store', 'data')
    )
    def refresh_data(n_clicks, current_data):
        if n_clicks is None:
            raise PreventUpdate

        # Reload the CSV data
        new_data = load_data()
        processed_data = process_components(new_data)

        # Convert to dictionary format for the data store
        data_dict = processed_data.to_dict('records')

        # Return the updated data and a success notification
        return "↻ Refresh Data", data_dict, dbc.Toast("Data refreshed successfully!", duration=4000, is_open=True, color="success")