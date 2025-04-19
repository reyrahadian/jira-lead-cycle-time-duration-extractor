from dash import html, dcc
import dash_bootstrap_components as dbc
from src.components.tabs.sprint_dashboard.components.filters import create_filters
from src.components.tabs.sprint_dashboard.components.sprint_goals import create_sprint_metrics
from src.components.tabs.sprint_dashboard.components.avg_cycletime import create_charts
from src.components.tabs.sprint_dashboard.components.tables import create_tables
from src.data.data_loaders import JiraData

def create_sprint_tab(jira_data: JiraData):
    filters = html.Div([
        html.Div([
                # Left column - Filters
                html.Div([
                    dbc.Card([
                        dbc.CardBody(create_filters(projects=jira_data.get_projects())),
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
