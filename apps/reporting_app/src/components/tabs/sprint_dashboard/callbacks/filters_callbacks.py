from dash import Input, Output, callback
import pandas as pd
from src.data.data_filters import JiraDataFilter, JiraDataFilterService
from src.config.constants import COLUMN_NAME_ID, COLUMN_NAME_NAME

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
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)
        squads = jira_data_filter_result.squads
        squad_options = [{'label': squad, 'value': squad} for squad in sorted(squads)]
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
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)
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
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)

        # Get ticket types options
        types = jira_data_filter_result.ticket_types
        type_options = [{'label': type_name, 'value': type_name} for type_name in types if pd.notna(type_name)]

        # Get ticket options
        ticket_options = [
            {'label': f"{row[COLUMN_NAME_ID]} - {row[COLUMN_NAME_NAME][:15]}..", 'value': row[COLUMN_NAME_ID]}
            for _, row in jira_data_filter_result.tickets.iterrows()
        ]

        # Get components options
        components = jira_data_filter_result.components
        component_options = [{'label': comp, 'value': comp} for comp in sorted(list(components))]

        return type_options, selected_types, ticket_options, None, component_options, []

