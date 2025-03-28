from dash import Dash, html, dcc
from config.constants import COLORS
from data.loader import JIRA_TICKETS
from components.tabs.sprint_dashboard.components.header import create_header
from components.tabs.sprint_dashboard  import create_sprint_tab
from components.tabs.teams_dashboard import create_teams_tab
from components.tabs.sprint_dashboard.callbacks import filter_callbacks as sprint_filter_callbacks, \
    chart_callbacks as sprint_chart_callbacks, table_callbacks as sprint_table_callbacks
from components.tabs.teams_dashboard.callbacks import chart_callbacks as teams_chart_callbacks

# Initialize Dash App
app = Dash(__name__)

# Create main layout with tabs
app.layout = html.Div([
    create_header(),
    dcc.Tabs([
        create_teams_tab(),
        create_sprint_tab(),
    ], id='tabs-component'),

], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'})

# Register callbacks with app
sprint_filter_callbacks.init_callbacks(app, JIRA_TICKETS)
sprint_chart_callbacks.init_callbacks(app, JIRA_TICKETS)
sprint_table_callbacks.init_callbacks(app, JIRA_TICKETS)
teams_chart_callbacks.init_callbacks(app, JIRA_TICKETS)

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)