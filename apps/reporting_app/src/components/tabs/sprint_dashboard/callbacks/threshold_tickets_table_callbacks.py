from dash import Input, Output, callback
import pandas as pd
import numpy as np
from src.config.constants import (
    STAGE_THRESHOLDS, PRIORITY_ORDER, THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS,
    ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS, COLUMN_NAME_STAGE, COLUMN_NAME_LINK, COLUMN_NAME_ID, COLUMN_NAME_NAME,
    COLUMN_NAME_TYPE, COLUMN_NAME_ASSIGNEE_NAME, COLUMN_NAME_STORY_POINTS, COLUMN_NAME_SPRINT, COLUMN_NAME_PRIORITY,
    STAGE_NAME_IN_PROGRESS_GROUPINGS
)
from src.utils.stage_utils import StageUtils
from src.data.data_filters import JiraDataFilter, JiraDataFilterService

def init_callbacks(app, jira_tickets):
    @callback(
        Output('tickets-exceeding-threshold-table', 'rowData'),
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_tickets_exceeding_threshold_table(selected_sprint: str, selected_types: list[str], selected_ticket: str, selected_squad: str, selected_components: list[str]) -> list[dict]:
        if not selected_sprint:
            return []

        filter = JiraDataFilter(sprints=[selected_sprint],
                                ticket_types=selected_types,
                                ticketIds=[selected_ticket],
                                squads=[selected_squad],
                                components=selected_components)
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)

        # Filter data
        sprint_data = jira_data_filter_result.tickets
        sprint_data = StageUtils.calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)

        tickets_exceeding_threshold = []
        for _, ticket in sprint_data.iterrows():
            # Track all stages exceeding thresholds
            exceeding_stages = []
            max_threshold_ratio = 0

            for stage_col in THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS:
                stage_name = StageUtils.to_stage_name(stage_col)
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
                if COLUMN_NAME_PRIORITY in ticket and pd.notna(ticket[COLUMN_NAME_PRIORITY]):
                    priority = str(ticket[COLUMN_NAME_PRIORITY])

                if not priority or pd.isna(priority) or priority.lower() == 'nan':
                    priority = 'N/A'

                ticket_data = {
                    COLUMN_NAME_ID: ticket[COLUMN_NAME_ID],
                    COLUMN_NAME_NAME: ticket[COLUMN_NAME_NAME],
                    COLUMN_NAME_TYPE: ticket[COLUMN_NAME_TYPE],
                    COLUMN_NAME_PRIORITY: priority,
                    COLUMN_NAME_STAGE: ticket[COLUMN_NAME_STAGE],
                    COLUMN_NAME_ASSIGNEE_NAME: ticket[COLUMN_NAME_ASSIGNEE_NAME],
                    'exceeding_stages': ', '.join(exceeding_stages),
                    COLUMN_NAME_STORY_POINTS: ticket[COLUMN_NAME_STORY_POINTS],
                    COLUMN_NAME_SPRINT: ticket[COLUMN_NAME_SPRINT],
                    '_threshold_ratio': max_threshold_ratio,
                    '_priority_order': PRIORITY_ORDER.get(priority, 8),
                    COLUMN_NAME_LINK: ticket[COLUMN_NAME_LINK]
                }
                tickets_exceeding_threshold.append(ticket_data)

        # Sort the list of dictionaries by priority first, then threshold ratio
        tickets_exceeding_threshold.sort(key=lambda x: (x['_priority_order'], -x['_threshold_ratio']))

        # Remove sorting keys before returning
        for ticket in tickets_exceeding_threshold:
            del ticket['_priority_order']
            del ticket['_threshold_ratio']

        # Convert ID to markdown link in the ticket_data dictionary
        for ticket in tickets_exceeding_threshold:
            ticket[COLUMN_NAME_ID] = f"[{ticket[COLUMN_NAME_ID]}]({ticket[COLUMN_NAME_LINK]})"

        return tickets_exceeding_threshold

    @callback(
        [Output('tickets-exceeding-threshold-details-table', 'rowData'),
        Output('tickets-exceeding-threshold-details-title', 'children')],
        [Input('sprint-dropdown', 'value'),
        Input('tickets-exceeding-threshold-table', 'selectedRows'),
        Input('tickets-exceeding-threshold-table', 'rowData')]
    )
    def update_ticket_exceeding_threshold_details_table(selected_sprint, selected_rows, table_data):
        result = (
            [],
            "Ticket's Cycle Time"
        )
        if not selected_rows or not table_data or len(selected_rows) == 0:
            return result

        try:
            # Extract the ID from the markdown link format
            selected_ticket_link = selected_rows[0][COLUMN_NAME_ID]
            selected_ticket = selected_ticket_link.split('[')[1].split(']')[0]
        except (IndexError, KeyError):
            return result

        # Process data for selected ticket
        sprint_data = jira_tickets[jira_tickets[COLUMN_NAME_SPRINT].str.contains(selected_sprint, na=False)]
        sprint_data = StageUtils.calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)
        ticket_data = sprint_data[sprint_data[COLUMN_NAME_ID] == selected_ticket]
        if ticket_data.empty:
            return result

        ticket_data = ticket_data.iloc[0]

        # Create a dictionary to map stages to their order in all_stage_columns
        stage_order = {StageUtils.to_stage_name(stage): idx
                    for idx, stage in enumerate(ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS)}

        # Prepare stage duration data using all_stage_columns
        stage_data = []
        total_days = 0
        for col in THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS:
            stage_name = StageUtils.to_stage_name(col)
            thresholds = STAGE_THRESHOLDS.get(stage_name, STAGE_THRESHOLDS['default'])
            # only include in progress stages
            if stage_name not in STAGE_NAME_IN_PROGRESS_GROUPINGS:
                continue
            days = ticket_data[col]
            if days > 0:  # Only include stages where time was spent
                total_days += days
                stage_data.append({
                    'stage': stage_name,
                    'days': round(days, 1),
                    'thresholds': thresholds
                })

        # Add total row
        stage_data.append({
            'stage': 'TOTAL',
            'days': round(total_days, 1)
        })

        # Sort stage_data by the original order in all_stage_columns (excluding total row)
        stage_data[:-1] = sorted(stage_data[:-1], key=lambda x: stage_order[x['stage']])

        return (
            stage_data,
            f"{selected_ticket} Cycle Time"
        )

