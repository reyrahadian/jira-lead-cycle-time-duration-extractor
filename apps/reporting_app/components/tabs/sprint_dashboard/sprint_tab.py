from dash import html, dcc
from components.tabs.sprint_dashboard.components.filters import create_filters
from components.tabs.sprint_dashboard.components.sprint_metrics import create_sprint_metrics
from components.tabs.sprint_dashboard.components.charts import create_charts
from components.tabs.sprint_dashboard.components.tables import create_tables
from data.loader import UNIQUE_PROJECTS, UNIQUE_COMPONENTS

def create_sprint_tab():
    return dcc.Tab(
        label='Sprint Dashboard',
        value='sprint-dashboard-tab',
        children=html.Div([
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
            ], style={'display': 'flex', 'flex-direction': 'row'})
        ])
    )
