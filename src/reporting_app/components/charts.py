from dash import html, dcc, dash_table
from src.reporting_app.config.styles import CARD_STYLE
from src.reporting_app.config.constants import COLORS

def create_charts():
    """Create the charts section of the dashboard."""
    return html.Div([  # Return a single Div containing all elements
        html.Div([  # Wrap everything in a Div
            html.H2("Tickets Cycle Time",
                    style={'color': COLORS['primary'], 'margin-bottom': '20px'}),
            dcc.Graph(id='stages-bar-chart'),
            # Stage Tickets Panel
            html.Div([
                # Left side - Stage Tickets Table
                html.Div([
                    html.H3("Tickets in Selected Stage",
                            id='selected-stage-title',
                            style={'display': 'none', 'color': COLORS['secondary']}),
                    dash_table.DataTable(
                        id='stage-tickets-table',
                        columns=[
                            {'name': 'Key', 'id': 'ID', 'type': 'text', 'presentation': 'markdown'},
                            {'name': 'Summary', 'id': 'Name'},
                            {'name': 'Type', 'id': 'Type'},
                            {'name': 'Priority', 'id': 'Priority'},
                            {'name': 'Current Stage', 'id': 'Stage'},
                            {'name': 'Days in Stage', 'id': 'days_in_stage'},
                            {'name': 'Story Points', 'id': 'StoryPoints'},
                            {'name': 'Sprint', 'id': 'Sprint'}
                        ],
                        markdown_options={'link_target': '_blank'},
                        row_selectable='single',
                        selected_rows=[],
                        style_table={'overflowX': 'auto', 'backgroundColor': COLORS['background']},
                        style_cell={
                            'textAlign': 'left',
                            'minWidth': '100px',
                            'maxWidth': '300px',
                            'whiteSpace': 'normal'
                        },
                        page_size=10,
                        style_header={
                            'backgroundColor': COLORS['primary'],
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'left'
                        }
                    )
                ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right side - Stage Duration Details for Stage Tickets
                html.Div([
                    html.H3("Stage Duration Details",
                            id='stage-ticket-details-title',
                            style={'color': COLORS['primary'], 'margin-bottom': '20px', 'display': 'none'}),
                    dash_table.DataTable(
                        id='stage-ticket-details-table',
                        columns=[
                            {'name': 'Stage', 'id': 'stage'},
                            {'name': 'Days', 'id': 'days'}
                        ],
                        style_table={'overflowX': 'auto', 'backgroundColor': COLORS['background']},
                        style_cell={
                            'textAlign': 'left',
                            'minWidth': '100px',
                            'maxWidth': '300px',
                            'whiteSpace': 'normal'
                        },
                        style_header={
                            'backgroundColor': COLORS['primary'],
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'left'
                        }
                    )
                ], id='stage-ticket-details-container', style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginTop': '20px'})
        ], style=CARD_STYLE)
    ])