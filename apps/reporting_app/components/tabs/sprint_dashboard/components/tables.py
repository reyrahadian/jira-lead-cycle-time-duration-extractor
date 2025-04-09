from dash import html, dash_table
import dash_bootstrap_components as dbc
from config.styles import TABLE_HEADER_STYLE, TABLE_CELL_STYLE

def create_tables():
    """Create the tables section of the dashboard."""
    return html.Div([
        dbc.Card([
        # Combined Details Panel
            dbc.CardBody([
                # Left side - Warning Tickets
                html.Div([
                    html.H2("Tickets Exceeding Stage Thresholds",
                            style={'marginBottom': '20px'}),
                    dash_table.DataTable(
                        id='tickets-exceeding-threshold-table',
                        columns=[
                            {'name': 'Key', 'id': 'ID', 'type': 'text', 'presentation': 'markdown'},
                            {'name': 'Summary', 'id': 'Name'},
                            {'name': 'Type', 'id': 'Type'},
                            {'name': 'Priority', 'id': 'Priority'},
                            {'name': 'Current Stage', 'id': 'Stage'},
                            {'name': 'Stages Exceeding Threshold', 'id': 'exceeding_stages'},
                            {'name': 'Story Points', 'id': 'StoryPoints'},
                            {'name': 'Assignee', 'id': 'AssigneeName'},
                            {'name': 'Sprint', 'id': 'Sprint'},
                        ],
                        markdown_options={'link_target': '_blank'},
                        sort_action='native',  # Enable native sorting
                        sort_mode='multi',     # Allow sorting by multiple columns
                        style_data_conditional=[
                            {
                                'if': {
                                    'column_id': 'Stage',
                                    'filter_query': '{Stage} != "Done" && {Stage} != "Closed" && {Stage} != "Rejected"'
                                },
                                'backgroundColor': '#ffeb9c',  # Light yellow background
                                'color': '#9c6500'  # Dark amber text
                            }
                        ],
                        style_table={'overflowX': 'auto'},
                        page_size=10,
                        row_selectable='single',
                        selected_rows=[],
                        style_header=TABLE_HEADER_STYLE,
                        style_cell=TABLE_CELL_STYLE
                    )
                ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right side - Stage Duration Details (moved from left)
                html.Div([
                    html.H2("Stage Duration Details",
                            id='tickets-exceeding-threshold-details-title',
                            style={'marginBottom': '20px', 'display': 'none'}),
                    dash_table.DataTable(
                        id='tickets-exceeding-threshold-details-table',
                        columns=[
                            {'name': 'Stage', 'id': 'stage'},
                            {'name': 'Days', 'id': 'days'}
                        ],
                        style_table={'overflowX': 'auto'},
                        style_header=TABLE_HEADER_STYLE,
                        style_cell=TABLE_CELL_STYLE
                    )
                ], id='tickets-exceeding-threshold-details-container', style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ]),
        ], style={'marginTop': '20px'}),
        # Defects Table Section
        dbc.Card([
            dbc.CardBody([
                html.H2("Defects Created During Sprint",
                        style={'marginBottom': '20px'}),
                dash_table.DataTable(
                id='defects-table',
                columns=[
                    {'name': 'Key', 'id': 'ID', 'type': 'text', 'presentation': 'markdown'},
                    {'name': 'Summary', 'id': 'Name'},
                    {'name': 'Priority', 'id': 'Priority'},
                    {'name': 'Stage', 'id': 'Stage'},
                    {'name': 'Story Points', 'id': 'StoryPoints', 'type': 'numeric'},
                    {'name': 'Parent Type', 'id': 'ParentType'},
                    {'name': 'Parent Name', 'id': 'ParentName'}
                ],
                markdown_options={'link_target': '_blank'},
                sort_action='native',  # Enable native sorting
                sort_mode='multi',     # Allow sorting by multiple columns
                style_table={'overflowX': 'auto'},
                page_size=10,
                style_header=TABLE_HEADER_STYLE,
                style_cell=TABLE_CELL_STYLE
                )
            ]),
        ], style={'marginTop': '20px'}),

        # Sprint Tickets Section
        dbc.Card([
            dbc.CardBody([
                html.H2("Sprint Tickets",
                        style={'marginBottom': '20px'}),
                dash_table.DataTable(
                id='sprint-tickets-table',
                columns=[
                    {'name': 'Key', 'id': 'ID', 'type': 'text', 'presentation': 'markdown'},
                    {'name': 'Summary', 'id': 'Name'},
                    {'name': 'Type', 'id': 'Type'},
                    {'name': 'Parent Type', 'id': 'ParentType'},
                    {'name': 'Parent Name', 'id': 'ParentName'},
                    {'name': 'Stage', 'id': 'Stage'},
                    {'name': 'Story Points', 'id': 'StoryPoints', 'type': 'numeric'},
                    {'name': 'Fix Versions', 'id': 'FixVersions'},
                    {'name': 'Created', 'id': 'CreatedDate'},
                    {'name': 'Updated', 'id': 'UpdatedDate'},
                    {'name': 'Sprint', 'id': 'Sprint'}
                ],
                markdown_options={'link_target': '_blank'},
                sort_action='native',  # Enable native sorting
                sort_mode='multi',     # Allow sorting by multiple columns
                style_table={'overflowX': 'auto'},
                page_size=10,
                style_header=TABLE_HEADER_STYLE,
                style_cell=TABLE_CELL_STYLE
                )
            ]),
        ], style={'marginTop': '20px'}),
    ])