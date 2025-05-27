from dash import Input, Output, callback
from src.data.data_filters import JiraDataFilter, JiraDataFilterService
from src.config.constants import COLUMN_NAME_ID, COLUMN_NAME_LINK, COLUMN_NAME_TYPE, COLUMN_NAME_PARENT_TYPE, \
    COLUMN_NAME_PARENT_NAME, COLUMN_NAME_STAGE, COLUMN_NAME_STORY_POINTS, COLUMN_NAME_FIX_VERSIONS, \
    COLUMN_NAME_CREATED_DATE, COLUMN_NAME_UPDATED_DATE, COLUMN_NAME_SPRINT, COLUMN_NAME_NAME

def init_callbacks(app, jira_tickets):
    @callback(
        Output('sprint-tickets-table', 'rowData'),
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_tickets_in_sprint_table(selected_sprint: str, selected_types: list[str], selected_ticket: str, selected_squad: str, selected_components: list[str]) -> list[dict]:
        if not selected_sprint:
            return []  # Return empty list instead of strings

        filter = JiraDataFilter(sprints=[selected_sprint],
                                ticket_types=selected_types,
                                ticketIds=[selected_ticket],
                                squads=[selected_squad],
                                components=selected_components)
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)

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
        sprint_data = jira_data_filter_result.tickets.copy()
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
            COLUMN_NAME_SPRINT: record[COLUMN_NAME_SPRINT]
        } for record in sprint_records]

        return sprint_records