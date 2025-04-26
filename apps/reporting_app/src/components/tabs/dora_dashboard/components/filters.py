from dash import html, dcc

def create_filters(projects=[]):
    """Create the filters section of the dashboard."""
    filters = html.Div([
        html.H2("Filters", style={'marginBottom': '20px'}),
        html.Div([
            html.Label("Projects:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='dora-tab-project-dropdown',
                options=[{'label': project, 'value': project} for project in projects],
                value=None,
                multi=True,
                placeholder="All projects",
                style={'marginBottom': '15px'}
            ),
            html.Label("Squads:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
            dcc.Dropdown(
                id='dora-tab-squads-dropdown',
                options=[],
                value=None,
                multi=True,
                placeholder="All squads",
                style={'marginBottom': '15px'}
            ),
            html.Label("Date Range:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
            dcc.Dropdown(
                id='dora-tab-time-range-dropdown',
                options=[
                    {'label': 'Last 6 Months', 'value': 'last_6_months'},
                    {'label': 'Last 3 Months', 'value': 'last_3_months'},
                    {'label': 'Last 2 Weeks', 'value': 'last_2_weeks'},
                    {'label': 'Last Week', 'value': 'last_week'},
                    {'label': 'Today', 'value': 'today'},
                    {'label': 'Custom Date Range', 'value': 'custom_date_range'},
                ],
                value='last_6_months',
                multi=False,
                style={'marginBottom': '15px'}
            ),
            html.Div(
                dcc.DatePickerRange(
                    id='dora-tab-date-range',
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    calendar_orientation='horizontal',
                    style={'marginBottom': '15px'}
                ),
                id='dora-tab-date-range-container',
                style={'display': 'none'}
            ),
        ]),
    ])

    return filters