from dash import html, dcc
import dash_bootstrap_components as dbc

def create_header():
    """Create the header component for the dashboard."""
    header_style = {
        'marginBottom': '20px',
        'textAlign': 'center',
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'width': '100%'
    }

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                # Center - title and subtitle
                html.Div([
                    html.H1(
                        "Jira Tickets Analysis Dashboard",
                        style={'marginBottom': '10px', 'textAlign': 'center'}
                    ),
                    html.P(
                        "Track and analyze ticket progression across different stages and sprints",
                        style={'marginBottom': '10px', 'textAlign': 'center'}
                    )
                ], style={'width': '100%'})
            ], style=header_style)
        ])
    ])