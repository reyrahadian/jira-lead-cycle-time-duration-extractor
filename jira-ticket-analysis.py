from dash import Dash, html, dcc, callback, Output, Input, dash_table, callback_context
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import json

#------------------------------------------------------------------------------
# Constants and Configuration
#------------------------------------------------------------------------------

STAGE_THRESHOLDS = {
    'default': {'warning': 2, 'critical': 5},  # Default thresholds in days
    'In Development': {'warning': 3, 'critical': 6},
    'In Code Review': {'warning': 1, 'critical': 2},
    'In PR Test': {'warning': 2, 'critical': 3},
    'In SIT Test': {'warning': 2, 'critical': 3},
    'In UAT Test': {'warning': 2, 'critical': 3},
    'Awaiting Prod Deployment': {'warning': 10, 'critical': 20},
    'Done': {'warning': 1000, 'critical': 1000}
}

COLORS = {
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'background': '#f8f9fa',
    'card': '#ffffff',
    'border': '#dee2e6'
}

CARD_STYLE = {
    'padding': '20px',
    'margin': '10px',
    'border-radius': '8px',
    'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
    'background-color': COLORS['card']
}

all_stage_columns = [
    "Stage Backlog days",
    "Stage Rejected days",
    "Stage Open days",
    "Stage Blocked days",
    "Stage Waiting for support days",
    "Stage Failed Test days",
    "Stage In Analysis days",
    "Stage Ready for Development days",
    "Stage In Development days",
    "Stage In Progress days",
    "Stage In Code Review days",
    "Stage In PR days",
    "Stage Ready for PR Test days",
    "Stage In PR Test days",
    "Stage Awaiting SIT Deployment days",
    "Stage In Sit days",
    "Stage In QA days",
    "Stage Ready for SIT Test days",
    "Stage In SIT Test days",
    "Stage In Test days",
    "Stage Ready for Staging days",
    "Stage Awaiting UAT Deployment days",
    "Stage Deployed to UAT days",
    "Stage In Staging days",
    "Stage Ready for UAT Test days",
    "Stage In UAT Test days",
    "Stage In UAT days",
    "Stage Design Review days",
    "Stage PO Review days",
    "Stage Ready for Release days",
    "Stage Pre-Production days",
    "Stage Awaiting Prod Deployment days",
    "Stage In Production days",
    "Stage In Prod Test days",
    "Stage Done days",
    "Stage Closed days"
]

threshold_stage_columns = [
    "Stage Waiting for support days",
    "Stage In Development days",
    "Stage In Progress days",
    "Stage Blocked days",
    "Stage In Code Review days",
    "Stage Ready for PR Test days",
    "Stage In PR Test days",
    #"Stage Awaiting Deployment days",
    "Stage Awaiting SIT Deployment days",
    "Stage In Sit days",
    "Stage Ready for SIT Test days",
    "Stage In SIT Test days",
    "Stage In Test days",
    "Stage In QA days",
    "Stage Awaiting UAT Deployment days",
    "Stage In Staging days",
    "Stage Deployed to UAT days",
    "Stage Ready for UAT Test days",
    "Stage In UAT Test days",
    "Stage In UAT days",
    "Stage Pre-Production days",
    "Stage PO Review days",
    "Stage Awaiting Prod Deployment days",
    "Stage Ready for Release days",
    "Stage In Prod Test days"
]

# Define priority order mapping
priority_order = {
    'Highest': 0,
    'P1': 1,
    'High': 2,
    'P2': 3,
    'Medium': 4,
    'P3': 5,
    'Low': 6,
    'P4': 7,
    'N/A': 8  # For items without priority
}

#------------------------------------------------------------------------------
# Data Loading and Preprocessing
#------------------------------------------------------------------------------

csv_filepath = "output-static.csv"
jira_tickets = pd.read_csv(csv_filepath, delimiter=",")

# Find all columns containing 'days' (case insensitive)
days_columns = [col for col in jira_tickets.columns if 'days' in col.lower()]

# Extract unique sprint names
unique_sprints = set()
for sprint_str in jira_tickets['Sprint'].dropna():
    if sprint_str.startswith('['):
        sprints = sprint_str.strip('[]').replace('"', '').split('-')
    else:
        sprints = [sprint_str]
    unique_sprints.update(sprint.strip() for sprint in sprints)
unique_sprints = sorted(list(unique_sprints))

# Extract other unique values
unique_projects = sorted(jira_tickets['Project'].unique())
unique_squads = sorted([squad for squad in jira_tickets['Squad'].unique() if pd.notna(squad)]) if 'Squad' in jira_tickets.columns else []
unique_types = []  # Will be populated by callback

#------------------------------------------------------------------------------
# Initialize Dash App
#------------------------------------------------------------------------------

app = Dash(__name__)

#------------------------------------------------------------------------------
# Layout Components
#------------------------------------------------------------------------------

# Header Section
header = html.Div([
    html.H1("Jira Tickets Analysis Dashboard",
            style={'color': COLORS['primary'], 'text-align': 'center', 'padding': '20px 0'}),
    html.P("This dashboard provides insights into ticket progression across different stages and sprints.",
           style={'text-align': 'center', 'color': COLORS['secondary'], 'margin-bottom': '20px'})
])

# Filters Section
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

# Sprint Goals and Metrics Section
sprint_metrics = html.Div([
    html.Div(id='sprint-goals', style={'margin-bottom': '20px'}),
    html.Div([
        html.Div(id='total-points', style={'font-size': '1.2em', 'margin-bottom': '10px'}),
        html.Div(id='ticket-count', style={'font-size': '1.2em'})
    ], style={'color': COLORS['secondary']})
], style=CARD_STYLE)

# Main Layout
app.layout = html.Div([
    header,
    # Main content container with two columns
    html.Div([
        # Left column - Filters
        html.Div([
            filters,
            sprint_metrics,
        ], style={'width': '20%', 'padding': '10px'}),

        # Right column - Charts and Tables
        html.Div([
            # Bar Chart and Stage Tickets Section
            html.Div([
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
                                {'name': 'Key', 'id': 'ID'},
                                {'name': 'Summary', 'id': 'Name'},
                                {'name': 'Type', 'id': 'Type'},
                                {'name': 'Priority', 'id': 'Priority'},
                                {'name': 'Current Stage', 'id': 'Stage'},
                                {'name': 'Days in Stage', 'id': 'days_in_stage'},
                                {'name': 'Story Points', 'id': 'StoryPoints'},
                                {'name': 'Sprint', 'id': 'Sprint'}
                            ],
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
            ], style=CARD_STYLE),

            # Combined Details Panel
            html.Div([
                # Left side - Warning Tickets
                html.Div([
                    html.H2("Tickets Exceeding Stage Thresholds",
                            style={'color': COLORS['primary'], 'margin-bottom': '20px'}),
                    dash_table.DataTable(
                        id='warning-tickets-table',
                        columns=[
                            {'name': 'Key', 'id': 'ID'},
                            {'name': 'Summary', 'id': 'Name'},
                            {'name': 'Type', 'id': 'Type'},
                            {'name': 'Priority', 'id': 'Priority'},
                            {'name': 'Current Stage', 'id': 'Stage'},
                            {'name': 'Stages Exceeding Threshold', 'id': 'exceeding_stages'},
                            {'name': 'Story Points', 'id': 'StoryPoints'},
                            {'name': 'Assignee', 'id': 'AssigneeName'},
                            {'name': 'Sprint', 'id': 'Sprint'},
                        ],
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
                        },
                        row_selectable='single',
                        selected_rows=[],
                    )
                ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Right side - Stage Duration Details (moved from left)
                html.Div([
                    html.H2("Stage Duration Details",
                            id='ticket-details-title',
                            style={'color': COLORS['primary'], 'margin-bottom': '20px', 'display': 'none'}),
                    dash_table.DataTable(
                        id='ticket-details-table',
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
                ], id='ticket-details-container', style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style=dict(CARD_STYLE, **{'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px'})),

            # Defects Table - Moved above Sprint Tickets Table
            html.Div([
                html.H2("Defects Created During Sprint",
                        style={'color': COLORS['primary'], 'margin-bottom': '20px'}),
                dash_table.DataTable(
                    id='defects-table',
                    columns=[
                        {'name': 'Key', 'id': 'ID'},
                        {'name': 'Summary', 'id': 'Name'},
                        {'name': 'Priority', 'id': 'Priority'},
                        {'name': 'Stage', 'id': 'Stage'},
                        {'name': 'Story Points', 'id': 'StoryPoints', 'type': 'numeric'},
                        {'name': 'Parent Type', 'id': 'ParentType'},
                        {'name': 'Parent Name', 'id': 'ParentName'}
                    ],
                    sort_action='native',  # Enable native sorting
                    sort_mode='multi',     # Allow sorting by multiple columns
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
            ], style=CARD_STYLE),

            # Sprint Tickets Table
            html.Div([
                html.H2("Sprint Tickets",
                        style={'color': COLORS['primary'], 'margin-bottom': '20px'}),
                dash_table.DataTable(
                    id='sprint-table',
                    columns=[
                        {'name': 'Key', 'id': 'ID'},
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
                    sort_action='native',  # Enable native sorting
                    sort_mode='multi',     # Allow sorting by multiple columns
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
            ], style=CARD_STYLE),
        ], style={'width': '75%', 'padding': '10px'}),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'})

#------------------------------------------------------------------------------
# Callbacks
#------------------------------------------------------------------------------

@callback(
    [Output('total-points', 'children'),
     Output('ticket-count', 'children'),
     Output('sprint-table', 'data')],
    [Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('ticket-dropdown', 'value'),
     Input('squad-dropdown', 'value')]
)
def update_sprint_data(selected_sprint, selected_types, selected_ticket, selected_squad):
    if not selected_sprint:
        return "No sprint selected", "No tickets", []

    # Filter data for selected sprint
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

    # Apply squad filter if selected
    if selected_squad and 'Squad' in sprint_data.columns:
        sprint_data = sprint_data[sprint_data['Squad'] == selected_squad]

    # Apply type filter if selected
    if selected_types and len(selected_types) > 0:
        sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]

    # Apply ticket filter if selected
    if selected_ticket:
        sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

    # Calculate total story points and ticket count
    total_points = sprint_data['StoryPoints'].sum()
    ticket_count = len(sprint_data)

    # Define type order for sorting
    type_order = {
        'Epic': 0,
        'Story': 1,
        'User Story': 1,
        'Task': 2,
        'Sub-task': 2,
        'Bug': 3,
        'Defect': 3,
    }

    # Create a copy and add the type order column
    sprint_data = sprint_data.copy()
    sprint_data['type_sort'] = sprint_data['Type'].map(lambda x: type_order.get(x, 999))

    # Sort the data using the temporary column
    sprint_data = sprint_data.sort_values(['type_sort', 'ID'])

    # Convert to records and remove the temporary sorting column
    sprint_records = sprint_data.drop(columns=['type_sort']).to_dict('records')

    return (
        f"Total Story Points: {total_points:.0f}",
        f"Total Tickets: {ticket_count}",
        sprint_records
    )

@callback(
    [Output('stage-tickets-table', 'data'),
     Output('selected-stage-title', 'children'),
     Output('selected-stage-title', 'style'),
     Output('stage-tickets-table', 'style_data_conditional')],
    [Input('stages-bar-chart', 'clickData'),
     Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('ticket-dropdown', 'value'),
     Input('squad-dropdown', 'value')]
)
def update_stage_tickets(click_data, selected_sprint, selected_types, selected_ticket, selected_squad):
    if not click_data or not selected_sprint:
        return [], "No stage selected", {'display': 'none'}, []

    clicked_stage = click_data['points'][0]['x']
    stage_column = f"Stage {clicked_stage} days"
    thresholds = STAGE_THRESHOLDS.get(clicked_stage, STAGE_THRESHOLDS['default'])

    # Filter data
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]
    if selected_squad and 'Squad' in sprint_data.columns:
        sprint_data = sprint_data[sprint_data['Squad'] == selected_squad]
    if selected_types and len(selected_types) > 0:
        sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]
    if selected_ticket:
        sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

    # Get tickets that spent time in this stage
    stage_tickets = sprint_data[sprint_data[stage_column] > 0].copy()
    stage_tickets['days_in_stage'] = stage_tickets[stage_column]

    # Add priority order column for sorting
    if 'Priority' in stage_tickets.columns:
        stage_tickets['priority_sort'] = stage_tickets['Priority'].map(lambda x: priority_order.get(x, 8))
    else:
        stage_tickets['priority_sort'] = 8

    # Define columns to select
    available_columns = ['ID', 'Name', 'Type', 'Priority', 'Stage', 'days_in_stage', 'StoryPoints', 'Sprint']

    # Sort by priority first, then days in stage
    stage_tickets = stage_tickets.sort_values(
        by=['priority_sort', 'days_in_stage'],
        ascending=[True, False]
    )

    # Convert to records and drop the sorting column
    table_data = stage_tickets[available_columns].to_dict('records')

    # Define conditional styling
    style_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        },
        {
            'if': {
                'filter_query': f'{{days_in_stage}} >= {thresholds["critical"]}',
                'column_id': 'days_in_stage'
            },
            'backgroundColor': '#ffcdd2',
            'color': '#c62828'
        },
        {
            'if': {
                'filter_query': f'{{days_in_stage}} >= {thresholds["warning"]} && {{days_in_stage}} < {thresholds["critical"]}',
                'column_id': 'days_in_stage'
            },
            'backgroundColor': '#fff9c4',
            'color': '#f9a825'
        },
        {
            'if': {
                'filter_query': f'{{days_in_stage}} < {thresholds["warning"]}',
                'column_id': 'days_in_stage'
            },
            'backgroundColor': '#c8e6c9',
            'color': '#2e7d32'
        }
    ]

    return (
        table_data,
        f"Tickets in {clicked_stage} Stage",
        {'display': 'block', 'marginTop': '20px'},
        style_conditional
    )

@callback(
    Output('stages-bar-chart', 'figure'),
    [Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('ticket-dropdown', 'value'),
     Input('squad-dropdown', 'value')]
)
def update_bar_chart(selected_sprint, selected_types, selected_ticket, selected_squad):
    if not selected_sprint:
        return {}

    # Filter data
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]
    if selected_squad and 'Squad' in sprint_data.columns:
        sprint_data = sprint_data[sprint_data['Squad'] == selected_squad]
    if selected_types and len(selected_types) > 0:
        sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]
    if selected_ticket:
        sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

    # Calculate stage sums and filter out zero values
    stage_sums = sprint_data[threshold_stage_columns].sum()
    non_zero_stages = stage_sums[stage_sums > 0]

    # Create DataFrame for the chart
    chart_data = pd.DataFrame({
        'Stage': non_zero_stages.index.str.replace('Stage ', '').str.replace(' days', ''),
        'Days': non_zero_stages.values
    })

    # Create bar chart with non-zero stages only
    fig = px.bar(
        chart_data,
        x='Stage',
        y='Days',
        labels={'Stage': 'Stage', 'Days': 'Total Days'},
        title=f'Time Spent in Each Stage - {selected_sprint}'
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        margin=dict(b=150),
        clickmode='event'
    )

    return fig

@callback(
    [Output('sprint-dropdown', 'options'),
     Output('sprint-dropdown', 'value'),
     Output('type-dropdown', 'options', allow_duplicate=True),
     Output('type-dropdown', 'value', allow_duplicate=True),
     Output('ticket-dropdown', 'options', allow_duplicate=True),
     Output('ticket-dropdown', 'value', allow_duplicate=True)],
    [Input('project-dropdown', 'value'),
     Input('squad-dropdown', 'value')],
    prevent_initial_call=True
)
def update_sprint_options(selected_project, selected_squad):
    if not selected_project:
        return [], None, [], [], [], None

    # Filter data
    filtered_data = jira_tickets[jira_tickets['Project'] == selected_project]
    if selected_squad and 'Squad' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Squad'] == selected_squad]

    # Get unique sprints
    sprint_set = set()
    for sprint_str in filtered_data['Sprint'].dropna():
        if sprint_str.startswith('['):
            sprints = sprint_str.strip('[]').replace('"', '').split('-')
        else:
            sprints = [sprint_str]
        sprint_set.update(sprint.strip() for sprint in sprints)

    sprint_options = [{'label': sprint, 'value': sprint} for sprint in sorted(list(sprint_set))]

    return sprint_options, None, [], [], [], None

@callback(
    [Output('type-dropdown', 'options', allow_duplicate=True),
     Output('type-dropdown', 'value', allow_duplicate=True),
     Output('ticket-dropdown', 'options', allow_duplicate=True),
     Output('ticket-dropdown', 'value', allow_duplicate=True)],
    [Input('project-dropdown', 'value'),
     Input('squad-dropdown', 'value'),
     Input('sprint-dropdown', 'value')],
    prevent_initial_call=True
)
def update_type_options(selected_project, selected_squad, selected_sprint):
    if not selected_project or not selected_sprint:
        return [], [], [], None

    # Filter data
    filtered_data = jira_tickets[jira_tickets['Project'] == selected_project]
    if selected_squad and 'Squad' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Squad'] == selected_squad]
    filtered_data = filtered_data[filtered_data['Sprint'].str.contains(selected_sprint, na=False)]

    # Get unique types
    types = sorted(filtered_data['Type'].unique())
    type_options = [{'label': type_name, 'value': type_name} for type_name in types if pd.notna(type_name)]

    # Get unique tickets
    ticket_options = [
        {'label': f"{row['ID']} - {row['Name']}", 'value': row['ID']}
        for _, row in filtered_data.iterrows()
    ]

    return type_options, [], ticket_options, None

@callback(
    Output('sprint-goals', 'children'),
    [Input('sprint-dropdown', 'value')]
)
def update_sprint_goals(selected_sprint):
    if not selected_sprint:
        return "No sprint selected"

    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

    if 'SprintGoals' in sprint_data.columns:
        goals = sprint_data['SprintGoals'].dropna().unique()
        if len(goals) > 0:
            # Get the last goal from the list
            last_goal = goals[-1]
            if isinstance(last_goal, str):
                if last_goal.startswith('['):
                    # Extract the last goal from the list format
                    goal_items = [item.strip() for item in last_goal.strip('[]').split('"')
                                if item and item not in ['-', ' ', '']]
                    if goal_items:
                        last_goal_item = goal_items[-1]
                        return html.Div([
                            html.H4("Sprint Goal:"),
                            html.P(last_goal_item)
                        ])
                else:
                    return html.Div([
                        html.H4("Sprint Goal:"),
                        html.P(last_goal)
                    ])

    return "No sprint goals available"

@callback(
    Output('warning-tickets-table', 'data'),
    [Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('ticket-dropdown', 'value'),
     Input('squad-dropdown', 'value')]
)
def update_warning_tickets(selected_sprint, selected_types, selected_ticket, selected_squad):
    if not selected_sprint:
        return []

    # Filter data
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]
    if selected_squad and 'Squad' in sprint_data.columns:
        sprint_data = sprint_data[sprint_data['Squad'] == selected_squad]
    if selected_types and len(selected_types) > 0:
        sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]
    if selected_ticket:
        sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

    warning_tickets = []
    for _, ticket in sprint_data.iterrows():
        # Track all stages exceeding thresholds
        exceeding_stages = []
        max_threshold_ratio = 0

        for stage_col in threshold_stage_columns:
            stage_name = stage_col.replace('Stage ', '').replace(' days', '')
            days_in_stage = ticket[stage_col]
            thresholds = STAGE_THRESHOLDS.get(stage_name, STAGE_THRESHOLDS['default'])

            if days_in_stage >= thresholds['warning']:
                # Calculate violation ratio (how many times over the warning threshold)
                threshold_ratio = days_in_stage / thresholds['warning']
                if threshold_ratio > max_threshold_ratio:
                    max_threshold_ratio = threshold_ratio

                # Add stage to exceeding stages list with days
                exceeding_stages.append(f"{stage_name} ({days_in_stage:.1f}d)")

        # Add ticket if it had any violations
        if exceeding_stages:
            # Get priority value from the available columns
            priority = None
            if 'Priority' in ticket and pd.notna(ticket['Priority']):
                priority = str(ticket['Priority'])

            if not priority or pd.isna(priority) or priority.lower() == 'nan':
                priority = 'N/A'

            ticket_data = {
                'ID': ticket['ID'],
                'Name': ticket['Name'],
                'Type': ticket['Type'],
                'Priority': priority,
                'Stage': ticket['Stage'],
                'AssigneeName': ticket['AssigneeName'],
                'exceeding_stages': ', '.join(exceeding_stages),
                'StoryPoints': ticket['StoryPoints'],
                'Sprint': ticket['Sprint'],
                '_threshold_ratio': max_threshold_ratio,
                '_priority_order': priority_order.get(priority, 8)
            }
            warning_tickets.append(ticket_data)

    # Sort the list of dictionaries by priority first, then threshold ratio
    warning_tickets.sort(key=lambda x: (x['_priority_order'], -x['_threshold_ratio']))

    # Remove sorting keys before returning
    for ticket in warning_tickets:
        del ticket['_priority_order']
        del ticket['_threshold_ratio']

    return warning_tickets

@callback(
    [Output('squad-dropdown', 'options'),
     Output('squad-dropdown', 'value')],
    [Input('project-dropdown', 'value')]
)
def update_squad_options(selected_project):
    if not selected_project:
        return [], None

    project_data = jira_tickets[jira_tickets['Project'] == selected_project]
    if 'Squad' in project_data.columns:
        squad_options = [
            {'label': squad, 'value': squad}
            for squad in sorted(project_data['Squad'].unique())
            if pd.notna(squad)
        ]
    else:
        squad_options = []

    return squad_options, None

@callback(
    [Output('ticket-details-container', 'style'),
     Output('ticket-details-title', 'style'),
     Output('ticket-details-table', 'data'),
     Output('ticket-details-title', 'children'),
     Output('ticket-details-table', 'style_data_conditional')],
    [Input('warning-tickets-table', 'selected_rows'),
     Input('warning-tickets-table', 'data')]
)
def update_ticket_details(warning_selected_rows, warning_table_data):
    if not warning_selected_rows or not warning_table_data or len(warning_selected_rows) == 0:
        return dict(CARD_STYLE, **{'display': 'none'}), {'display': 'none'}, [], "", []

    try:
        selected_ticket = warning_table_data[warning_selected_rows[0]]['ID']
    except (IndexError, KeyError):
        return dict(CARD_STYLE, **{'display': 'none'}), {'display': 'none'}, [], "", []

    # Filter data for selected ticket
    ticket_data = jira_tickets[jira_tickets['ID'] == selected_ticket]
    if ticket_data.empty:
        return dict(CARD_STYLE, **{'display': 'none'}), {'display': 'none'}, [], "", []

    ticket_data = ticket_data.iloc[0]

    # Create a dictionary to map stages to their order in all_stage_columns
    stage_order = {stage.replace('Stage ', '').replace(' days', ''): idx
                  for idx, stage in enumerate(all_stage_columns)}

    # Prepare stage duration data using all_stage_columns
    stage_data = []
    total_days = 0
    for col in all_stage_columns:
        stage_name = col.replace('Stage ', '').replace(' days', '')
        # Skip the Open and Done stages
        if stage_name in ['Open', 'Done']:
            continue
        days = ticket_data[col]
        if days > 0:  # Only include stages where time was spent
            total_days += days
            stage_data.append({
                'stage': stage_name,
                'days': round(days, 1)
            })

    # Add total row
    stage_data.append({
        'stage': 'TOTAL',
        'days': round(total_days, 1)
    })

    # Sort stage_data by the original order in all_stage_columns (excluding total row)
    stage_data[:-1] = sorted(stage_data[:-1], key=lambda x: stage_order[x['stage']])

    # Prepare conditional styling based on thresholds
    style_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        },
        {
            'if': {'filter_query': '{stage} = "TOTAL"'},
            'backgroundColor': '#e3f2fd',
            'fontWeight': 'bold'
        }
    ]

    # Add threshold-based styling for each stage
    for stage_entry in stage_data[:-1]:  # Exclude total row from threshold styling
        stage = stage_entry['stage']
        days = stage_entry['days']
        thresholds = STAGE_THRESHOLDS.get(stage, STAGE_THRESHOLDS['default'])

        if days >= thresholds['critical']:
            style_conditional.append({
                'if': {
                    'filter_query': f'{{stage}} = "{stage}" && {{days}} >= {thresholds["critical"]}'
                },
                'backgroundColor': '#ffcdd2',
                'color': '#c62828'
            })
        elif days >= thresholds['warning']:
            style_conditional.append({
                'if': {
                    'filter_query': f'{{stage}} = "{stage}" && {{days}} >= {thresholds["warning"]} && {{days}} < {thresholds["critical"]}'
                },
                'backgroundColor': '#fff9c4',
                'color': '#f9a825'
            })
        else:
            style_conditional.append({
                'if': {
                    'filter_query': f'{{stage}} = "{stage}" && {{days}} < {thresholds["warning"]}'
                },
                'backgroundColor': '#c8e6c9',
                'color': '#2e7d32'
            })

    return (
        dict(CARD_STYLE, **{'display': 'block'}),
        {'color': COLORS['primary'], 'margin-bottom': '20px', 'display': 'block'},
        stage_data,
        f"Stage Duration Details for {selected_ticket}",
        style_conditional
    )

@callback(
    [Output('stage-ticket-details-container', 'style'),
     Output('stage-ticket-details-title', 'style'),
     Output('stage-ticket-details-table', 'data'),
     Output('stage-ticket-details-title', 'children'),
     Output('stage-ticket-details-table', 'style_data_conditional')],
    [Input('stage-tickets-table', 'selected_rows'),
     Input('stage-tickets-table', 'data')]
)
def update_stage_ticket_details(selected_rows, table_data):
    if not selected_rows or not table_data or len(selected_rows) == 0 or len(table_data) == 0:
        return (
            {'display': 'none'},
            {'display': 'none'},
            [],
            "",
            []
        )

    try:
        selected_ticket = table_data[selected_rows[0]]['ID']
    except (IndexError, KeyError):
        return (
            {'display': 'none'},
            {'display': 'none'},
            [],
            "",
            []
        )

    # Filter data for selected ticket
    ticket_data = jira_tickets[jira_tickets['ID'] == selected_ticket]
    if ticket_data.empty:
        return (
            {'display': 'none'},
            {'display': 'none'},
            [],
            "",
            []
        )

    ticket_data = ticket_data.iloc[0]

    # Create a dictionary to map stages to their order in all_stage_columns
    stage_order = {stage.replace('Stage ', '').replace(' days', ''): idx
                  for idx, stage in enumerate(all_stage_columns)}

    # Prepare stage duration data using all_stage_columns
    stage_data = []
    total_days = 0
    for col in all_stage_columns:
        stage_name = col.replace('Stage ', '').replace(' days', '')
        # Skip the Open and Done stages
        if stage_name in ['Open', 'Done']:
            continue
        days = ticket_data[col]
        if days > 0:  # Only include stages where time was spent
            total_days += days
            stage_data.append({
                'stage': stage_name,
                'days': round(days, 1)
            })

    # Add total row
    stage_data.append({
        'stage': 'TOTAL',
        'days': round(total_days, 1)
    })

    # Sort stage_data by the original order in all_stage_columns (excluding total row)
    stage_data[:-1] = sorted(stage_data[:-1], key=lambda x: stage_order[x['stage']])

    # Prepare conditional styling based on thresholds
    style_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        },
        {
            'if': {'filter_query': '{stage} = "TOTAL"'},
            'backgroundColor': '#e3f2fd',
            'fontWeight': 'bold'
        }
    ]

    # Add threshold-based styling for each stage
    for stage_entry in stage_data[:-1]:  # Exclude total row from threshold styling
        stage = stage_entry['stage']
        days = stage_entry['days']
        thresholds = STAGE_THRESHOLDS.get(stage, STAGE_THRESHOLDS['default'])

        if days >= thresholds['critical']:
            style_conditional.append({
                'if': {
                    'filter_query': f'{{stage}} = "{stage}" && {{days}} >= {thresholds["critical"]}'
                },
                'backgroundColor': '#ffcdd2',
                'color': '#c62828'
            })
        elif days >= thresholds['warning']:
            style_conditional.append({
                'if': {
                    'filter_query': f'{{stage}} = "{stage}" && {{days}} >= {thresholds["warning"]} && {{days}} < {thresholds["critical"]}'
                },
                'backgroundColor': '#fff9c4',
                'color': '#f9a825'
            })
        else:
            style_conditional.append({
                'if': {
                    'filter_query': f'{{stage}} = "{stage}" && {{days}} < {thresholds["warning"]}'
                },
                'backgroundColor': '#c8e6c9',
                'color': '#2e7d32'
            })

    return (
        {'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'},
        {'color': COLORS['primary'], 'margin-bottom': '20px', 'display': 'block'},
        stage_data,
        f"Stage Duration Details for {selected_ticket}",
        style_conditional
    )

@callback(
    Output('defects-table', 'data'),
    [Input('project-dropdown', 'value'),
     Input('squad-dropdown', 'value'),
     Input('sprint-dropdown', 'value')]
)
def update_defects_table(selected_project, selected_squad, selected_sprint):
    if not selected_project or not selected_sprint:
        return []

    # First filter by project
    filtered_data = jira_tickets[jira_tickets['Project'] == selected_project]

    # Then filter by squad if selected
    if selected_squad and 'Squad' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Squad'] == selected_squad]

    # Then filter by sprint
    sprint_data = filtered_data[filtered_data['Sprint'].str.contains(selected_sprint, na=False)]
    if sprint_data.empty:
        return []

    # Filter defects
    defects = sprint_data[sprint_data['Type'].isin(['Bug', 'Defect'])].copy()

    # Add priority order for sorting
    defects['priority_sort'] = defects['Priority'].map(lambda x: priority_order.get(x, 8))

    # Sort by priority first (using priority_order), then by created date
    defects['CreatedDate'] = pd.to_datetime(defects['CreatedDate'])
    defects = defects.sort_values(['priority_sort', 'CreatedDate'],
                                ascending=[True, False])

    # Prepare table data (exclude the sorting column)
    table_data = defects[[
        'ID', 'Name', 'Priority', 'Stage', 'StoryPoints',
        'ParentType', 'ParentName'
    ]].to_dict('records')

    return table_data

#------------------------------------------------------------------------------
# Run the application
#------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)