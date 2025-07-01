from dash import Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.config.constants import (
    STAGE_THRESHOLDS, PRIORITY_ORDER, THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS,
    COLUMN_NAME_SPRINT, COLUMN_NAME_TYPE, COLUMN_NAME_ID, COLUMN_NAME_PRIORITY, STAGE_NAME_GROUPINGS,
    STAGE_NAME_IGNORE, ALL_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS, COLUMN_NAME_LINK, COLUMN_NAME_STORY_POINTS,
    COLUMN_NAME_NAME, COLUMN_NAME_STAGE
)
from src.utils.stage_utils import StageUtils
from src.data.data_filters import JiraDataFilter, JiraDataFilterService

def init_callbacks(app, jira_tickets: pd.DataFrame):
    def get_avg_days_dataframe(jira_tickets: pd.DataFrame, selected_sprint: str, selected_squad: str,
                               selected_types: list[str], selected_components: list[str], selected_ticket: str) -> pd.DataFrame:
        if not selected_sprint:
            # Return empty DataFrame with expected columns instead of empty dict
            return pd.DataFrame(columns=['Stage', 'Days'])

        filter = JiraDataFilter(squads=[selected_squad],
                                sprints=[selected_sprint],
                                ticket_types=selected_types,
                                ticketIds=[selected_ticket],
                                components=selected_components)
        jira_data_filter_result = JiraDataFilterService().filter_tickets(jira_tickets, filter)
        sprint_data = jira_data_filter_result.tickets
        sprint_data = StageUtils.calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)

        # Calculate stage mean using stage_mappings
        stage_sums = {}
        stage_ticket_ids = {}  # New dictionary to store ticket IDs for each stage

        for merged_stage, related_stages in STAGE_NAME_GROUPINGS.items():
            # Calculate the mean for each group of related stages
            related_stage_columns = [StageUtils.to_stage_in_sprint_duration_days_column_name(stage) for stage in related_stages]

            # Filter out columns that don't exist in the DataFrame
            existing_columns = [col for col in related_stage_columns if col in sprint_data.columns]

            if not existing_columns:
                stage_sums[merged_stage] = 0
                stage_ticket_ids[merged_stage] = []
                continue

            # Get tickets with non-zero days in any of the related stages
            tickets_in_stage = sprint_data[sprint_data[existing_columns].gt(0).any(axis=1)]

            if not tickets_in_stage.empty:
                for idx, ticket in tickets_in_stage.iterrows():
                    days_in_stages = [ticket[col] for col in existing_columns if ticket[col] > 0]
                    avg_days = sum(days_in_stages) / len(days_in_stages) if days_in_stages else 0

                total_days = tickets_in_stage[existing_columns].sum().sum()
                num_tickets = len(tickets_in_stage)
                stage_avg = total_days / num_tickets if num_tickets > 0 else 0
                stage_sums[merged_stage] = round(stage_avg, 2)
                stage_ticket_ids[merged_stage] = tickets_in_stage[COLUMN_NAME_ID].tolist()  # Store ticket IDs
            else:
                stage_sums[merged_stage] = 0
                stage_ticket_ids[merged_stage] = []  # Empty list if no tickets

        # Process remaining stages from ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS
        for stage_column in ALL_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS:
            if stage_column not in sprint_data.columns:
                continue  # Skip this column if it doesn't exist

            stage_name = StageUtils.to_stage_name(stage_column)

            # Skip if stage is already processed in STAGE_NAME_GROUPINGS
            if any(stage_name in related_stages for related_stages in STAGE_NAME_GROUPINGS.values()):
                continue

            # Get tickets with non-zero days in this stage
            tickets_in_stage = sprint_data[sprint_data[stage_column] > 0]

            if not tickets_in_stage.empty:
                total_days = tickets_in_stage[stage_column].sum()
                num_tickets = len(tickets_in_stage)
                stage_avg = total_days / num_tickets if num_tickets > 0 else 0
                stage_sums[stage_name] = round(stage_avg, 2)
                stage_ticket_ids[stage_name] = tickets_in_stage[COLUMN_NAME_ID].tolist()  # Store ticket IDs
            else:
                stage_ticket_ids[stage_name] = []  # Empty list if no tickets

        # Remove ignored stages
        stage_sums = {stage: value for stage, value in stage_sums.items()
                     if stage not in STAGE_NAME_IGNORE}
        stage_ticket_ids = {stage: ids for stage, ids in stage_ticket_ids.items()
                            if stage not in STAGE_NAME_IGNORE}

        # Filter out zero values
        stage_sums = {k: v for k, v in stage_sums.items() if v > 0}
        stage_ticket_ids = {k: v for k, v in stage_ticket_ids.items() if k in stage_sums}

        # Create DataFrame for the chart
        result = pd.DataFrame({
            'Stage': list(stage_sums.keys()),
            'Days': list(stage_sums.values()),
            'Ticket IDs': [', '.join(map(str, ids)) for ids in stage_ticket_ids.values()],
            'Grouped Stages': [', '.join(STAGE_NAME_GROUPINGS.get(stage, [stage])) for stage in stage_sums.keys()]
        })

        return result

    @callback(
        Output('tickets-in-stage-bar-chart', 'figure'),
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_bar_chart(selected_sprint, selected_types, selected_ticket, selected_squad, selected_components):
        chart_data = get_avg_days_dataframe(jira_tickets, selected_sprint, selected_squad, selected_types, selected_components, selected_ticket)
        # Create empty figure if no data
        if chart_data.empty:
            fig = go.Figure()
            fig.update_layout(
                title="No data available",
                xaxis_title="Stage",
                yaxis_title="Avg Days",
                height=500,
                margin=dict(b=150)
            )
            return fig

        # Create bar chart with merged stages
        fig = px.bar(
            chart_data,
            x='Stage',
            y='Days',
            labels={'Stage': 'Stage', 'Days': 'Avg Days'},
            title=f'Time Spent in Each Stage - {selected_sprint}',
            custom_data=['Ticket IDs', 'Grouped Stages']
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            margin=dict(b=150),
            clickmode='event'
        )

        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>" +
                         "Avg Days: %{y:.2f}<br>" +
                         "Grouped Stages: %{customdata[1]}<br><extra></extra>"
        )

        return fig

    @callback(
        Output('avg-days-table', 'rowData'),
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_avg_days_table(selected_sprint, selected_types, selected_ticket, selected_squad, selected_components):
        table_data = get_avg_days_dataframe(jira_tickets, selected_sprint, selected_squad, selected_types, selected_components, selected_ticket)

        # Convert DataFrame to list of dictionaries for Dash table
        return table_data.to_dict('records')

    @callback(
        [Output('tickets-in-stage-table', 'rowData'),
         Output('tickets-in-stage-title', 'children'),
         Output('tickets-in-stage-ticket-ids', 'data')],
        [Input('tickets-in-stage-bar-chart', 'clickData'),
         Input('sprint-dropdown', 'value'),
         Input('type-dropdown', 'value'),
         Input('ticket-dropdown', 'value'),
         Input('squad-dropdown', 'value'),
         Input('components-dropdown', 'value')]
    )
    def update_stage_tickets(click_data, selected_sprint: str, selected_types: list[str], selected_ticket: str, selected_squad: str, selected_components: list[str]) -> tuple[list[dict], str, list[str], dict]:
        if not click_data or not selected_sprint:
            return [], "No stage selected", []

        clicked_stage = click_data['points'][0]['x']
        ticket_ids = click_data['points'][0]['customdata'][0].split(', ')

        # Filter by ticket IDs
        sprint_data = jira_tickets[jira_tickets[COLUMN_NAME_ID].isin(ticket_ids)]

        filter = JiraDataFilter(squads=[selected_squad],
                                sprints=[selected_sprint],
                                ticket_types=selected_types,
                                ticketIds=[selected_ticket],
                                components=selected_components)
        jira_data_filter_result = JiraDataFilterService().filter_tickets(sprint_data, filter)

        if jira_data_filter_result.tickets.empty:
            return [], "No tickets found", []

        sprint_data = jira_data_filter_result.tickets
        sprint_data = StageUtils.calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)

        # Use stage_mappings to get all related stages
        related_stages = STAGE_NAME_GROUPINGS.get(clicked_stage, [clicked_stage])
        if not related_stages:
            related_stages = [clicked_stage]
        days_column_names = [StageUtils.to_stage_in_sprint_duration_days_column_name(stage) for stage in related_stages]

        # Get tickets that spent time in any of the related stages
        stage_tickets = sprint_data[sprint_data[days_column_names].sum(axis=1) > 0].copy()
        stage_tickets['days_in_stage'] = stage_tickets[days_column_names].sum(axis=1)

        # Add thresholds column
        thresholds = STAGE_THRESHOLDS.get(clicked_stage, STAGE_THRESHOLDS['default'])
        stage_tickets['thresholds'] = [thresholds for _ in range(len(stage_tickets))]

        # Add priority order column for sorting
        if COLUMN_NAME_PRIORITY in stage_tickets.columns:
            stage_tickets['priority_sort'] = stage_tickets[COLUMN_NAME_PRIORITY].map(lambda x: PRIORITY_ORDER.get(x, 8))
        else:
            stage_tickets['priority_sort'] = 8

        # Define columns to select
        available_columns = [
            COLUMN_NAME_ID,
            COLUMN_NAME_NAME,
            COLUMN_NAME_TYPE,
            COLUMN_NAME_PRIORITY,
            COLUMN_NAME_SPRINT,
            COLUMN_NAME_STAGE,
            'days_in_stage',
            COLUMN_NAME_STORY_POINTS,
            'thresholds'
            ]

        # Sort by priority first, then days in stage
        stage_tickets = stage_tickets.sort_values(
            by=['priority_sort', 'days_in_stage'],
            ascending=[True, False]
        )

        # Convert ID column to markdown links
        stage_tickets[COLUMN_NAME_ID] = stage_tickets.apply(lambda x: f'[{x[COLUMN_NAME_ID]}]({x[COLUMN_NAME_LINK]})', axis=1)

        # Convert to records and drop the sorting column
        table_data = stage_tickets[available_columns].to_dict('records')

        return (
            table_data,
            f"Tickets in {clicked_stage} Stage",
            ticket_ids,  # Return the extracted ticket IDs
        )

    @callback(
        [Output('tickets-in-stage-ticket-details-table', 'rowData'),
        Output('tickets-in-stage-ticket-details-title', 'children')],
        [Input('sprint-dropdown', 'value'),
        Input('tickets-in-stage-table', 'selectedRows'),
        Input('tickets-in-stage-table', 'rowData')]
    )
    def update_stage_ticket_details(selected_sprint, selected_rows, table_data):
        result = (
            [],
            "Ticket's Cycle Time"
        )
        if not selected_rows or not table_data or len(selected_rows) == 0 or len(table_data) == 0:
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
                    for idx, stage in enumerate(THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS)}

        # Prepare stage duration data using all_stage_columns
        stage_data = []
        total_days = 0
        for col in THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS:
            stage_name = StageUtils.to_stage_name(col)
            thresholds = STAGE_THRESHOLDS.get(stage_name, STAGE_THRESHOLDS['default'])
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

        # Filter out ignored stages
        stage_data = [entry for entry in stage_data if entry['stage'] not in STAGE_NAME_IGNORE]

        # Sort stage_data by the original order in all_stage_columns (excluding total row)
        stage_data[:-1] = sorted(stage_data[:-1], key=lambda x: stage_order[x['stage']])

        return (
            stage_data,
            f"{selected_ticket} Cycle Time"
        )