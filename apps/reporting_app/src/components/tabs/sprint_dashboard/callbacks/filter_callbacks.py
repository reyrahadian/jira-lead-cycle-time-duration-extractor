from dash import Input, Output, callback, html
import pandas as pd
import numpy as np
from src.utils.sprint_utils import get_sprint_date_range
from src.utils.string_utils import split_string_array
from src.data.loaders import JiraDataSingleton
from src.config.constants import COLUMN_NAME_PROJECT, COLUMN_NAME_SQUAD, COLUMN_NAME_SPRINT, \
    COLUMN_NAME_STORY_POINTS, COLUMN_NAME_SPRINT_GOALS, COLUMN_NAME_STAGE, COLUMN_NAME_TYPE
from src.data.loaders import JiraDataFilter

def init_callbacks(app, jira_tickets):
    @callback(
    [Output('squad-dropdown', 'options'),
     Output('squad-dropdown', 'value')],
    [Input('project-dropdown', 'value')]
    )
    def update_squad_dropdown_options(selected_project):
        if not selected_project:
            return [], None

        filter = JiraDataFilter(project=selected_project)
        jira_data_filter_result = JiraDataSingleton().get_jira_data().filter_tickets(filter)
        squads = jira_data_filter_result.squads
        squad_options = [
            {'label': squad, 'value': squad}
            for squad in sorted(squads)
        ]
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

        filter = JiraDataFilter(project=selected_project, squad=selected_squad)
        jira_data_filter_result = JiraDataSingleton().get_jira_data().filter_tickets(filter)
        sprint_set = jira_data_filter_result.sprints
        sprint_options = [{'label': sprint, 'value': sprint} for sprint in list(sprint_set)]

        return sprint_options, None, [], [], [], None

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

        filter = JiraDataFilter(project=selected_project, squad=selected_squad, sprint=selected_sprint, ticket_types=selected_types)
        jira_data_filter_result = JiraDataSingleton().get_jira_data().filter_tickets(filter)

        # Get ticket types options
        types = jira_data_filter_result.ticket_types
        type_options = [{'label': type_name, 'value': type_name} for type_name in types if pd.notna(type_name)]

        # Get ticket options
        ticket_options = [
            {'label': f"{row['ID']} - {row['Name']}", 'value': row['ID']}
            for _, row in jira_data_filter_result.tickets.iterrows()
        ]

        # Get components options
        components = jira_data_filter_result.components
        component_options = [{'label': comp, 'value': comp} for comp in sorted(list(components))]

        return type_options, selected_types, ticket_options, None, component_options, []

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
                list = split_string_array(list, '"-"')
                return list.index(value)
            return 0
        def get_sprint_goals_from_multiple_values(index, list):
            # example value: ["Complete Apple Pay- Complete Wishlist in Bag- Complete prepartion for Non-Shoppable (Design- Tickets- Test Plan- TC Prep- Env)"-"Apple Pay defects- Non-shoppable PDPs development"]
            if is_multiple_values(list):
                list = split_string_array(list, '"-"')
                return list[index]
            return list

        if not selected_sprint:
            return "No sprint selected", "", ""

        filter = JiraDataFilter(sprint=selected_sprint)
        jira_data_filter_result = JiraDataSingleton().get_jira_data().filter_tickets(filter)
        jira_ticket = jira_data_filter_result.tickets.iloc[0]

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
        sprint_start_date, sprint_end_date = get_sprint_date_range(jira_data_filter_result.tickets, selected_sprint)
        sprint_dates = f"{sprint_start_date.strftime('%d %b %Y')} - {sprint_end_date.strftime('%d %b %Y')}"
        sprint_dates_component = html.Div([
            html.H4("Sprint Dates:"),
            html.P(sprint_dates)
        ])

       # Calculate total story points and ticket count
        total_points = int(jira_data_filter_result.tickets[COLUMN_NAME_STORY_POINTS].sum())
        ticket_count = len(jira_data_filter_result.tickets)
        # Calculate tickets in terminal states
        terminal_states = ['Closed', 'Done', 'Resolved', 'Rejected']
        completed_tickets = len(jira_data_filter_result.tickets[jira_data_filter_result.tickets[COLUMN_NAME_STAGE].isin(terminal_states)])
        total_points_completed = int(jira_data_filter_result.tickets[jira_data_filter_result.tickets[COLUMN_NAME_STAGE].isin(terminal_states)][COLUMN_NAME_STORY_POINTS].sum())
        sprint_stats_component = html.Div([
            html.H4("Sprint Planned:"),
            html.P(f"Total Points: {total_points}"),
            html.P(f"Total Tickets: {ticket_count}"),
            html.H4("Sprint Outcomes:"),
            html.P(f"Completed Points: {total_points_completed}"),
            html.P(f"Completed Tickets: {completed_tickets}"),
        ])

        return goals_component, sprint_dates_component, sprint_stats_component
