from dash import html, dcc
from src.reporting_app.data.loader import UNIQUE_PROJECTS
from src.reporting_app.components.tabs.teams_dashboard.components.filters import create_filters

def create_teams_tab():
    return dcc.Tab(
        label='Teams Dashboard',
        value='teams-dashboard-tab',
        children=[
            html.Div([
                # Left column - Filters
                html.Div([
                    create_filters(unique_projects=UNIQUE_PROJECTS),
                ], style={'width': '20%', 'padding': '10px'}),

                # Right column - Charts and Tables
                html.Div([
                    dcc.Graph(id='ticket-progression-chart'),
                    dcc.Graph(id='avg-ticket-progression-chart'),
                    dcc.Graph(id='ticket-type-distribution-pie-chart')
                ], style={'width': '75%', 'padding': '10px'})
            ], style={'display': 'flex', 'flex-direction': 'row'})
        ]
    )