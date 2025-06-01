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
                ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right column - Average Days Table
                html.Div([
                    html.H4("Average Days per Stage",
                            style={'marginBottom': '10px'}),
                    dag.AgGrid(
                        id='avg-days-table',
                        columnDefs=[
                            {'headerName': 'Stage', 'field': 'Stage'},
                            {'headerName': 'Average Days', 'field': 'Days'}
                        ],
                        columnSize="sizeToFit",
                        className="ag-theme-quartz",
                    )
                ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginBottom': '20px'}),
            # Stage Tickets Panel
            html.Div([
                # Left side - Stage Tickets Table
                html.Div([
                    html.H3("Tickets in Selected Stage",
                            id='tickets-in-stage-title'),
                    dag.AgGrid(
                        id='tickets-in-stage-table',
                        columnDefs=[
                            {'headerName': 'Key', 'field': 'ID', 'type': 'text', 'cellRenderer': 'markdown', 'linkTarget': '_blank', 'pinned': 'left', 'resizable': True},
                            {'headerName': 'Summary', 'field': 'Name', 'resizable': True, 'width': 400, 'tooltipField': 'Name'},
                            {'headerName': 'Type', 'field': 'Type', 'resizable': True},
                            {'headerName': 'Priority', 'field': 'Priority', 'resizable': True},
                            {'headerName': 'Current Stage', 'field': 'Stage', 'resizable': True},
                            {
                                'headerName': 'Days in Stage',
                                'field': 'days_in_stage',
                                'resizable': True,
                                "cellStyle": {
                                    "styleConditions": [
                                        {
                                            "condition": "params.data.thresholds && params.value >= params.data.thresholds.critical",
                                            "style": {"backgroundColor": "#ffcdd2", "color": "#c62828"}
                                        },
                                        {
                                            "condition": "params.data.thresholds && params.value >= params.data.thresholds.warning",
                                            "style": {"backgroundColor": "#fff9c4", "color": "#f9a825"}
                                        },
                                        {
                                            "condition": "params.data.thresholds && params.value < params.data.thresholds.warning",
                                            "style": {"backgroundColor": "#c8e6c9", "color": "#2e7d32"}
                                        }
                                    ],
                                    "defaultStyle": {
                                        "backgroundColor": "#f8f9fa",
                                        "color": "#000000"
                                    }
                                }
                            },
                            {'headerName': 'Story Points', 'field': 'StoryPoints', 'resizable': True},
                            {'headerName': 'Sprint', 'field': 'Sprint', 'resizable': True, 'tooltipField': 'Sprint'}
                        ],
                        columnSize="sizeToFit",
                        className="ag-theme-quartz",
                        dashGridOptions={"rowSelection": "single"}
                    )
                ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right side - Ticket's Cycle Time Details for Stage Tickets
                html.Div([
                    html.H4("Ticket's Cycle Time",
                            id='tickets-in-stage-ticket-details-title',
                            style={'marginBottom': '20px'}),
                    dag.AgGrid(
                        id='tickets-in-stage-ticket-details-table',
                        columnDefs=[
                            {'headerName': 'Stage', 'field': 'stage'},
                            {
                                'headerName': 'Days',
                                'field': 'days',
                                "cellStyle": {
                                    "styleConditions": [
                                        {
                                            "condition": "params.data.thresholds && params.value >= params.data.thresholds.critical",
                                            "style": {"backgroundColor": "#ffcdd2", "color": "#c62828"}
                                        },
                                        {
                                            "condition": "params.data.thresholds && params.value >= params.data.thresholds.warning",
                                            "style": {"backgroundColor": "#fff9c4", "color": "#f9a825"}
                                        },
                                        {
                                            "condition": "params.data.thresholds && params.value < params.data.thresholds.warning",
                                            "style": {"backgroundColor": "#c8e6c9", "color": "#2e7d32"}
                                        }
                                    ]
                                }
                             }
                        ],
                        columnSize="sizeToFit",
                        className="ag-theme-quartz",
                    )
                ], id='tickets-in-stage-ticket-details-container', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginTop': '20px'})
            ])
        ])
    ])