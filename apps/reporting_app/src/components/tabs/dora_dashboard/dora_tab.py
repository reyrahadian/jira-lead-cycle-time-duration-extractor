from dash import html, dcc
import dash_bootstrap_components as dbc
from src.components.tabs.dora_dashboard.components.filters import create_filters
from src.components.tabs.dora_dashboard.components.dora_tiles import create_dora_tiles
from src.data.data_loaders import JiraData

def create_dora_tab(jira_data: JiraData):
    components = html.Div([
        html.Div([
                # Left column - Filters
                html.Div([
                    dbc.Card([
                        dbc.CardBody(create_filters(projects=jira_data.get_projects())),
                    ])
                ], style={'width': '20%', 'paddingRight': '20px', 'paddingBottom': '20px'}),

                # Right column - Charts and Tables
                html.Div([
                    create_dora_tiles(),
                ], style={'width': '75%'}),
            ], style={'display': 'flex', 'flexDirection': 'row'})
    ])
    return dcc.Tab(
            label='DORA Dashboard',
        id='dora-dashboard-tab',
        children=components
    )
