from dash import Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.reporting_app.config.constants import (
    STAGE_THRESHOLDS, PRIORITY_ORDER, THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS, COLORS,
    COLUMN_NAME_SPRINT, COLUMN_NAME_TYPE, COLUMN_NAME_SQUAD, COLUMN_NAME_ID, COLUMN_NAME_CALCULATED_COMPONENTS, COLUMN_NAME_PRIORITY
)
from src.reporting_app.utils.jira_utils import create_jira_link
from src.reporting_app.utils.stage_utils import calculate_tickets_duration_in_sprint, to_stage_name, to_stage_in_sprint_duration_days_column_name

def init_callbacks(app, jira_tickets):
    def get_avg_days_dataframe(jira_tickets, selected_sprint, selected_squad, selected_types, selected_components, selected_ticket):
        if not selected_sprint:
            # Return empty DataFrame with expected columns instead of empty dict
            return pd.DataFrame(columns=['Stage', 'Days'])

        # Filter data
        sprint_data = jira_tickets[jira_tickets[COLUMN_NAME_SPRINT].str.contains(selected_sprint, na=False)]
        sprint_data = calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)
        if selected_squad and COLUMN_NAME_SQUAD in sprint_data.columns:
            sprint_data = sprint_data[sprint_data[COLUMN_NAME_SQUAD] == selected_squad]
        if selected_types and len(selected_types) > 0:
            sprint_data = sprint_data[sprint_data[COLUMN_NAME_TYPE].isin(selected_types)]
        if selected_components and len(selected_components) > 0:
            sprint_data = sprint_data[sprint_data[COLUMN_NAME_CALCULATED_COMPONENTS].apply(
                lambda x: any(comp in str(x).split(',') for comp in selected_components) if pd.notna(x) else False
            )]
        if selected_ticket:
            sprint_data = sprint_data[sprint_data[COLUMN_NAME_ID] == selected_ticket]

        # Calculate stage mean
        stage_sums = sprint_data[THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS].apply(lambda x: x[x > 0].mean() if any(x > 0) else 0)

        # Define stage mappings (add this according to your workflow)
        stage_mappings = {
            'In Progress': ['In Development', 'In Progress'],
            'In PR Test': ['Ready for PR Test', 'In PR Test'],
            'In SIT Test': ['Ready for SIT Test', 'In SIT Test', 'In Sit'],
            'Awaiting UAT Deployment': ['Awaiting UAT Deployment', 'Pending Deployment to UAT'],
            'In UAT Test': ['Ready for UAT Test', 'In UAT Test', 'In UAT', 'Deployed to UAT'],
            'Awaiting Prod Deployment': ['Awaiting Prod Deployment', 'Prod - Pre-check Deployment'],
            # Add more mappings as needed
        }

        # Combine related stages
        merged_stages = {}
        for stage_name in stage_sums.index:
            stage = to_stage_name(stage_name)
            # Check if this stage should be merged
            merged_into = None
            for merged_name, related_stages in stage_mappings.items():
                if stage in related_stages:
                    merged_into = merged_name
                    break

            if merged_into:
                merged_stages[merged_into] = merged_stages.get(merged_into, 0) + stage_sums[stage_name]
            else:
                merged_stages[stage] = stage_sums[stage_name]

        # Filter out zero values
        merged_stages = {k: v for k, v in merged_stages.items() if v > 0}

        # Create DataFrame for the chart
        result = pd.DataFrame({
            'Stage': list(merged_stages.keys()),
            'Days': list(merged_stages.values())
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
            title=f'Time Spent in Each Stage - {selected_sprint}'
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            margin=dict(b=150),
            clickmode='event'
        )

        return fig

    @callback(
        Output('avg-days-table', 'data'),
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
        [Output('tickets-in-stage-table', 'data'),
        Output('tickets-in-stage-title', 'children'),
        Output('tickets-in-stage-title', 'style'),
        Output('tickets-in-stage-table', 'style_data_conditional')],
        [Input('tickets-in-stage-bar-chart', 'clickData'),
        Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_stage_tickets(click_data, selected_sprint, selected_types, selected_ticket, selected_squad, selected_components):
        if not click_data or not selected_sprint:
            return [], "No stage selected", {'display': 'none'}, []

        clicked_stage = click_data['points'][0]['x']
        stage_name = to_stage_name(clicked_stage)
        days_column_name = to_stage_in_sprint_duration_days_column_name(stage_name)
        thresholds = STAGE_THRESHOLDS.get(clicked_stage, STAGE_THRESHOLDS['default'])

        # Filter data
        sprint_data = jira_tickets[jira_tickets[COLUMN_NAME_SPRINT].str.contains(selected_sprint, na=False)]
        sprint_data = calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)
        if selected_squad and COLUMN_NAME_SQUAD in sprint_data.columns:
            sprint_data = sprint_data[sprint_data[COLUMN_NAME_SQUAD] == selected_squad]
        if selected_types and len(selected_types) > 0:
            sprint_data = sprint_data[sprint_data[COLUMN_NAME_TYPE].isin(selected_types)]
        if selected_ticket:
            sprint_data = sprint_data[sprint_data[COLUMN_NAME_ID] == selected_ticket]

        # Apply components filter if selected
        if selected_components and len(selected_components) > 0:
            sprint_data = sprint_data[sprint_data[COLUMN_NAME_CALCULATED_COMPONENTS].apply(
                lambda x: any(comp in str(x).split(',') for comp in selected_components) if pd.notna(x) else False
            )]

        # Get tickets that spent time in this stage
        stage_tickets = sprint_data[sprint_data[days_column_name] > 0].copy()
        stage_tickets['days_in_stage'] = stage_tickets[days_column_name]

        # Add priority order column for sorting
        if COLUMN_NAME_PRIORITY in stage_tickets.columns:
            stage_tickets['priority_sort'] = stage_tickets[COLUMN_NAME_PRIORITY].map(lambda x: PRIORITY_ORDER.get(x, 8))
        else:
            stage_tickets['priority_sort'] = 8

        # Define columns to select
        available_columns = ['ID', 'Name', 'Type', 'Priority', 'Stage', 'days_in_stage', 'StoryPoints', 'Sprint']

        # Sort by priority first, then days in stage
        stage_tickets = stage_tickets.sort_values(
            by=['priority_sort', 'days_in_stage'],
            ascending=[True, False]
        )

        # Convert ID column to markdown links
        stage_tickets['ID'] = stage_tickets['ID'].apply(lambda x: f'[{x}]({create_jira_link(x)})')

        # Convert to records and drop the sorting column
        table_data = stage_tickets[available_columns].to_dict('records')

        # Define conditional styling
        style_conditional = [
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            {
                'if': {
                    'filter_query': f'{{days_in_stage}} >= {thresholds["critical"]}',
                    'column_id': 'days_in_stage'
                },
                'backgroundColor': '#ffcdd2',
                'color': '#c62828'
            },
            {
                'if': {
                    'filter_query': f'{{days_in_stage}} >= {thresholds["warning"]} && {{days_in_stage}} < {thresholds["critical"]}',
                    'column_id': 'days_in_stage'
                },
                'backgroundColor': '#fff9c4',
                'color': '#f9a825'
            },
            {
                'if': {
                    'filter_query': f'{{days_in_stage}} < {thresholds["warning"]}',
                    'column_id': 'days_in_stage'
                },
                'backgroundColor': '#c8e6c9',
                'color': '#2e7d32'
            }
        ]

        return (
            table_data,
            f"Tickets in {clicked_stage} Stage",
            {'display': 'block', 'marginTop': '20px'},
            style_conditional
        )

    @callback(
        [Output('tickets-in-stage-ticket-details-container', 'style'),
        Output('tickets-in-stage-ticket-details-title', 'style'),
        Output('tickets-in-stage-ticket-details-table', 'data'),
        Output('tickets-in-stage-ticket-details-title', 'children'),
        Output('tickets-in-stage-ticket-details-table', 'style_data_conditional')],
        [Input('sprint-dropdown', 'value'),
        Input('tickets-in-stage-table', 'selected_rows'),
        Input('tickets-in-stage-table', 'data')]
    )
    def update_stage_ticket_details(selected_sprint, selected_rows, table_data):
        if not selected_rows or not table_data or len(selected_rows) == 0 or len(table_data) == 0:
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
        sprint_data = jira_tickets[jira_tickets[COLUMN_NAME_SPRINT].str.contains(selected_sprint, na=False)]
        sprint_data = calculate_tickets_duration_in_sprint(sprint_data, selected_sprint)
        ticket_data = sprint_data[sprint_data[COLUMN_NAME_ID] == selected_ticket]
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
                    for idx, stage in enumerate(THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS)}

        # Prepare stage duration data using all_stage_columns
        stage_data = []
        total_days = 0
        for col in THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS:
            stage_name = to_stage_name(col)
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
            {'color': COLORS['primary'], 'margin-bottom': '20px', 'display': 'block'},
            stage_data,
            f"Stage Duration Details for {selected_ticket}",
            style_conditional
        )