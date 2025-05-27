from dash import callback, Input, Output
from src.data.data_filters import JiraDataFilter, JiraDataFilterService
from src.config.constants import COLUMN_NAME_ID, COLUMN_NAME_LINK, COLUMN_NAME_TYPE, COLUMN_NAME_PRIORITY, \
    COLUMN_NAME_STORY_POINTS, COLUMN_NAME_PARENT_TYPE, COLUMN_NAME_PARENT_NAME, COLUMN_NAME_CREATED_DATE, PRIORITY_ORDER, \
    COLUMN_NAME_STAGE, COLUMN_NAME_NAME
from src.utils.sprint_utils import get_sprint_date_range

def init_callbacks(app, jira_tickets):
    @callback(
        Output('defects-table', 'rowData'),
        [Input('project-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('sprint-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_defects_table(selected_project: str, selected_squad: str, selected_sprint: str, selected_components: list[str]) -> list[dict]:
        if not selected_project or not selected_sprint:
            return []

        filter = JiraDataFilter(projects=[selected_project],
                                sprints=[selected_sprint],
                                squads=[selected_squad],
                                components=selected_components)
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)

        # Filter defects
        defects = jira_data_filter_result.tickets[jira_data_filter_result.tickets[COLUMN_NAME_TYPE].isin(['Bug', 'Defect'])].copy()
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
            COLUMN_NAME_PARENT_TYPE, COLUMN_NAME_PARENT_NAME, COLUMN_NAME_LINK
        ]].copy()

        # Convert ID column to markdown links
        table_data[COLUMN_NAME_ID] = table_data.apply(lambda x: f'[{x[COLUMN_NAME_ID]}]({x[COLUMN_NAME_LINK]})', axis=1)

        return table_data.to_dict('records')

