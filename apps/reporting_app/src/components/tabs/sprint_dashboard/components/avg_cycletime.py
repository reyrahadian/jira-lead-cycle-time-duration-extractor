from dash import html, dcc, dash_table
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from src.config.styles import TABLE_HEADER_STYLE, TABLE_CELL_STYLE
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
                    dag.AgGrid(
                        id='avg-days-table',
                        columnDefs=[
                            {'headerName': 'Stage', 'field': 'Stage'},
                            {'headerName': 'Average Days', 'field': 'Days'}
                        ],
                        columnSize="sizeToFit",
                        className="ag-theme-quartz"
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
                    dag.AgGrid(
                        id='tickets-in-stage-table',
                        columnDefs=[
                            {'headerName': 'Key', 'field': 'ID', 'type': 'text', 'cellRenderer': 'markdown', 'linkTarget': '_blank', 'pinned': 'left', 'resizable': True},
                            {'headerName': 'Summary', 'field': 'Name', 'resizable': True},
                            {'headerName': 'Type', 'field': 'Type', 'resizable': True},
                            {'headerName': 'Priority', 'field': 'Priority', 'resizable': True},
                            {'headerName': 'Current Stage', 'field': 'Stage', 'resizable': True},
                            {'headerName': 'Days in Stage', 'field': 'days_in_stage', 'resizable': True},
                            {'headerName': 'Story Points', 'field': 'StoryPoints', 'resizable': True},
                            {'headerName': 'Sprint', 'field': 'Sprint', 'resizable': True}
                        ],
                        columnSize="sizeToFit",
                        className="ag-theme-quartz",
                        dashGridOptions={"rowSelection": "single"}
                    )
                ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right side - Stage Duration Details for Stage Tickets
                html.Div([
                    html.H4("Stage Duration Details",
                            id='tickets-in-stage-ticket-details-title',
                            style={'marginBottom': '20px', 'display': 'none'}),
                    dag.AgGrid(
                        id='tickets-in-stage-ticket-details-table',
                        columnDefs=[
                            {'headerName': 'Stage', 'field': 'stage'},
                            {'headerName': 'Days', 'field': 'days'}
                        ],
                        columnSize="sizeToFit",
                        className="ag-theme-quartz"
                    )
                ], id='tickets-in-stage-ticket-details-container', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginTop': '20px'})
            ])
        ])
    ])