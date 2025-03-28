from dash import html, dcc
from config.styles import CARD_STYLE
from config.constants import VALID_COMPONENTS, COLORS

def create_filters(unique_projects=[], unique_components=[]):
    """Create the filters section of the dashboard."""
    filters = html.Div([
        html.H2("Filters", style={'color': COLORS['primary'], 'margin-bottom': '20px'}),
        html.Div([
            html.Label("Project:", style={'font-weight': 'bold', 'color': COLORS['secondary']}),
            dcc.Dropdown(
                id='project-dropdown',
                options=[{'label': project, 'value': project} for project in unique_projects],
                value=unique_projects[0] if unique_projects else None,
                multi=False,
                style={'margin-bottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Squad:", style={'font-weight': 'bold', 'color': COLORS['secondary']}),
            dcc.Dropdown(
                id='squad-dropdown',
                options=[],  # Populated by callback
                value=None,
                multi=False,
                placeholder="Select squad (optional)",
                style={'margin-bottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Sprint:", style={'font-weight': 'bold', 'color': COLORS['secondary']}),
            dcc.Dropdown(
                id='sprint-dropdown',
                options=[],  # Populated by callback
                value=None,
                multi=False,
                style={'margin-bottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Ticket Type:", style={'font-weight': 'bold', 'color': COLORS['secondary']}),
            dcc.Dropdown(
                id='type-dropdown',
                options=[],
                value=[],
                multi=True,
                placeholder="Select ticket type(s)",
                style={'margin-bottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Components:", style={'font-weight': 'bold', 'color': COLORS['secondary']}),
            dcc.Dropdown(
                id='components-dropdown',
                options=[{'label': comp, 'value': comp} for comp in unique_components],
                value=[],
                multi=True,
                placeholder="Select component(s)",
                style={'margin-bottom': '15px'}
            ),
        ]),
        html.Div([
            html.Label("Specific Ticket:", style={'font-weight': 'bold', 'color': COLORS['secondary']}),
            dcc.Dropdown(
                id='ticket-dropdown',
                options=[],
                value=None,
                multi=False,
                placeholder="Select a specific ticket",
                style={'margin-bottom': '15px'}
            ),
        ]),
    ], style=CARD_STYLE)

    return filters