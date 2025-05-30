from dash import html, dash_table
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from src.config.styles import TABLE_HEADER_STYLE, TABLE_CELL_STYLE

def create_tables():
    """Create the tables section of the dashboard."""
    return html.Div([
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
                            {"headerName": "Summary", "field": "Name", "resizable": True},
                            {"headerName": "Type", "field": "Type", "resizable": True},
                            {"headerName": "Priority", "field": "Priority", "resizable": True},
                            {"headerName": "Current Stage", "field": "Stage", "resizable": True},
                            {"headerName": "Stages Exceeding Threshold", "field": "exceeding_stages", "resizable": True},
                            {"headerName": "Story Points", "field": "StoryPoints", "resizable": True},
                            {"headerName": "Assignee", "field": "AssigneeName", "resizable": True},
                            {"headerName": "Sprint", "field": "Sprint", "resizable": True},
                        ],
                        columnSize="sizeToFit",
                        className="ag-theme-quartz",
                        dashGridOptions={"rowSelection": "single"}
                    )
                ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                    # Right side - Stage Duration Details (moved from left)
                    html.Div([
                        html.H3("Stage Duration Details",
                                id='tickets-exceeding-threshold-details-title',
                                style={'marginBottom': '20px', 'display': 'none'}),
                        dag.AgGrid(
                            id='tickets-exceeding-threshold-details-table',
                            columnDefs=[
                                {"headerName": "Stage", "field": "stage", "resizable": True},
                                {"headerName": "Days", "field": "days", "resizable": True}
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
                    {"headerName": "Summary", "field": "Name", "resizable": True},
                    {"headerName": "Priority", "field": "Priority", "resizable": True},
                    {"headerName": "Stage", "field": "Stage", "resizable": True},
                    {"headerName": "Story Points", "field": "StoryPoints", "type": "numeric", "resizable": True},
                    {"headerName": "Parent Type", "field": "ParentType", "resizable": True},
                    {"headerName": "Parent Name", "field": "ParentName", "resizable": True}
                ],
                columnSize="sizeToFit",
                className="ag-theme-quartz"
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
                    {"headerName": "Summary", "field": "Name", "resizable": True},
                    {"headerName": "Type", "field": "Type", "resizable": True},
                    {"headerName": "Parent Type", "field": "ParentType", "resizable": True},
                    {"headerName": "Parent Name", "field": "ParentName", "resizable": True},
                    {"headerName": "Stage", "field": "Stage", "resizable": True},
                    {"headerName": "Story Points", "field": "StoryPoints", "type": "numeric", "resizable": True},
                    {"headerName": "Fix Versions", "field": "FixVersions", "resizable": True},
                    {"headerName": "Created", "field": "CreatedDate", "resizable": True},
                    {"headerName": "Updated", "field": "UpdatedDate", "resizable": True},
                    {"headerName": "Sprint", "field": "Sprint", "resizable": True},
                ],
                columnSize="sizeToFit",
                className="ag-theme-quartz"
                )
            ]),
        ], style={'marginTop': '20px'}),
    ])