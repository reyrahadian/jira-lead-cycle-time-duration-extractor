from dash import html

def create_sprint_metrics():
    """Create the sprint metrics summary component."""
    sprint_metrics = html.Div([
        html.Div(id='sprint-goals', style={'marginBottom': '20px'}),
        html.Div([
            html.Div(id='sprint-dates', style={'marginBottom': '20px'})
        ]),
        html.Div([
            html.Div(id='sprint-stats', style={'marginBottom': '20px'})
        ])
    ])

    return sprint_metrics