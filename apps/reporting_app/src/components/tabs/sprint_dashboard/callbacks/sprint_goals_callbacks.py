from dash import Input, Output, callback, html
from src.data.data_filters import JiraDataFilter, JiraDataFilterService
from src.config.constants import COLUMN_NAME_SPRINT, COLUMN_NAME_SPRINT_GOALS, COLUMN_NAME_STORY_POINTS, COLUMN_NAME_STAGE
from src.utils.sprint_utils import get_sprint_date_range
from src.utils.string_utils import split_string_array

def init_callbacks(app, jira_tickets):
    @callback(
        [Output('sprint-goals', 'children'),
         Output('sprint-dates', 'children'),
         Output('sprint-stats', 'children')],
        [Input('sprint-dropdown', 'value')]
    )
    def update_sprint_info(selected_sprint: str) -> tuple[str, str, str]:
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

        filter = JiraDataFilter(sprints=[selected_sprint])
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)
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
