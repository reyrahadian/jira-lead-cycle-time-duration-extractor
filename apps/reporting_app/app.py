from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from src.components.tabs.sprint_dashboard.callbacks \
    import avg_cycletime_callbacks, defects_table_callbacks, filters_callbacks, \
        sprint_goals_callbacks, sprint_tickets_callbacks, threshold_tickets_table_callbacks
from src.data.data_loaders import JiraDataSingleton
from src.components.tabs.sprint_dashboard.components.header import create_header
from src.components.tabs.sprint_dashboard.sprint_tab import create_sprint_tab
from src.components.tabs.teams_dashboard.teams_tab import create_teams_tab
from src.components.tabs.teams_dashboard.callbacks import chart_callbacks as teams_chart_callbacks
from src.components.tabs.dora_dashboard.dora_tab import create_dora_tab
from src.components.tabs.dora_dashboard.callbacks import filters_callbacks as dora_filters_callbacks
from src.components.tabs.dora_dashboard.callbacks import dora_tiles_callbacks
from flask import send_file
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# Access jira data
jira_data_singleton = JiraDataSingleton()
jira_data = jira_data_singleton.get_jira_data()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

@app.server.route('/download_csv_file')
def download_jira_csv():
    csv_path = jira_data_singleton.get_csv_filepath()
    if not os.path.exists(csv_path):
        return "CSV file not found", 404
    return send_file(csv_path, as_attachment=True, download_name='jira_metrics.csv', mimetype='text/csv')

# Create main layout with tabs
app.layout = html.Div([
    # Add dcc.Store component to store ticket IDs
    dcc.Store(id='tickets-in-stage-ticket-ids'),

    create_header(),
    dbc.Tabs([
        create_sprint_tab(jira_data),
        create_dora_tab(jira_data)
        #create_teams_tab(jira_data),
    ], id='tabs-component',style={'margin-top': '10px'}),

    # Add a placeholder for the notification
    html.Div(id='notification', style={"position": "fixed", "top": 10, "right": 10, "zIndex": 9999}),

], style={'minHeight': '100vh', 'padding': '20px', 'backgroundColor': '#f8f9fa'})

# Register callbacks with app
filters_callbacks.init_callbacks(app, jira_data.get_tickets())
sprint_goals_callbacks.init_callbacks(app, jira_data.get_tickets())
avg_cycletime_callbacks.init_callbacks(app, jira_data.get_tickets())
threshold_tickets_table_callbacks.init_callbacks(app, jira_data.get_tickets())
defects_table_callbacks.init_callbacks(app, jira_data.get_tickets())
sprint_tickets_callbacks.init_callbacks(app, jira_data.get_tickets())
dora_filters_callbacks.init_callbacks(app, jira_data.get_tickets())
dora_tiles_callbacks.init_callbacks(app, jira_data.get_tickets())
#teams_chart_callbacks.init_callbacks(app, jira_data.get_tickets())

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=8050)