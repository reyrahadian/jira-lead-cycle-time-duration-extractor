from dash import html, dcc
import dash_bootstrap_components as dbc

def create_header():
    """Create the header component for the dashboard."""
    header_style = {
        'marginBottom': '20px',
        'textAlign': 'center',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center'
    }

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                # Left side - empty div for alignment
                html.Div(style={'width': '100px'}),

                # Center - title and subtitle
                html.Div([
                    html.H1(
                        "Jira Tickets Analysis Dashboard",
                        style={'marginBottom': '10px'}
                    ),
                    html.P(
                        "Track and analyze ticket progression across different stages and sprints",
                        style={'marginBottom': '10px'}
                    )
                ]),

                # Right side - refresh button
                html.Div([
                    html.Button(
                        "↻ Refresh Data",
                        id='refresh-data-button',
                        className='btn btn-primary'
                    )
                ], style={'width': '100px'})
            ], style=header_style)
        ])
    ])