from dash import Dash, html
from src.reporting_app.config.constants import COLORS
from src.reporting_app.config.styles import *
from src.reporting_app.components.header import create_header
from src.reporting_app.components.filters import create_filters
from src.reporting_app.components.sprint_metrics import create_sprint_metrics
from src.reporting_app.components.charts import create_charts
from src.reporting_app.components.tables import create_tables
from src.reporting_app.data.loader import JIRA_TICKETS, UNIQUE_PROJECTS, UNIQUE_COMPONENTS
from src.reporting_app.callbacks import filter_callbacks, chart_callbacks, table_callbacks

# Initialize Dash App
app = Dash(__name__)

# Create main layout
app.layout = html.Div([
    create_header(),
    html.Div([
        # Left column - Filters
        html.Div([
            create_filters(unique_projects=UNIQUE_PROJECTS, unique_components=UNIQUE_COMPONENTS),
            create_sprint_metrics(),
        ], style={'width': '20%', 'padding': '10px'}),

        # Right column - Charts and Tables
        html.Div([
            create_charts(),
            create_tables(),
        ], style={'width': '75%', 'padding': '10px'}),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'})

# Register callbacks with app
filter_callbacks.init_callbacks(app, JIRA_TICKETS)
chart_callbacks.init_callbacks(app, JIRA_TICKETS)
table_callbacks.init_callbacks(app, JIRA_TICKETS)

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)