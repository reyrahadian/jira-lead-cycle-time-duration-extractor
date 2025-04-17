from dash import html, dcc
import dash_bootstrap_components as dbc
from data.loaders import JiraDataLoaderWithCache
from components.tabs.teams_dashboard.components.filters import create_filters

jira_data_loader = JiraDataLoaderWithCache()
jira_data = jira_data_loader.load_data()

UNIQUE_PROJECTS = jira_data.projects

def create_teams_tab():
    return dbc.Tab(
        label='Teams Dashboard',
        id='teams-dashboard-tab',
        children=[
            html.Div([
                # Left column - Filters
                html.Div([
                    dbc.Card([
                        dbc.CardBody(create_filters(unique_projects=UNIQUE_PROJECTS)),
                    ]),
                ], style={'width': '20%', 'paddingRight': '20px', 'paddingBottom': '20px'}),

                # Right column - Charts and Tables
                html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='ticket-progression-chart'),
                        dcc.Graph(id='avg-ticket-progression-chart'),
                        dcc.Graph(id='ticket-type-distribution-pie-chart')
                        ])
                    ])
                ], style={'width': '75%'})
            ], style={'display': 'flex', 'flexDirection': 'row'})
        ]
    )