from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from apps.reporting_app.src.components.tabs.sprint_dashboard.callbacks import avg_cycletime_callbacks as sprint_chart_callbacks, filters_callbacks as sprint_filter_callbacks, threshold_tickets_table_callbacks as sprint_table_callbacks
from data.loaders import JiraDataLoaderWithCache
from components.tabs.sprint_dashboard.components.header import create_header
from components.tabs.sprint_dashboard.sprint_tab import create_sprint_tab
from components.tabs.teams_dashboard.teams_tab import create_teams_tab
from components.tabs.sprint_dashboard.callbacks import header_callbacks as sprint_header_callbacks
from components.tabs.teams_dashboard.callbacks import chart_callbacks as teams_chart_callbacks
from flask import send_file
import os

# load jira data
jira_data_loader = JiraDataLoaderWithCache()
jira_data = jira_data_loader.load_data()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

@app.server.route('/download_csv_file')
def download_jira_csv():
    csv_path = jira_data_loader.get_csv_filepath()
    if not os.path.exists(csv_path):
        return "CSV file not found", 404
    return send_file(csv_path, as_attachment=True, download_name='jira_metrics.csv', mimetype='text/csv')

# Create main layout with tabs
app.layout = html.Div([
    # Add dcc.Store component to store ticket IDs
    dcc.Store(id='tickets-in-stage-ticket-ids'),

    create_header(),
    dbc.Tabs([
        create_sprint_tab(),
        create_teams_tab(),
    ], id='tabs-component',style={'margin-top': '10px'}),

    # Add a placeholder for the notification
    html.Div(id='notification', style={"position": "fixed", "top": 10, "right": 10, "zIndex": 9999}),

], style={'minHeight': '100vh', 'padding': '20px', 'backgroundColor': '#f8f9fa'})

# Register callbacks with app
sprint_filter_callbacks.init_callbacks(app, jira_data.tickets)
sprint_chart_callbacks.init_callbacks(app, jira_data.tickets)
sprint_table_callbacks.init_callbacks(app, jira_data.tickets)
sprint_header_callbacks.init_callbacks(app, jira_data.tickets)
teams_chart_callbacks.init_callbacks(app, jira_data.tickets)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=8050)