from dash import html
from src.reporting_app.config.styles import CARD_STYLE
from src.reporting_app.config.constants import COLORS

def create_header():
    """Create the header component for the dashboard."""
    header_style = {
        **CARD_STYLE,
        'margin-bottom': '20px',
        'text-align': 'center'
    }

    return html.Div([
        html.H1(
            "Jira Tickets Analysis Dashboard",
            style={'color': COLORS['primary'], 'margin-bottom': '10px'}
        ),
        html.P(
            "Track and analyze ticket progression across different stages and sprints",
            style={'color': COLORS['secondary']}
        )
    ], style=header_style)