import pandas as pd
from dash import Input, Output, callback
from src.data.data_filters import JiraDataFilter, JiraDataFilterService
from src.config.constants import COLUMN_NAME_ID, COLUMN_NAME_LINK, COLUMN_NAME_TYPE, COLUMN_NAME_PARENT_TYPE, \
    COLUMN_NAME_PARENT_NAME, COLUMN_NAME_STAGE, COLUMN_NAME_STORY_POINTS, COLUMN_NAME_FIX_VERSIONS, \
    COLUMN_NAME_CREATED_DATE, COLUMN_NAME_UPDATED_DATE, COLUMN_NAME_SPRINT, COLUMN_NAME_NAME, COLUMN_NAME_PRIORITY, \
    PRIORITY_ORDER, THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS, STAGE_THRESHOLDS, COLUMN_NAME_ASSIGNEE_NAME, \
    ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS, STAGE_NAME_IN_PROGRESS_GROUPINGS
from src.utils.sprint_utils import get_sprint_date_range
from src.utils.stage_utils import StageUtils

def get_column_defs(hide_exceeding_stages: bool = True)->list[dict]:
    return [
            {"headerName": "Key", "field": "ID", "cellRenderer": "markdown", "linkTarget": "_blank", "pinned": "left"},
            {"headerName": "Summary", "field": "Name", "width": 400, "tooltipField": "Name"},
            {
                "headerName": "Stages Exceeding Threshold",
                "field": "exceeding_stages",
                "width": 200,
                "suppressColumnsToolPanel": True,
                "hide": hide_exceeding_stages,
                "suppressMenu": True
            },
            {"headerName": "Type", "field": "Type"},
            {"headerName": "Priority", "field": "Priority"},
            {"headerName": "CurrentStage", "field": "Stage"},
            {"headerName": "Story Points", "field": "StoryPoints", "filter": "agNumberColumnFilter"},
            {
                "headerName": "More Details",
                "children": [
                    {"field": "ParentName", "tooltipField": "ParentName"},
                    {"field": "ParentType", "columnGroupShow": "open"},
                    {"field": "FixVersions", "tooltipField": "FixVersions", "columnGroupShow": "open"},
                    {"field": "Sprint", "tooltipField": "Sprint", "columnGroupShow": "open"},
                    {"field": "CreatedDate", "columnGroupShow": "open"},
                    {"field": "UpdatedDate", "columnGroupShow": "open"},
                ]
            }
        ];

def init_callbacks(app, jira_tickets):
    def get_defects(jira_tickets: pd.DataFrame, selected_sprint: str) -> list[dict]:
        defects = jira_tickets[jira_tickets[COLUMN_NAME_TYPE].isin(['Bug', 'Defect'])].copy()
        sprint_start_date, sprint_end_date = get_sprint_date_range(defects, selected_sprint)
        # Filter defects created during the sprint
        if sprint_start_date is not None:
            defects = defects[defects[COLUMN_NAME_CREATED_DATE] >= sprint_start_date]
        if sprint_end_date is not None:
            defects = defects[defects[COLUMN_NAME_CREATED_DATE] <= sprint_end_date]

        # Add priority order for sorting
        defects['priority_sort'] = defects[COLUMN_NAME_PRIORITY].map(lambda x: PRIORITY_ORDER.get(x, 8))

        # Prepare table data with markdown links
        table_data = defects[[
            COLUMN_NAME_ID, COLUMN_NAME_NAME, COLUMN_NAME_PRIORITY, COLUMN_NAME_STAGE, COLUMN_NAME_STORY_POINTS,
            COLUMN_NAME_PARENT_TYPE, COLUMN_NAME_PARENT_NAME, COLUMN_NAME_LINK, COLUMN_NAME_TYPE, COLUMN_NAME_CREATED_DATE,
            COLUMN_NAME_UPDATED_DATE, COLUMN_NAME_SPRINT, COLUMN_NAME_FIX_VERSIONS
        ]].copy()

        # Convert ID column to markdown links
        table_data[COLUMN_NAME_ID] = table_data.apply(lambda x: f'[{x[COLUMN_NAME_ID]}]({x[COLUMN_NAME_LINK]})', axis=1)

        return table_data.to_dict('records')

    def get_threshold_violations(jira_tickets: pd.DataFrame, selected_sprint: str) -> list[dict]:
        sprint_data = jira_tickets
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
                    COLUMN_NAME_LINK: ticket[COLUMN_NAME_LINK],
                    COLUMN_NAME_FIX_VERSIONS: ticket[COLUMN_NAME_FIX_VERSIONS],
                    COLUMN_NAME_CREATED_DATE: ticket[COLUMN_NAME_CREATED_DATE],
                    COLUMN_NAME_UPDATED_DATE: ticket[COLUMN_NAME_UPDATED_DATE],
                    COLUMN_NAME_PARENT_TYPE: ticket[COLUMN_NAME_PARENT_TYPE],
                    COLUMN_NAME_PARENT_NAME: ticket[COLUMN_NAME_PARENT_NAME],
                    COLUMN_NAME_PRIORITY: ticket[COLUMN_NAME_PRIORITY]
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

    def get_all_tickets(jira_tickets: pd.DataFrame, selected_sprint: str) -> list[dict]:
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
        sprint_data = jira_tickets.copy()
        sprint_data['type_sort'] = sprint_data['Type'].map(lambda x: type_order.get(x, 999))

        # Sort the data using the temporary column
        sprint_data = sprint_data.sort_values(['type_sort', 'ID'])

        # Convert ID column to markdown links
        sprint_data[COLUMN_NAME_ID] = sprint_data.apply(lambda x: f'[{x[COLUMN_NAME_ID]}]({x[COLUMN_NAME_LINK]})', axis=1)

        # Convert to records and remove the temporary sorting column
        sprint_records = sprint_data.drop(columns=['type_sort']).to_dict('records')

        # Filter to only include columns shown in the table
        sprint_records = [{
            COLUMN_NAME_ID: record[COLUMN_NAME_ID],
            COLUMN_NAME_NAME: record[COLUMN_NAME_NAME],
            COLUMN_NAME_TYPE: record[COLUMN_NAME_TYPE],
            COLUMN_NAME_PARENT_TYPE: record[COLUMN_NAME_PARENT_TYPE],
            COLUMN_NAME_PARENT_NAME: record[COLUMN_NAME_PARENT_NAME],
            COLUMN_NAME_STAGE: record[COLUMN_NAME_STAGE],
            COLUMN_NAME_STORY_POINTS: record[COLUMN_NAME_STORY_POINTS],
            COLUMN_NAME_FIX_VERSIONS: record[COLUMN_NAME_FIX_VERSIONS],
            COLUMN_NAME_CREATED_DATE: record[COLUMN_NAME_CREATED_DATE],
            COLUMN_NAME_UPDATED_DATE: record[COLUMN_NAME_UPDATED_DATE],
            COLUMN_NAME_SPRINT: record[COLUMN_NAME_SPRINT],
            COLUMN_NAME_PRIORITY: record[COLUMN_NAME_PRIORITY]
        } for record in sprint_records]

        return sprint_records

    @callback(
        [Output('sprint-tickets-with-options-table', 'rowData'),
        Output('sprint-tickets-with-options-table', 'columnDefs')],
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value'),
        Input('sprint-tickets-with-options-radio', 'value')]
    )
    def update_tickets_in_sprint_table(
        selected_sprint: str,
        selected_types: list[str],
        selected_ticket: str,
        selected_squad: str,
        selected_components: list[str],
        selected_view: str) -> list[dict]:

        if not selected_sprint:
            return [], get_column_defs()

        filter = JiraDataFilter(sprints=[selected_sprint],
                                ticket_types=selected_types,
                                ticketIds=[selected_ticket],
                                squads=[selected_squad],
                                components=selected_components)
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)

        if selected_view == 'defects':
            return get_defects(jira_data_filter_result.tickets, selected_sprint), get_column_defs()
        elif selected_view == 'threshold':
            return get_threshold_violations(jira_data_filter_result.tickets, selected_sprint), get_column_defs(hide_exceeding_stages=False)

        all_tickets = get_all_tickets(jira_data_filter_result.tickets, selected_sprint)
        return all_tickets, get_column_defs()

    @callback(
        [Output('sprint-tickets-with-options-details-table', 'rowData'),
        Output('sprint-tickets-with-options-details-title', 'children')],
        [Input('sprint-dropdown', 'value'),
        Input('sprint-tickets-with-options-table', 'selectedRows'),
        Input('sprint-tickets-with-options-table', 'rowData')]
    )
    def update_ticket_stage_details_table(selected_sprint, selected_rows, table_data):
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
        filter = JiraDataFilter(sprints=[selected_sprint],
                                ticket_types=[],
                                ticketIds=[selected_ticket],
                                squads=[],
                                components=[])
        sprint_data = JiraDataFilterService().filter_tickets(jira_tickets, filter).tickets
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
                    'days': days,
                    'thresholds': thresholds
                })

        # Add total row
        stage_data.append({
            'stage': 'TOTAL',
            'days': total_days
        })

        # Sort stage_data by the original order in all_stage_columns (excluding total row)
        stage_data[:-1] = sorted(stage_data[:-1], key=lambda x: stage_order[x['stage']])

        return (
            stage_data,
            f"{selected_ticket} Cycle Time"
        )