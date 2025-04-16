from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from data.loader import JIRA_TICKETS
from components.tabs.sprint_dashboard.components.header import create_header
from components.tabs.sprint_dashboard import create_sprint_tab
from components.tabs.teams_dashboard import create_teams_tab
from components.tabs.sprint_dashboard.callbacks import filter_callbacks as sprint_filter_callbacks, \
    chart_callbacks as sprint_chart_callbacks, table_callbacks as sprint_table_callbacks, \
    header_callbacks as sprint_header_callbacks
from components.tabs.teams_dashboard.callbacks import chart_callbacks as teams_chart_callbacks

# --- Add for download route ---
from flask import send_file
import os

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Hidden download route for the main JIRA CSV file
def get_jira_csv_path():
    return os.getenv('REPORTING_CSV_PATH', "/mnt/c/workspace/jira-lead-cycle-time-duration-extractor/docker/data/jira_metrics.csv")

@app.server.route('/download_csv_file')
def download_jira_csv():
    csv_path = get_jira_csv_path()
    if not os.path.exists(csv_path):
        return "CSV file not found", 404
    return send_file(csv_path, as_attachment=True, download_name='jira_metrics.csv', mimetype='text/csv')
# --- End download route ---

# Create main layout with tabs
app.layout = html.Div([
    # Add dcc.Store component to store Jira data
    dcc.Store(id='jira-data-store', data=JIRA_TICKETS.to_dict('records')),
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
sprint_filter_callbacks.init_callbacks(app, JIRA_TICKETS)
sprint_chart_callbacks.init_callbacks(app, JIRA_TICKETS)
sprint_table_callbacks.init_callbacks(app, JIRA_TICKETS)
sprint_header_callbacks.init_callbacks(app, JIRA_TICKETS)
teams_chart_callbacks.init_callbacks(app, JIRA_TICKETS)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)