from dash import html, dcc

def create_filters(unique_projects=[], unique_components=[]):
    """Create the filters section of the dashboard."""
    filters = html.Div([
        html.H2("Filters", style={'marginBottom': '20px'}),
        html.Div([
                html.Label("Project:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='teams-tab-project-dropdown',
                options=[{'label': project, 'value': project} for project in unique_projects],
                value=unique_projects[0] if unique_projects else None,
                multi=False,
                style={'marginBottom': '15px'}
            ),
            html.Label("Date Range:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
            dcc.DatePickerRange(
                id='teams-tab-date-range',
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                calendar_orientation='horizontal',
                style={'marginBottom': '15px'}
            ),
        ]),
    ])

    return filters