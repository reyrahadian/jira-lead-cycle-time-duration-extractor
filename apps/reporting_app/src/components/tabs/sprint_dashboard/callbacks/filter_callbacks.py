from dash import Input, Output, callback, html
import pandas as pd
import numpy as np
from src.utils.sprint_utils import get_sprint_date_range
from src.utils.string_utils import split_string_array
from src.config.constants import COLUMN_NAME_PROJECT, COLUMN_NAME_SQUAD, COLUMN_NAME_SPRINT, \
    COLUMN_NAME_STORY_POINTS, COLUMN_NAME_SPRINT_GOALS, COLUMN_NAME_STAGE, COLUMN_NAME_TYPE

def init_callbacks(app, jira_tickets):
    @callback(
    [Output('squad-dropdown', 'options'),
     Output('squad-dropdown', 'value')],
    [Input('project-dropdown', 'value')]
    )
    def update_squad_dropdown_options(selected_project):
        if not selected_project:
            return [], None

        project_data = jira_tickets[jira_tickets[COLUMN_NAME_PROJECT] == selected_project]
        if COLUMN_NAME_SQUAD in project_data.columns:
            # Filter out NaN values and convert to list before sorting
            squads = [squad for squad in project_data[COLUMN_NAME_SQUAD].unique() if pd.notna(squad)]
            squad_options = [
                {'label': squad, 'value': squad}
                for squad in sorted(squads)
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
        filtered_data = jira_tickets[jira_tickets[COLUMN_NAME_PROJECT] == selected_project]
        if selected_squad and COLUMN_NAME_SQUAD in filtered_data.columns:
            filtered_data = filtered_data[filtered_data[COLUMN_NAME_SQUAD] == selected_squad]

        # Get unique sprints
        sprint_set = set()
        for sprint_str in filtered_data[COLUMN_NAME_SPRINT].dropna().unique():
            sprints = split_string_array(sprint_str)
            sprint_set.update(sprint.strip() for sprint in sprints)

        # Get sprint end dates and sort sprints by end date descending
        sprint_dates = {}
        for sprint in sprint_set:
            # Get one ticket from this sprint to get its dates
            sprint_ticket = filtered_data[filtered_data[COLUMN_NAME_SPRINT].str.contains(sprint, na=False)].iloc[0]
            # Convert the Series to a DataFrame with a single row
            sprint_ticket_df = sprint_ticket.to_frame().T
            start_date, _ = get_sprint_date_range(sprint_ticket_df, sprint)
            if start_date and not pd.isna(start_date):
                # Ensure timezone-naive comparison by converting to UTC and removing timezone
                sprint_dates[sprint] = start_date.tz_localize(None) if start_date.tz else start_date
            else:
                # Use timezone-naive minimum timestamp
                sprint_dates[sprint] = pd.Timestamp.min.tz_localize(None)

        # Sort sprints by start date descending
        sprint_set = sorted(sprint_dates.keys(), key=lambda x: sprint_dates[x], reverse=True)
        sprint_options = [{'label': sprint, 'value': sprint} for sprint in list(sprint_set)]

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
        filtered_data = jira_tickets[jira_tickets[COLUMN_NAME_PROJECT] == selected_project]

        # Apply squad filter if selected
        if selected_squad and COLUMN_NAME_SQUAD in filtered_data.columns:
            filtered_data = filtered_data[filtered_data[COLUMN_NAME_SQUAD] == selected_squad]

        # Apply sprint filter
        filtered_data = filtered_data[filtered_data[COLUMN_NAME_SPRINT].str.contains(selected_sprint, na=False)]

        # Apply type filter for components only
        components_data = filtered_data.copy()
        if selected_types and len(selected_types) > 0:
            components_data = filtered_data[filtered_data[COLUMN_NAME_TYPE].isin(selected_types)]

        # Get unique types
        types = sorted(filtered_data[COLUMN_NAME_TYPE].unique())
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
        def is_multiple_values(value):
            if isinstance(value, str) and '[' in value:
                return True
            return False
        def get_sprint_value_index(value, list):
            # example value: ["LFW 1.1.25"-"LFW 2.1.25"]
            if is_multiple_values(list):
                list = split_string_array(list)
                return list.index(value)
            return 0
        def get_sprint_goals_from_multiple_values(index, list):
            # example value: ["Complete Apple Pay- Complete Wishlist in Bag- Complete prepartion for Non-Shoppable (Design- Tickets- Test Plan- TC Prep- Env)"-"Apple Pay defects- Non-shoppable PDPs development"]
            if is_multiple_values(list):
                list = split_string_array(list)
                return list[index]
            return list

        if not selected_sprint:
            return "No sprint selected", "", ""

        sprint_data = jira_tickets[jira_tickets[COLUMN_NAME_SPRINT].str.contains(selected_sprint, na=False)]
        jira_ticket = sprint_data.iloc[0]

        if is_multiple_values(jira_ticket[COLUMN_NAME_SPRINT]):
            sprint_index = get_sprint_value_index(selected_sprint, jira_ticket[COLUMN_NAME_SPRINT])
            sprint_goals = get_sprint_goals_from_multiple_values(sprint_index, jira_ticket[COLUMN_NAME_SPRINT_GOALS])
        else:
            sprint_goals = jira_ticket[COLUMN_NAME_SPRINT_GOALS]

        goals_component = html.Div([
            html.H4("Sprint Goal:"),
            html.P(sprint_goals)
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
        total_points = int(sprint_data[COLUMN_NAME_STORY_POINTS].sum())
        ticket_count = len(sprint_data)
        # Calculate tickets in terminal states
        terminal_states = ['Closed', 'Done', 'Resolved', 'Rejected']
        completed_tickets = len(sprint_data[sprint_data[COLUMN_NAME_STAGE].isin(terminal_states)])
        total_points_completed = int(sprint_data[sprint_data[COLUMN_NAME_STAGE].isin(terminal_states)][COLUMN_NAME_STORY_POINTS].sum())
        sprint_stats_component = html.Div([
            html.H4("Sprint Planned:"),
            html.P(f"Total Points: {total_points}"),
            html.P(f"Total Tickets: {ticket_count}"),
            html.H4("Sprint Outcomes:"),
            html.P(f"Completed Points: {total_points_completed}"),
            html.P(f"Completed Tickets: {completed_tickets}"),
        ])

        return goals_component, sprint_dates_component, sprint_stats_component
