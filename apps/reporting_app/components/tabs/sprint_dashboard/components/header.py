from dash import html, dcc
from config.styles import CARD_STYLE
from config.constants import COLORS

def create_header():
    """Create the header component for the dashboard."""
    header_style = {
        **CARD_STYLE,
        'margin-bottom': '20px',
        'text-align': 'center',
        'display': 'flex',
        'justify-content': 'space-between',
        'align-items': 'center'
    }

    return html.Div([
        # Left side - empty div for alignment
        html.Div(style={'width': '100px'}),

        # Center - title and subtitle
        html.Div([
            html.H1(
                "Jira Tickets Analysis Dashboard",
                style={'color': COLORS['primary'], 'margin-bottom': '10px'}
            ),
            html.P(
                "Track and analyze ticket progression across different stages and sprints",
                style={'color': COLORS['secondary']}
            )
        ]),

        # Right side - refresh button
        html.Div([
            html.Button(
                "↻ Refresh Data",
                id='refresh-data-button',
                style={
                    'backgroundColor': COLORS['primary'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }
            )
        ], style={'width': '100px'})
    ], style=header_style)