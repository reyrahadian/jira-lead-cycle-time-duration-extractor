from dash import Input, Output, callback, State
import dash_bootstrap_components as dbc  # Import dash-bootstrap-components
from dash.exceptions import PreventUpdate
from src.data.loaders import JiraDataLoaderWithCache

def init_callbacks(app, jira_tickets):
    @callback(
        [Output('refresh-data-button', 'children'),
         Output('notification', 'children')],
        Input('refresh-data-button', 'n_clicks')
    )
    def refresh_data(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        # # Reload the CSV data
        # new_data = load_data()
        # processed_data = process_components(new_data)

        # # Convert to dictionary format for the data store
        # data_dict = processed_data.to_dict('records')

        # Return the updated data and a success notification
        return "↻ Refresh Data", data_dict, dbc.Toast("Data refreshed successfully!", duration=4000, is_open=True, color="success")