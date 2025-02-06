from dash import html
from src.reporting_app.config.styles import CARD_STYLE
from src.reporting_app.config.constants import COLORS

def create_sprint_metrics():
    """Create the sprint metrics summary component."""
    sprint_metrics = html.Div([
        html.Div(id='sprint-goals', style={'margin-bottom': '20px'}),
        html.Div([
            html.Div(id='sprint-dates', style={'margin-bottom': '20px'})
        ]),
        html.Div([
            html.Div(id='sprint-stats', style={'margin-bottom': '20px'})
        ])
    ], style=CARD_STYLE)

    return sprint_metrics