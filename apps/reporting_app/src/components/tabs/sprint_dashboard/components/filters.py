from dash import html, dcc

def create_filters(projects=[]):
    """Create the filters section of the dashboard."""
    filters = html.Div([
        html.H2("Filters", style={'marginBottom': '20px'}),
        html.Div([
            html.Label("Project:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='project-dropdown',
                options=[{'label': project, 'value': project} for project in projects],
                value=None,
                multi=False,
                placeholder="Select project",
                style={'marginBottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Squad:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='squad-dropdown',
                options=[],
                value=None,
                multi=False,
                placeholder="Select squad (optional)",
                style={'marginBottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Sprint:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='sprint-dropdown',
                options=[],
                value=None,
                multi=False,
                style={'marginBottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Ticket Type:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='type-dropdown',
                options=[],
                value=[],
                multi=True,
                placeholder="Select ticket type(s)",
                style={'marginBottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Components:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='components-dropdown',
                options=[],
                value=[],
                multi=True,
                placeholder="Select component(s)",
                style={'marginBottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Specific Ticket:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='ticket-dropdown',
                options=[],
                value=None,
                multi=False,
                placeholder="Select a specific ticket",
                style={'marginBottom': '15px'}
            ),
        ]),
    ])

    return filters