from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import json

csv_filepath = "output1737863374557.csv"
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

# Get unique ticket types
unique_types = sorted(jira_tickets['Type'].unique())

# Initialize the Dash app
app = Dash(__name__)

# Create the layout
app.layout = html.Div([
    html.H1("Jira Tickets Analysis"),

    # Sprint and Type Selection Dropdowns
    html.Div([
        html.H2("Sprint Analysis"),
        html.Div([
            html.Label("Sprint:"),
            dcc.Dropdown(
                id='sprint-dropdown',
                options=[{'label': sprint, 'value': sprint} for sprint in unique_sprints],
                value=unique_sprints[0] if unique_sprints else None,
                multi=False
            ),
        ]),
        html.Div([
            html.Label("Ticket Type:"),
            dcc.Dropdown(
                id='type-dropdown',
                options=[{'label': type_, 'value': type_} for type_ in unique_types],
                value=[],
                multi=True,
                placeholder="Select ticket type(s)"
            ),
        ]),
        html.Div([
            html.Label("Specific Ticket:"),
            dcc.Dropdown(
                id='ticket-dropdown',
                options=[],  # Will be populated based on sprint and type selection
                value=None,
                multi=False,
                placeholder="Select a specific ticket"
            ),
        ]),
        html.H3(id='total-points'),
        html.H3(id='ticket-count')
    ]),

    # Bar Chart and Related Tickets
    html.Div([
        html.H2("Time Spent in Each Stage"),
        dcc.Graph(id='stages-bar-chart'),
        html.H3("Tickets in Selected Stage", id='selected-stage-title', style={'display': 'none'}),
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
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'minWidth': '100px',
                'maxWidth': '300px',
                'whiteSpace': 'normal'
            },
            page_size=10,
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
        )
    ]),

    # Data Table
    html.Div([
        html.H2("Sprint Tickets"),
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
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'minWidth': '100px',
                'maxWidth': '300px',
                'whiteSpace': 'normal'
            },
            page_size=10
        )
    ])
])

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
     Output('selected-stage-title', 'style')],
    [Input('stages-bar-chart', 'clickData'),
     Input('sprint-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('ticket-dropdown', 'value')]
)
def update_stage_tickets(click_data, selected_sprint, selected_types, selected_ticket):
    if not click_data or not selected_sprint:
        return [], "No stage selected", {'display': 'none'}

    # Get the clicked stage name
    clicked_stage = click_data['points'][0]['x']
    stage_column = f"Stage {clicked_stage} days"

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

    return (
        table_data,
        f"Tickets in {clicked_stage} Stage",
        {'display': 'block', 'marginTop': '20px'}
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
        "Stage Ready for QA days",
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

# Run the app
if __name__ == '__main__':
    app.run(debug=True)