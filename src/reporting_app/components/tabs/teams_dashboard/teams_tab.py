from dash import html, dcc
from src.reporting_app.config.styles import CARD_STYLE

def create_teams_tab():
    return dcc.Tab(
        label='Teams Dashboard',
        value='teams-dashboard-tab',
        children=[
            html.Div([
                dcc.Graph(id='ticket-progression-chart')
            ]),
            html.Div([
                html.H3('Teams Metrics', style={'color': '#2c3e50', 'margin-bottom': '20px'}),
                html.Div(id='teams-metrics-panel')
            ], style={
                **CARD_STYLE
            })
        ]
    )