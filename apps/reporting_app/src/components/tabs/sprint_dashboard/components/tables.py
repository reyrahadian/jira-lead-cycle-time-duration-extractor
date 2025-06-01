from dash import html, dash_table
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from src.config.styles import TABLE_HEADER_STYLE, TABLE_CELL_STYLE
from src.components.tabs.sprint_dashboard.components.sprint_tickets import create_sprint_tickets

def create_tables():
    """Create the tables section of the dashboard."""
    return html.Div([
        create_sprint_tickets(),
        dbc.Card([
        # Combined Details Panel
            dbc.CardBody([
                html.Div([
                    # Left side - Warning Tickets
                    html.Div([
                    html.H2("Tickets Exceeding Stage Thresholds",
                            style={'marginBottom': '20px'}),
                    dag.AgGrid(
                        id='tickets-exceeding-threshold-table',
                        columnDefs=[
                            {"headerName": "Key", "field": "ID", "resizable": True, "cellRenderer": "markdown", "linkTarget": "_blank", "pinned": "left"},
                            {"headerName": "Summary", "field": "Name", "resizable": True, "width": 400, "tooltipField": "Name"},
                            {"headerName": "Type", "field": "Type", "resizable": True},
                            {"headerName": "Priority", "field": "Priority", "resizable": True},
                            {"headerName": "Current Stage", "field": "Stage", "resizable": True},
                            {"headerName": "Stages Exceeding Threshold", "field": "exceeding_stages", "resizable": True},
                            {"headerName": "Story Points", "field": "StoryPoints", "resizable": True},
                            {"headerName": "Assignee", "field": "AssigneeName", "resizable": True, "tooltipField": "AssigneeName"},
                            {"headerName": "Sprint", "field": "Sprint", "resizable": True, "tooltipField": "Sprint"},
                        ],
                        columnSize="sizeToFit",
                        className="ag-theme-quartz",
                        dashGridOptions={"rowSelection": "single"}
                    )
                ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                    # Right side - Ticket's Cycle Time
                    html.Div([
                        html.H4("Ticket's Cycle Time",
                                id='tickets-exceeding-threshold-details-title',
                                style={'marginBottom': '20px'}),
                        dag.AgGrid(
                            id='tickets-exceeding-threshold-details-table',
                            columnDefs=[
                                {"headerName": "Stage", "field": "stage", "resizable": True},
                                {
                                    "headerName": "Days",
                                    "field": "days",
                                    "resizable": True,
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
                            className="ag-theme-quartz"
                        )
                    ], id='tickets-exceeding-threshold-details-container', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px'})
            ]),
        ], style={'marginTop': '20px'}),
        # Defects Table Section
        dbc.Card([
            dbc.CardBody([
                html.H2("Defects Created During Sprint",
                        style={'marginBottom': '20px'}),
                dag.AgGrid(
                id='defects-table',
                columnDefs=[
                    {"headerName": "Key", "field": "ID", "resizable": True, "cellRenderer": "markdown", "linkTarget": "_blank", "pinned": "left"},
                    {"headerName": "Summary", "field": "Name", "resizable": True, "width": 400, "tooltipField": "Name"},
                    {"headerName": "Priority", "field": "Priority", "resizable": True},
                    {"headerName": "Stage", "field": "Stage", "resizable": True},
                    {"headerName": "Story Points", "field": "StoryPoints", "type": "numeric", "resizable": True},
                    {"headerName": "Parent Type", "field": "ParentType", "resizable": True},
                    {"headerName": "Parent Name", "field": "ParentName", "resizable": True, "tooltipField": "ParentName"}
                ],
                columnSize="sizeToFit",
                className="ag-theme-quartz",
                )
            ]),
        ], style={'marginTop': '20px'}),

        # Sprint Tickets Section
        dbc.Card([
            dbc.CardBody([
                html.H2("Sprint Tickets",
                        style={'marginBottom': '20px'}),
                dag.AgGrid(
                id='sprint-tickets-table',
                columnDefs=[
                    {"headerName": "Key", "field": "ID", "resizable": True, "cellRenderer": "markdown", "linkTarget": "_blank", "pinned": "left"},
                    {"headerName": "Summary", "field": "Name", "resizable": True, "width": 400, "tooltipField": "Name"},
                    {"headerName": "Type", "field": "Type", "resizable": True},
                    {"headerName": "Parent Type", "field": "ParentType", "resizable": True},
                    {"headerName": "Parent Name", "field": "ParentName", "resizable": True, "tooltipField": "ParentName"},
                    {"headerName": "Stage", "field": "Stage", "resizable": True},
                    {"headerName": "Story Points", "field": "StoryPoints", "type": "numeric", "resizable": True},
                    {"headerName": "Fix Versions", "field": "FixVersions", "resizable": True, "tooltipField": "FixVersions"},
                    {"headerName": "Created", "field": "CreatedDate", "resizable": True},
                    {"headerName": "Updated", "field": "UpdatedDate", "resizable": True},
                    {"headerName": "Sprint", "field": "Sprint", "resizable": True, "tooltipField": "Sprint"},
                ],
                columnSize="sizeToFit",
                className="ag-theme-quartz",
                )
            ]),
        ], style={'marginTop': '20px'}),
    ])