from dash import html
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from src.components.tabs.sprint_dashboard.callbacks.sprint_tickets_with_options_callbacks import get_column_defs
def create_sprint_tickets():
    return dbc.Card([
        dbc.CardBody([
            html.H2("Sprint Tickets",
                    style={'marginBottom': '20px'}),
            html.Div([
                html.Div([
                    dbc.RadioItems(
                        id='sprint-tickets-with-options-radio',
                        options=[
                            {'label': 'All Tickets', 'value': 'all'},
                            {'label': 'Threshold Violation', 'value': 'threshold'},
                            {'label': 'Defects', 'value': 'defects'}
                        ],
                        value='all',
                        inline=True,
                        style={'marginBottom': '20px'}
                    ),
                    dag.AgGrid(
                        id='sprint-tickets-with-options-table',
                        columnDefs=get_column_defs(),
                        columnSize="sizeToFit",
                        className="ag-theme-quartz compact",
                        dashGridOptions={"rowSelection": "single", "tooltipShowDelay": 0},
                        defaultColDef={"resizable": True, "filter": "agTextColumnFilter", "floatingFilter": True}
                    )
                ], id="sprint-tickets-with-options-container-left", style={'width': '80%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                html.Div([
                    html.H4("Ticket's Cycle Time",
                            id='sprint-tickets-with-options-details-title',
                            style={'marginBottom': '20px'}),
                    dag.AgGrid(
                        id='sprint-tickets-with-options-details-table',
                        columnDefs=[
                            {"headerName": "Stage", "field": "stage", "tooltipField": "stage"},
                            {
                                "headerName": "Days",
                                "field": "days",
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
                        className="ag-theme-quartz compact",
                        dashGridOptions={"tooltipShowDelay": 0},
                    )
                ], id="sprint-tickets-with-options-container-right", style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '10px'})
        ])
    ], style={'marginTop': '20px'})