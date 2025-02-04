from dash import Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.reporting_app.config.constants import (
    STAGE_THRESHOLDS, PRIORITY_ORDER, THRESHOLD_STAGE_COLUMNS,
    ALL_STAGE_COLUMNS, COLORS
)
from src.reporting_app.utils.jira_utils import create_jira_link

def init_callbacks(app, jira_tickets):
    @callback(
        Output('tickets-in-stage-bar-chart', 'figure'),
        [Input('sprint-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('ticket-dropdown', 'value'),
        Input('squad-dropdown', 'value'),
        Input('components-dropdown', 'value')]
    )
    def update_bar_chart(selected_sprint, selected_types, selected_ticket, selected_squad, selected_components):
        if not selected_sprint:
            return {}

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

        # Calculate stage sums and filter out zero values
        stage_sums = sprint_data[THRESHOLD_STAGE_COLUMNS].sum()
        non_zero_stages = stage_sums[stage_sums > 0]

        # Create DataFrame for the chart
        chart_data = pd.DataFrame({
            'Stage': non_zero_stages.index.str.replace('Stage ', '').str.replace(' days', ''),
            'Days': non_zero_stages.values
        })

        # Create bar chart with non-zero stages only
        fig = px.bar(
            chart_data,
            x='Stage',
            y='Days',
            labels={'Stage': 'Stage', 'Days': 'Total Days'},
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
        stage_column = f"Stage {clicked_stage} days"
        thresholds = STAGE_THRESHOLDS.get(clicked_stage, STAGE_THRESHOLDS['default'])

        # Filter data
        sprint_data = jira_tickets[jira_tickets['Sprint'].str.contains(selected_sprint, na=False)]
        if selected_squad and 'Squad' in sprint_data.columns:
            sprint_data = sprint_data[sprint_data['Squad'] == selected_squad]
        if selected_types and len(selected_types) > 0:
            sprint_data = sprint_data[sprint_data['Type'].isin(selected_types)]
        if selected_ticket:
            sprint_data = sprint_data[sprint_data['ID'] == selected_ticket]

        # Apply components filter if selected
        if selected_components and len(selected_components) > 0:
            sprint_data = sprint_data[sprint_data['CalculatedComponents'].apply(
                lambda x: any(comp in str(x).split(',') for comp in selected_components) if pd.notna(x) else False
            )]

        # Get tickets that spent time in this stage
        stage_tickets = sprint_data[sprint_data[stage_column] > 0].copy()
        stage_tickets['days_in_stage'] = stage_tickets[stage_column]

        # Add priority order column for sorting
        if 'Priority' in stage_tickets.columns:
            stage_tickets['priority_sort'] = stage_tickets['Priority'].map(lambda x: PRIORITY_ORDER.get(x, 8))
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
        [Input('tickets-in-stage-table', 'selected_rows'),
        Input('tickets-in-stage-table', 'data')]
    )
    def update_stage_ticket_details(selected_rows, table_data):
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

        # Filter data for selected ticket
        ticket_data = jira_tickets[jira_tickets['ID'] == selected_ticket]
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
        stage_order = {stage.replace('Stage ', '').replace(' days', ''): idx
                    for idx, stage in enumerate(ALL_STAGE_COLUMNS)}

        # Prepare stage duration data using all_stage_columns
        stage_data = []
        total_days = 0
        for col in ALL_STAGE_COLUMNS:
            stage_name = col.replace('Stage ', '').replace(' days', '')
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
            {'color': COLORS['primary'], 'margin-bottom': '20px', 'display': 'block'},
            stage_data,
            f"Stage Duration Details for {selected_ticket}",
            style_conditional
        )