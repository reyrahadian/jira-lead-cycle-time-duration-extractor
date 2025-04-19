from dash import Input, Output, callback
import pandas as pd
import numpy as np
from src.config.constants import (
    STAGE_THRESHOLDS, PRIORITY_ORDER, THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS,
    ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS, COLUMN_NAME_STAGE
)
from src.utils.stage_utils import calculate_tickets_duration_in_sprint, to_stage_name
from src.data.loaders import JiraDataFilter, JiraDataSingleton

def init_callbacks(app, jira_tickets):
    @callback(
        Output('tickets-exceeding-threshold-table', 'data'),
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_tickets_exceeding_threshold_table(selected_sprint, selected_types, selected_ticket, selected_squad, selected_components):
        if not selected_sprint:
            return []

        filter = JiraDataFilter(sprint=selected_sprint, ticket_types=selected_types, ticketId=selected_ticket, squad=selected_squad, components=selected_components)
        jira_data_filter_result = JiraDataSingleton().get_jira_data().filter_tickets(filter)

        # Filter data
        sprint_data = jira_data_filter_result.tickets
        sprint_data = calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)
        # Exclude tickets in Done or Closed stages
        sprint_data = sprint_data[~sprint_data[COLUMN_NAME_STAGE].isin(['Done', 'Closed', 'Rejected'])]

        tickets_exceeding_threshold = []
        for _, ticket in sprint_data.iterrows():
            # Track all stages exceeding thresholds
            exceeding_stages = []
            max_threshold_ratio = 0

            for stage_col in THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS:
                stage_name = to_stage_name(stage_col)
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
                    '_priority_order': PRIORITY_ORDER.get(priority, 8)
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
            ticket['ID'] = f"[{ticket['ID']}]({ticket['Link']})"

        return tickets_exceeding_threshold

    @callback(
        [Output('tickets-exceeding-threshold-details-container', 'style'),
        Output('tickets-exceeding-threshold-details-title', 'style'),
        Output('tickets-exceeding-threshold-details-table', 'data'),
        Output('tickets-exceeding-threshold-details-title', 'children'),
        Output('tickets-exceeding-threshold-details-table', 'style_data_conditional')],
        [Input('sprint-dropdown', 'value'),
        Input('tickets-exceeding-threshold-table', 'selected_rows'),
        Input('tickets-exceeding-threshold-table', 'data')]
    )
    def update_ticket_exceeding_threshold_details_table(selected_sprint, selected_rows, table_data):
        if not selected_rows or not table_data or len(selected_rows) == 0:
            return (
                {'width': '40%', 'display': 'none', 'verticalAlign': 'top'},
                {'display': 'none'},
                [],
                "",
                []
            )

        try:
            # Extract the ID from the markdown link format
            selected_ticket_link = table_data[selected_rows[0]]['ID']
            selected_ticket = selected_ticket_link.split('[')[1].split(']')[0]
        except (IndexError, KeyError):
            return (
                {'width': '40%', 'display': 'none', 'verticalAlign': 'top'},
                {'display': 'none'},
                [],
                "",
                []
            )

        # Process data for selected ticket
        sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]
        sprint_data = calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)
        ticket_data = sprint_data[sprint_data['ID'] == selected_ticket]
        if ticket_data.empty:
            return (
                {'width': '40%', 'display': 'none', 'verticalAlign': 'top'},
                {'display': 'none'},
                [],
                "",
                []
            )

        ticket_data = ticket_data.iloc[0]

        # Create a dictionary to map stages to their order in all_stage_columns
        stage_order = {to_stage_name(stage): idx
                    for idx, stage in enumerate(ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS)}

        # Prepare stage duration data using all_stage_columns
        stage_data = []
        total_days = 0
        for col in THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS:
            stage_name = to_stage_name(col)
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
            {'marginBottom': '20px', 'display': 'block'},
            stage_data,
            f"Stage Duration Details for {selected_ticket}",
            style_conditional
        )

