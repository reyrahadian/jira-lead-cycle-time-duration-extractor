from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import json

# Add these constants near the top of the file, after the imports
STAGE_THRESHOLDS = {
    'default': {'warning': 2, 'critical': 5},  # Default thresholds in days
    'In Development': {'warning': 5, 'critical': 10},
    'In Code Review': {'warning': 2, 'critical': 4},
    'In PR Test': {'warning': 2, 'critical': 4},
    'In SIT Test': {'warning': 3, 'critical': 6},
    'In UAT Test': {'warning': 3, 'critical': 6}
}

# Add these style constants after the imports
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

csv_filepath = "output1737864602005.csv"
jira_tickets = pd.read_csv(csv_filepath,delimiter=";")

# Convert string representations of lists to actual lists and extract unique sprint names
unique_sprints = set()
for sprint_str in jira_tickets['Sprint'].dropna():
    # Remove brackets and quotes, then split by "-"
    if sprint_str.startswith('['):
        # Remove brackets and split by "-"
        sprints = sprint_str.strip('[]').replace('"', '').split('-')
    else:
        sprints = [sprint_str]
    # Add each sprint to the set
    unique_sprints.update(sprint.strip() for sprint in sprints)

# Convert to sorted list and print
unique_sprints = sorted(list(unique_sprints))

# Initialize with empty list since it will be populated by callback
unique_types = []

# Initialize the Dash app
app = Dash(__name__)

# Create the layout
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1("Jira Tickets Analysis Dashboard",
                style={'color': COLORS['primary'], 'text-align': 'center', 'padding': '20px 0'}),
        html.P("This dashboard provides insights into ticket progression across different stages and sprints.",
               style={'text-align': 'center', 'color': COLORS['secondary'], 'margin-bottom': '20px'})
    ]),

    # Main content container with two columns
    html.Div([
        # Left column - Filters
        html.Div([
            # Filters section
            html.Div([
                html.H2("Filters", style={'color': COLORS['primary'], 'margin-bottom': '20px'}),
                html.Div([
                    html.Label("Sprint:", style={'font-weight': 'bold', 'color': COLORS['secondary']}),
                    dcc.Dropdown(
                        id='sprint-dropdown',
                        options=[{'label': sprint, 'value': sprint} for sprint in unique_sprints],
                        value=unique_sprints[0] if unique_sprints else None,
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
            ], style=CARD_STYLE),

            # Sprint Goals and Metrics
            html.Div([
                html.Div(id='sprint-goals', style={'margin-bottom': '20px'}),
                html.Div([
                    html.Div(id='total-points', style={'font-size': '1.2em', 'margin-bottom': '10px'}),
                    html.Div(id='ticket-count', style={'font-size': '1.2em'})
                ], style={'color': COLORS['secondary']})
            ], style=CARD_STYLE),
        ], style={'width': '25%', 'padding': '10px'}),

        # Right column - Charts and Tables
        html.Div([
            # Bar Chart
            html.Div([
                html.H2("Time Spent in Each Stage",
                        style={'color': COLORS['primary'], 'margin-bottom': '20px'}),
                dcc.Graph(id='stages-bar-chart'),
                html.H3("Tickets in Selected Stage",
                        id='selected-stage-title',
                        style={'display': 'none', 'color': COLORS['secondary']}),
                dash_table.DataTable(
                    id='stage-tickets-table',
                    columns=[
                        {'name': 'Key', 'id': 'ID'},
                        {'name': 'Summary', 'id': 'Name'},
                        {'name': 'Type', 'id': 'Type'},
                        {'name': 'Days in Stage', 'id': 'days_in_stage'},
                        {'name': 'Story Points', 'id': 'StoryPoints'},
                        {'name': 'Fix Versions', 'id': 'FixVersions'},
                        {'name': 'Sprint', 'id': 'Sprint'}
                    ],
                    style_table={'overflowX': 'auto', 'backgroundColor': COLORS['background']},
                    style_cell={
                        'textAlign': 'left',
                        'minWidth': '100px',
                        'maxWidth': '300px',
                        'whiteSpace': 'normal'
                    },
                    page_size=10,
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
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
                        {'name': 'Status', 'id': 'Stage'},
                        {'name': 'Story Points', 'id': 'StoryPoints'},
                        {'name': 'Fix Versions', 'id': 'FixVersions'},
                        {'name': 'Created', 'id': 'CreatedDate'},
                        {'name': 'Updated', 'id': 'UpdatedDate'},
                        {'name': 'Sprint', 'id': 'Sprint'}
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
                    }
                )
            ], style=CARD_STYLE),
        ], style={'width': '75%', 'padding': '10px'}),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'})

# Callbacks for updating total points, ticket count and table
@callback(
    [Output('total-points', 'children'),
     Output('ticket-count', 'children'),
     Output('sprint-table', 'data')],
    [Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('ticket-dropdown', 'value')]
)
def update_sprint_data(selected_sprint, selected_types, selected_ticket):
    if not selected_sprint:
        return "No sprint selected", "No tickets", []

    # Filter data for selected sprint
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

    # Apply type filter if selected
    if selected_types and len(selected_types) > 0:
        sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]

    # Apply ticket filter if selected
    if selected_ticket:
        sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

    # Calculate total story points and ticket count
    total_points = sprint_data['StoryPoints'].sum()
    ticket_count = len(sprint_data)

    # Prepare table data
    table_data = sprint_data.to_dict('records')

    return (
        f"Total Story Points: {total_points:.0f}",
        f"Total Tickets: {ticket_count}",
        table_data
    )

# Add new callback for handling bar chart clicks and updating the tickets table
@callback(
    [Output('stage-tickets-table', 'data'),
     Output('selected-stage-title', 'children'),
     Output('selected-stage-title', 'style'),
     Output('stage-tickets-table', 'style_data_conditional')],
    [Input('stages-bar-chart', 'clickData'),
     Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('ticket-dropdown', 'value')]
)
def update_stage_tickets(click_data, selected_sprint, selected_types, selected_ticket):
    if not click_data or not selected_sprint:
        return [], "No stage selected", {'display': 'none'}, []

    # Get the clicked stage name
    clicked_stage = click_data['points'][0]['x']
    stage_column = f"Stage {clicked_stage} days"

    # Get thresholds for this stage
    thresholds = STAGE_THRESHOLDS.get(clicked_stage, STAGE_THRESHOLDS['default'])

    # Filter data for selected sprint
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

    # Apply type filter if selected
    if selected_types and len(selected_types) > 0:
        sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]

    # Apply ticket filter if selected
    if selected_ticket:
        sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

    # Filter for tickets that spent time in this stage
    stage_tickets = sprint_data[sprint_data[stage_column] > 0].copy()

    # Add the days in stage to the output
    stage_tickets['days_in_stage'] = stage_tickets[stage_column]

    # Prepare table data
    table_data = stage_tickets[['ID', 'Name', 'Type', 'days_in_stage', 'StoryPoints', 'FixVersions', 'Sprint']].sort_values(
        by='days_in_stage',
        ascending=False
    ).to_dict('records')

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
            'backgroundColor': '#ffcdd2',  # Light red
            'color': '#c62828'  # Dark red
        },
        {
            'if': {
                'filter_query': f'{{days_in_stage}} >= {thresholds["warning"]} && {{days_in_stage}} < {thresholds["critical"]}',
                'column_id': 'days_in_stage'
            },
            'backgroundColor': '#fff9c4',  # Light yellow
            'color': '#f9a825'  # Dark yellow
        },
        {
            'if': {
                'filter_query': f'{{days_in_stage}} < {thresholds["warning"]}',
                'column_id': 'days_in_stage'
            },
            'backgroundColor': '#c8e6c9',  # Light green
            'color': '#2e7d32'  # Dark green
        }
    ]

    return (
        table_data,
        f"Tickets in {clicked_stage} Stage",
        {'display': 'block', 'marginTop': '20px'},
        style_conditional
    )

# Update the bar chart callback to make it clickable
@callback(
    Output('stages-bar-chart', 'figure'),
    [Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('ticket-dropdown', 'value')]
)
def update_bar_chart(selected_sprint, selected_types, selected_ticket):
    if not selected_sprint:
        return {}

    # Filter data for selected sprint
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

    # Apply type filter if selected
    if selected_types and len(selected_types) > 0:
        sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]

    # Apply ticket filter if selected
    if selected_ticket:
        sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

    days_columns = [
        "Stage In Development days",
        "Stage In Progress days",
        "Stage Blocked days",
        "Stage In Code Review days",
        "Stage In PR Test days",
        "Stage Ready for PR Test days",
        "Stage Awaiting SIT Deployment days",
        "Stage In Sit days",
        #"Stage Ready for QA days",
        "Stage Ready for SIT Test days",
        "Stage In SIT Test days",
        "Stage Awaiting UAT Deployment days",
        "Stage Deployed to UAT days",
        "Stage Ready for UAT Test days",
        "Stage In UAT Test days",
        "Stage In UAT days",
        "Stage PO Review days",
        "Stage Awaiting Prod Deployment days",
    ]

    # Calculate sum of days for each stage
    stage_sums = sprint_data[days_columns].sum()

    # Create bar chart using plotly express
    fig = px.bar(
        x=stage_sums.index.str.replace('Stage ', '').str.replace(' days', ''),
        y=stage_sums.values,
        labels={'x': 'Stage', 'y': 'Total Days'},
        title=f'Time Spent in Each Stage - {selected_sprint}'
    )

    # Rotate x-axis labels for better readability
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        margin=dict(b=150),  # Add bottom margin for rotated labels
        clickmode='event'    # Enable clicking on bars
    )

    return fig

# Add callback to update ticket dropdown options
@callback(
    Output('ticket-dropdown', 'options'),
    [Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value')]
)
def update_ticket_options(selected_sprint, selected_types):
    if not selected_sprint:
        return []

    # Filter data for selected sprint
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

    # Apply type filter if selected
    if selected_types and len(selected_types) > 0:
        sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]

    # Create options with ticket ID and summary
    options = [
        {'label': f"{row['ID']} - {row['Name']}", 'value': row['ID']}
        for _, row in sprint_data.iterrows()
    ]

    return sorted(options, key=lambda x: x['value'])

# Add new callback for sprint goals
@callback(
    Output('sprint-goals', 'children'),
    [Input('sprint-dropdown', 'value')]
)
def update_sprint_goals(selected_sprint):
    if not selected_sprint:
        return "No sprint selected"

    # Filter data for selected sprint
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

    # Get sprint goals if they exist
    if 'SprintGoals' in sprint_data.columns:
        # Get unique non-null sprint goals
        goals = sprint_data['SprintGoals'].dropna().unique()
        if len(goals) > 0:
            # Split goals if they're in a single string
            all_goals = []
            for goal in goals:
                if isinstance(goal, str):
                    # Remove outer brackets and split by quotes
                    if goal.startswith('['):
                        # Split by quotes and take odd-indexed items (the actual goals)
                        goal_items = [item for item in goal.strip('[]').split('"') if item and item not in ['-', ' ', '']]
                    else:
                        goal_items = [goal]
                    # Add each non-empty goal to the list
                    all_goals.extend([g.strip() for g in goal_items if g.strip()])

            # Remove duplicates
            unique_goals = list(set(all_goals))

            if unique_goals:
                return html.Div([
                    html.H4("Sprint Goals:"),
                    html.Ul([html.Li(goal) for goal in unique_goals])
                ])

    return "No sprint goals available"

# Add callback to update type dropdown options based on selected sprint
@callback(
    [Output('type-dropdown', 'options'),
     Output('type-dropdown', 'value')],
    [Input('sprint-dropdown', 'value')]
)
def update_type_options(selected_sprint):
    if not selected_sprint:
        return [], []

    # Filter data for selected sprint
    sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

    # Get unique types for the selected sprint
    sprint_types = sorted(sprint_data['Type'].unique())

    # Create options list
    options = [{'label': type_, 'value': type_} for type_ in sprint_types]

    return options, []  # Reset selection when sprint changes

# Run the app
if __name__ == '__main__':
    app.run(debug=True)