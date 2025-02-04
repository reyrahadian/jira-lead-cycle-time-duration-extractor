from dash import html
from src.reporting_app.config.styles import CARD_STYLE
from src.reporting_app.config.constants import COLORS

def create_sprint_metrics():
    """Create the sprint metrics summary component."""
    sprint_metrics = html.Div([
        html.Div(id='sprint-goals', style={'margin-bottom': '20px'}),
        html.Div([
            html.Div(id='total-points', style={'font-size': '1.2em', 'margin-bottom': '10px'}),
            html.Div(id='ticket-count', style={'font-size': '1.2em'})
        ], style={'color': COLORS['secondary']})
    ], style=CARD_STYLE)

    return sprint_metrics