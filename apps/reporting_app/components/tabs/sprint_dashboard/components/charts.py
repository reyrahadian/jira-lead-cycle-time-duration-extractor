from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from config.styles import TABLE_HEADER_STYLE, TABLE_CELL_STYLE
def create_charts():
    """Create the charts section of the dashboard."""
    return html.Div([  # Return a single Div containing all elements
        dbc.Card([
            dbc.CardBody([  # Wrap everything in a Div
                html.H2("Tickets Cycle Time",
                        style={'marginBottom': '20px'}),
            # Create a flex container for the graph and average days table
            html.Div([
                # Left column - Graph
                html.Div([
                    dcc.Graph(id='tickets-in-stage-bar-chart')
                ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right column - Average Days Table
                html.Div([
                    html.H3("Average Days per Stage",
                            style={'marginBottom': '10px'}),
                    dash_table.DataTable(
                        id='avg-days-table',
                        columns=[
                            {'name': 'Stage', 'id': 'Stage'},
                            {'name': 'Average Days', 'id': 'Days'}
                        ],
                        style_header=TABLE_HEADER_STYLE,
                        style_cell=TABLE_CELL_STYLE
                    )
                ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginBottom': '20px'}),
            # Stage Tickets Panel
            html.Div([
                # Left side - Stage Tickets Table
                html.Div([
                    html.H3("Tickets in Selected Stage",
                            id='tickets-in-stage-title',
                            style={'display': 'none'}),
                    dash_table.DataTable(
                        id='tickets-in-stage-table',
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
                        style_table={'overflowX': 'auto'},
                        page_size=10,
                        style_header=TABLE_HEADER_STYLE,
                        style_cell=TABLE_CELL_STYLE
                    )
                ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right side - Stage Duration Details for Stage Tickets
                html.Div([
                    html.H3("Stage Duration Details",
                            id='tickets-in-stage-ticket-details-title',
                            style={'marginBottom': '20px', 'display': 'none'}),
                    dash_table.DataTable(
                        id='tickets-in-stage-ticket-details-table',
                        columns=[
                            {'name': 'Stage', 'id': 'stage'},
                            {'name': 'Days', 'id': 'days'}
                        ],
                        style_table={'overflowX': 'auto'},
                        style_header=TABLE_HEADER_STYLE,
                        style_cell=TABLE_CELL_STYLE
                    )
                ], id='tickets-in-stage-ticket-details-container', style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginTop': '20px'})
            ])
        ])
    ])