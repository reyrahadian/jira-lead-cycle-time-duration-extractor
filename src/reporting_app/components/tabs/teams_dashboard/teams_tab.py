from dash import html, dcc
from src.reporting_app.config.styles import CARD_STYLE

def create_teams_tab():
    return dcc.Tab(
        label='Teams Dashboard',
        value='teams-dashboard-tab',
        children=[
            html.Div([
                dcc.Graph(id='ticket-progression-chart'),
                dcc.Graph(id='avg-ticket-progression-chart'),
                dcc.Graph(id='ticket-type-distribution-pie-chart')
            ])
        ]
    )