from dash import Input, Output, callback, html
import pandas as pd
from src.reporting_app.utils.sprint_utils import get_sprint_date_range

def init_callbacks(app, jira_tickets):
    @callback(
    [Output('squad-dropdown', 'options'),
     Output('squad-dropdown', 'value')],
    [Input('project-dropdown', 'value')]
    )
    def update_squad_dropdown_options(selected_project):
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
    def update_sprint_dropdown_options(selected_project, selected_squad):
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

    def parse_components(components_str):
        if pd.isna(components_str):
            return set()

        components = set()
        if isinstance(components_str, str):
            # Remove brackets and extra whitespace
            cleaned_str = components_str.replace('[', '').replace(']', '').strip()

            # First split by comma if present
            for part in cleaned_str.split(','):
                # Then split by hyphen if present
                subparts = part.split('-')
                components.update(comp.strip('"').strip("'").strip() for comp in subparts if comp.strip())
        elif isinstance(components_str, (list, np.ndarray)):
            for comp in components_str:
                if pd.notna(comp):
                    # Handle potential hyphenated values in array elements
                    subparts = str(comp).split('-')
                    components.update(part.strip('"').strip("'").strip() for part in subparts if part.strip())

        return components

    @callback(
        [Output('type-dropdown', 'options', allow_duplicate=True),
        Output('type-dropdown', 'value', allow_duplicate=True),
        Output('ticket-dropdown', 'options', allow_duplicate=True),
        Output('ticket-dropdown', 'value', allow_duplicate=True),
        Output('components-dropdown', 'options'),
        Output('components-dropdown', 'value')],
        [Input('project-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_type_and_components_dropdown_options(selected_project, selected_squad, selected_sprint, selected_types):
        if not selected_project or not selected_sprint:
            return [], [], [], None, [], []

        # Filter data
        filtered_data = jira_tickets[jira_tickets['Project'] == selected_project]

        # Apply squad filter if selected
        if selected_squad and 'Squad' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['Squad'] == selected_squad]

        # Apply sprint filter
        filtered_data = filtered_data[filtered_data['Sprint'].str.contains(selected_sprint, na=False)]

        # Apply type filter for components only
        components_data = filtered_data.copy()
        if selected_types and len(selected_types) > 0:
            components_data = filtered_data[filtered_data['Type'].isin(selected_types)]

        # Get unique types
        types = sorted(filtered_data['Type'].unique())
        type_options = [{'label': type_name, 'value': type_name} for type_name in types if pd.notna(type_name)]

        # Preserve selected types if they're still valid
        valid_types = [t['value'] for t in type_options]
        preserved_types = selected_types if selected_types else []
        preserved_types = [t for t in preserved_types if t in valid_types]

        # Get unique tickets
        ticket_options = [
            {'label': f"{row['ID']} - {row['Name']}", 'value': row['ID']}
            for _, row in filtered_data.iterrows()
        ]

        # Get unique components based on filtered data
        unique_components = set()
        for components_str in components_data['CalculatedComponents'].dropna():
            components = parse_components(components_str)
            unique_components.update(components)

        component_options = [{'label': comp, 'value': comp} for comp in sorted(list(unique_components))]

        return type_options, preserved_types, ticket_options, None, component_options, []

    @callback(
        [Output('sprint-goals', 'children'),
         Output('sprint-dates', 'children'),
         Output('sprint-stats', 'children')],
        [Input('sprint-dropdown', 'value')]
    )
    def update_sprint_info(selected_sprint):
        if not selected_sprint:
            return "No sprint selected", "", ""

        sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

         # Get sprint goals
        goals_component = "No sprint goals available"
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
                            goals_component = html.Div([
                                html.H4("Sprint Goal:"),
                                html.P(last_goal_item)
                            ])
                    else:
                        goals_component = html.Div([
                            html.H4("Sprint Goal:"),
                            html.P(last_goal)
                        ])

        # Get sprint dates
        sprint_dates = "Sprint dates not available"
        sprint_start_date, sprint_end_date = get_sprint_date_range(sprint_data, selected_sprint)
        sprint_dates = f"{sprint_start_date.strftime('%d %b %Y')} - {sprint_end_date.strftime('%d %b %Y')}"
        sprint_dates_component = html.Div([
            html.H4("Sprint Dates:"),
            html.P(sprint_dates)
        ])

       # Calculate total story points and ticket count
        total_points = int(sprint_data['StoryPoints'].sum())
        ticket_count = len(sprint_data)
        # Calculate tickets in terminal states
        terminal_states = ['Closed', 'Done', 'Resolved', 'Rejected']
        completed_tickets = len(sprint_data[sprint_data['Stage'].isin(terminal_states)])
        total_points_completed = int(sprint_data[sprint_data['Stage'].isin(terminal_states)]['StoryPoints'].sum())
        sprint_stats_component = html.Div([
            html.H4("Sprint Stats:"),
            html.P(f"Total Points: {total_points}"),
            html.P(f"Total Tickets: {ticket_count}"),
            html.H4("Sprint Outcomes:"),
            html.P(f"Completed Points: {total_points_completed}"),
            html.P(f"Completed Tickets: {completed_tickets}"),
        ])

        return goals_component, sprint_dates_component, sprint_stats_component
