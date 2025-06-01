from dash import html, dcc
import dash_bootstrap_components as dbc
from src.components.tabs.sprint_dashboard.components.filters import create_filters
from src.components.tabs.sprint_dashboard.components.sprint_goals import create_sprint_metrics
from src.components.tabs.sprint_dashboard.components.avg_cycletime import create_avg_cycletime_report
from src.components.tabs.sprint_dashboard.components.sprint_tickets import create_sprint_tickets
from src.data.data_loaders import JiraData
from src.config.app_settings import AppSettings

def create_sprint_tab(jira_data: JiraData):
    app_settings = AppSettings()
    projects = [project for project in jira_data.get_projects() if project in app_settings.SPRINT_DASHBOARD_VALID_PROJECT_NAMES]

    filters = html.Div([
        html.Div([
                # Left column - Filters
                html.Div([
                    dbc.Card([
                        dbc.CardBody(create_filters(projects=projects)),
                    ]),
                    dbc.Card([
                        dbc.CardBody(create_sprint_metrics()),
                    ], style={'marginTop': '20px'}),
                ], style={'width': '20%', 'paddingRight': '20px', 'paddingBottom': '20px'}),

                # Right column - Charts and Tables
                html.Div([
                    create_avg_cycletime_report(),
                    create_sprint_tickets(),
                ], style={'width': '75%'}),
            ], style={'display': 'flex', 'flexDirection': 'row'})
    ])
    return dcc.Tab(
        label='Sprint Dashboard',
        id='sprint-dashboard-tab',
        children=filters
    )
