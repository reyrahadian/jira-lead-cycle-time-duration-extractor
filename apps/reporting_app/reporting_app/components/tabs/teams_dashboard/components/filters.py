from dash import html, dcc
from src.reporting_app.config.styles import CARD_STYLE
from src.reporting_app.config.constants import COLORS

def create_filters(unique_projects=[], unique_components=[]):
    """Create the filters section of the dashboard."""
    filters = html.Div([
        html.H2("Filters", style={'color': COLORS['primary'], 'margin-bottom': '20px'}),
        html.Div([
            html.Label("Project:", style={'font-weight': 'bold', 'color': COLORS['secondary']}),
            dcc.Dropdown(
                id='teams-tab-project-dropdown',
                options=[{'label': project, 'value': project} for project in unique_projects],
                value=unique_projects[0] if unique_projects else None,
                multi=False,
                style={'margin-bottom': '15px'}
            ),
            html.Label("Date Range:", style={'font-weight': 'bold', 'color': COLORS['secondary'], 'margin-top': '10px'}),
            dcc.DatePickerRange(
                id='teams-tab-date-range',
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                calendar_orientation='horizontal',
                style={'margin-bottom': '15px'}
            ),
        ]),
    ], style=CARD_STYLE)

    return filters