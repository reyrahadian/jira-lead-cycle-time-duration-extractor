from dash import html, dcc
import dash_bootstrap_components as dbc
from components.tabs.sprint_dashboard.components.filters import create_filters
from components.tabs.sprint_dashboard.components.sprint_metrics import create_sprint_metrics
from components.tabs.sprint_dashboard.components.charts import create_charts
from components.tabs.sprint_dashboard.components.tables import create_tables
from data.loader import UNIQUE_PROJECTS, UNIQUE_COMPONENTS

def create_sprint_tab():
    filters = html.Div([
        html.Div([
                # Left column - Filters
                html.Div([
                    dbc.Card([
                        dbc.CardBody(create_filters(unique_projects=UNIQUE_PROJECTS, unique_components=UNIQUE_COMPONENTS)),
                    ]),
                    dbc.Card([
                        dbc.CardBody(create_sprint_metrics()),
                    ], style={'marginTop': '20px'}),
                ], style={'width': '20%', 'paddingRight': '20px', 'paddingBottom': '20px'}),

                # Right column - Charts and Tables
                html.Div([
                    create_charts(),
                    create_tables(),
                ], style={'width': '75%'}),
            ], style={'display': 'flex', 'flexDirection': 'row'})
    ])
    return dcc.Tab(
        label='Sprint Dashboard',
        id='sprint-dashboard-tab',
        children=filters
    )
