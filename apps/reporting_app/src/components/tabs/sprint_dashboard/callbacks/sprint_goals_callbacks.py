from dash import Input, Output, callback, html
from datetime import datetime
from src.data.data_filters import JiraDataFilter, JiraDataFilterService
from src.utils.stage_utils import StageUtils
from src.config.constants import (
    COLUMN_NAME_SPRINT, COLUMN_NAME_SPRINT_GOALS, COLUMN_NAME_STORY_POINTS, COLUMN_NAME_STAGE, STAGE_NAME_FINAL_STAGES,
    ALL_STAGE_NAMES, STAGE_NAME_IGNORE, COLUMN_NAME_TYPE
)
from src.utils.sprint_utils import get_sprint_date_range
from src.utils.string_utils import split_string_array
from src.data.data_filters import JiraDataFilterResult

def init_callbacks(app, jira_tickets):
    def calculate_lead_time_for_changes(jira_data_filter_result: JiraDataFilterResult, sprint_name: str) -> float:
        tickets = jira_data_filter_result.tickets
        tickets = StageUtils.calculate_tickets_duration_in_sprint(tickets, sprint_name)
        tickets = tickets[tickets[COLUMN_NAME_STAGE].isin(STAGE_NAME_FINAL_STAGES)]
        valid_stage_names = [stage for stage in ALL_STAGE_NAMES if stage not in STAGE_NAME_IGNORE]
        valid_stage_names = [StageUtils.to_stage_in_sprint_duration_days_column_name(stage) for stage in valid_stage_names]

        # Filter out columns that don't exist in the DataFrame
        existing_columns = [col for col in valid_stage_names if col in tickets.columns]

        if not existing_columns:
            return 0

        # Filter tickets that have at least one valid stage with duration > 0
        valid_tickets = tickets[tickets[existing_columns].gt(0).any(axis=1)]

        if valid_tickets.empty:
            return 0

        # Sum the values of all valid stage duration columns for valid tickets
        total_duration = valid_tickets[existing_columns].sum().sum()
        average_duration = total_duration / len(valid_tickets)

        return average_duration


    def format_days_duration(duration: float) -> str:
        return f"{duration:.0f}d"

    @callback(
        [Output('sprint-goals', 'children'),
         Output('sprint-dates', 'children'),
         Output('sprint-stats', 'children')],
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('components-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('assignee-dropdown', 'value')]
    )
    def update_sprint_info(selected_sprint: str, selected_types: list[str], selected_components: list[str], selected_ticket: str, selected_assignee: str) -> tuple[str, str, str]:
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

        filter = JiraDataFilter(sprints=[selected_sprint], ticket_types=selected_types, components=selected_components, ticketIds=[selected_ticket], assignees=[selected_assignee])
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)

        if len(jira_data_filter_result.tickets) == 0:
            return "No tickets found for this sprint", "Sprint dates not available", "No sprint statistics available"

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
        non_subtask_tickets = jira_data_filter_result.tickets[jira_data_filter_result.tickets[COLUMN_NAME_TYPE] != 'Sub-task']
        total_points = int(non_subtask_tickets[COLUMN_NAME_STORY_POINTS].sum())
        ticket_count = len(jira_data_filter_result.tickets)
        # Calculate tickets in terminal states
        completed_tickets = jira_data_filter_result.tickets[jira_data_filter_result.tickets[COLUMN_NAME_STAGE].isin(STAGE_NAME_FINAL_STAGES)]
        non_subtask_completed_tickets = completed_tickets[completed_tickets[COLUMN_NAME_TYPE] != 'Sub-task']
        total_completed_tickets = len(completed_tickets)
        total_points_completed = int(non_subtask_completed_tickets[non_subtask_completed_tickets[COLUMN_NAME_STAGE].isin(STAGE_NAME_FINAL_STAGES)][COLUMN_NAME_STORY_POINTS].sum())
        lead_time_for_changes = calculate_lead_time_for_changes(jira_data_filter_result, selected_sprint)

        sprint_stats_component = html.Div([
            html.H4("Sprint Planned:"),
            html.P(f"Total Points: {total_points}"),
            html.P(f"Total Tickets: {ticket_count}"),
            html.H4("Sprint Outcomes:"),
            html.P(f"Completed Points: {total_points_completed}"),
            html.P(f"Completed Tickets: {total_completed_tickets}"),
            html.P(f"Lead Time for Changes: {format_days_duration(lead_time_for_changes)}")
        ])

        return goals_component, sprint_dates_component, sprint_stats_component
