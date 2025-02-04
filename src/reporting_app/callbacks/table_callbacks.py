from dash import Input, Output, callback
import pandas as pd
import numpy as np
from src.reporting_app.config.constants import STAGE_THRESHOLDS
from src.reporting_app.config.constants import (
    STAGE_THRESHOLDS, PRIORITY_ORDER, THRESHOLD_STAGE_COLUMNS
)
from src.reporting_app.utils.jira_utils import create_jira_link

def init_callbacks(app, jira_tickets):
    @callback(
        Output('warning-tickets-table', 'data'),
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_warning_tickets(selected_sprint, selected_types, selected_ticket, selected_squad, selected_components):
        if not selected_sprint:
            return []

        # Filter data
        sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]
        if selected_squad and 'Squad' in sprint_data.columns:
            sprint_data = sprint_data[sprint_data['Squad'] == selected_squad]
        if selected_types and len(selected_types) > 0:
            sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]
        if selected_components and len(selected_components) > 0:
            sprint_data = sprint_data[sprint_data['CalculatedComponents'].apply(
                lambda x: any(comp in str(x).split(',') for comp in selected_components) if pd.notna(x) else False
            )]
        if selected_ticket:
            sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

        warning_tickets = []
        for _, ticket in sprint_data.iterrows():
            # Track all stages exceeding thresholds
            exceeding_stages = []
            max_threshold_ratio = 0

            for stage_col in THRESHOLD_STAGE_COLUMNS:
                stage_name = stage_col.replace('Stage ', '').replace(' days', '')
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
                warning_tickets.append(ticket_data)

        # Sort the list of dictionaries by priority first, then threshold ratio
        warning_tickets.sort(key=lambda x: (x['_priority_order'], -x['_threshold_ratio']))

        # Remove sorting keys before returning
        for ticket in warning_tickets:
            del ticket['_priority_order']
            del ticket['_threshold_ratio']

        # Convert ID to markdown link in the ticket_data dictionary
        for ticket in warning_tickets:
            ticket['ID'] = f"[{ticket['ID']}]({create_jira_link(ticket['ID'])})"

        return warning_tickets

    @callback(
        Output('defects-table', 'data'),
        [Input('project-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('sprint-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_defects_table(selected_project, selected_squad, selected_sprint, selected_components):
        if not selected_project or not selected_sprint:
            return []

        # First filter by project
        filtered_data = jira_tickets[jira_tickets['Project'] == selected_project]

        # Then filter by squad if selected
        if selected_squad and 'Squad' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['Squad'] == selected_squad]

        # Then filter by components if selected
        if selected_components and len(selected_components) > 0:
            filtered_data = filtered_data[filtered_data['CalculatedComponents'].apply(
                lambda x: any(comp in str(x).split(',') for comp in selected_components) if pd.notna(x) else False
            )]

        # Then filter by sprint
        sprint_data = filtered_data[filtered_data['Sprint'].str.contains(selected_sprint, na=False)]
        if sprint_data.empty:
            return []

        # Filter defects
        defects = sprint_data[sprint_data['Type'].isin(['Bug', 'Defect'])].copy()

        # Add priority order for sorting
        defects['priority_sort'] = defects['Priority'].map(lambda x: PRIORITY_ORDER.get(x, 8))

        # Sort by priority first (using priority_order), then by created date
        # Fix the datetime parsing warning by specifying utc=True
        defects['CreatedDate'] = pd.to_datetime(defects['CreatedDate'], utc=True)
        defects = defects.sort_values(['priority_sort', 'CreatedDate'],
                                    ascending=[True, False])

        # Prepare table data with markdown links
        table_data = defects[[
            'ID', 'Name', 'Priority', 'Stage', 'StoryPoints',
            'ParentType', 'ParentName'
        ]].copy()

        # Convert ID column to markdown links
        table_data['ID'] = table_data['ID'].apply(lambda x: f'[{x}]({create_jira_link(x)})')

        return table_data.to_dict('records')

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

    def filter_by_components(data, selected_components):
        if not selected_components or len(selected_components) == 0:
            return data

        def check_components(components_str):
            if pd.isna(components_str) or components_str == 'nan':
                return False

            components = parse_components(components_str)
            return any(comp in components for comp in selected_components)

        return data[data['CalculatedComponents'].apply(check_components)]

    @callback(
        [Output('total-points', 'children'),
        Output('ticket-count', 'children'),
        Output('sprint-tickets-table', 'data')],
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_sprint_data(selected_sprint, selected_types, selected_ticket, selected_squad, selected_components):
        if not selected_sprint:
            return "No sprint selected", "No tickets", []

        # Filter data for selected sprint
        sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]

        # Apply squad filter if selected
        if selected_squad and 'Squad' in sprint_data.columns:
            sprint_data = sprint_data[sprint_data['Squad'] == selected_squad]

        # Apply type filter if selected
        if selected_types and len(selected_types) > 0:
            sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]

        # Apply components filter if selected
        if selected_components and len(selected_components) > 0:
            sprint_data = filter_by_components(sprint_data, selected_components)

        # Apply ticket filter if selected
        if selected_ticket:
            sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

        # Calculate total story points and ticket count
        total_points = sprint_data['StoryPoints'].sum()
        ticket_count = len(sprint_data)

        # Define type order for sorting
        type_order = {
            'Epic': 0,
            'Story': 1,
            'User Story': 1,
            'Task': 2,
            'Sub-task': 2,
            'Bug': 3,
            'Defect': 3,
        }

        # Create a copy and add the type order column
        sprint_data = sprint_data.copy()
        sprint_data['type_sort'] = sprint_data['Type'].map(lambda x: type_order.get(x, 999))

        # Sort the data using the temporary column
        sprint_data = sprint_data.sort_values(['type_sort', 'ID'])

        # Convert ID column to markdown links
        sprint_data['ID'] = sprint_data['ID'].apply(lambda x: f'[{x}]({create_jira_link(x)})')

        # Convert to records and remove the temporary sorting column
        sprint_records = sprint_data.drop(columns=['type_sort']).to_dict('records')

        return (
            f"Total Story Points: {total_points:.0f}",
            f"Total Tickets: {ticket_count}",
            sprint_records
        )