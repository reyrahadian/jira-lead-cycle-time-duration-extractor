from dash import Input, Output, callback
from src.data.loaders import JiraDataSingleton, JiraDataFilter
from src.config.constants import COLUMN_NAME_ID, COLUMN_NAME_LINK, COLUMN_NAME_TYPE

def init_callbacks(app, jira_tickets):
    @callback(
        Output('sprint-tickets-table', 'data'),
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_tickets_in_sprint_table(selected_sprint, selected_types, selected_ticket, selected_squad, selected_components):
        if not selected_sprint:
            return []  # Return empty list instead of strings

        filter = JiraDataFilter(sprint=selected_sprint, ticket_types=selected_types, ticketId=selected_ticket, squad=selected_squad, components=selected_components)
        jira_data_filter_result = JiraDataSingleton().get_jira_data().filter_tickets(filter)

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

        return sprint_records