from dash import Output, Input, callback, no_update, dash_table
import plotly.express as px
import pandas as pd
from src.reporting_app.config.constants import THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS
from src.reporting_app.utils.stage_utils import to_stage_name
import dash
import dash_html_components as html

def init_callbacks(app, jira_tickets):
    @callback(
        [Output('ticket-progression-chart', 'figure'),
         Output('teams-metrics-panel', 'children')],
        [Input('tabs-component', 'value')]
    )
    def update_chart(active_tab):
        if active_tab != 'teams-dashboard-tab':
            return no_update, no_update  # Return no_update for both outputs

        # Calculate stage sums and counts
        stage_sums = jira_tickets[THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS].sum()
        stage_counts = (jira_tickets[THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS] > 0).sum()

        # Define stage mappings (add this according to your workflow)
        stage_mappings = {
            'Blocked': ['Blocked', 'Pending', 'Waiting for support'],
            'Discovery': ['Discovery', 'In Analysis'],
            'In Progress': ['Ready for Development', 'In Development', 'In Progress', 'In Code Review', 'In Design Review', 'In PR',
                            'Failed Test', 'Awaiting SIT Deployment', 'Awaiting UAT Deployment', 'Pending Deployment to UAT', 'Ready for Staging',
                            'PO Review','Ready for Release', 'Pre-Production', 'Awaiting Prod Deployment'],
            'In QA': ['Ready for PR Test', 'In PR Test', 'In SIT Test', 'In UAT Test', 'In QA', 'In Test', 'In UAT Test', 'In Prod Test',
                      'In SIT Test', 'In UAT Test', 'In Staging', 'Design Review', 'In Sit', 'Ready for QA', 'Ready for SIT Test', 'Deployed to UAT',
                      'In UAT', 'Ready for UAT Test', 'Prod - Pre-check Deployment'],
            # Add more mappings as needed
        }

        # Combine related stages (modified to track both sum and count)
        merged_stages = {}
        merged_counts = {}
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
                merged_counts[merged_into] = merged_counts.get(merged_into, 0) + stage_counts[stage_name]
            else:
                merged_stages[stage] = stage_sums[stage_name]
                merged_counts[stage] = stage_counts[stage_name]

        # Filter out zero values
        merged_stages = {k: v for k, v in merged_stages.items() if v > 0}

        # Create DataFrame for the chart
        chart_data = pd.DataFrame({
            'Stage': list(merged_stages.keys()),
            'Days': list(merged_stages.values())
        })

        # Create category order based on stage_mappings keys
        category_order = [stage for stage in stage_mappings.keys() if stage in merged_stages]

        # Create bar chart with merged stages and custom category order
        fig = px.bar(
            chart_data,
            x='Stage',
            y='Days',
            labels={'Stage': 'Stage', 'Days': 'Total Days'},
            title=f'Time Spent in Each Stage',
            category_orders={'Stage': category_order}  # Set the custom order
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            margin=dict(b=150),
            clickmode='event'
        )

        # Replace the HTML table with a Dash DataTable
        table_data = [
            dash_table.DataTable(
                data=[
                    {
                        'Stage': stage,
                        'Total Days': f"{total_days:.1f}",
                        'Ticket Count': merged_counts[stage],
                        'Average Days': f"{total_days / merged_counts[stage]:.1f}"
                    }
                    for stage, total_days in merged_stages.items()
                    if merged_counts[stage] > 0
                ],
                columns=[
                    {'name': 'Stage', 'id': 'Stage'},
                    {'name': 'Total Days', 'id': 'Total Days'},
                    {'name': 'Ticket Count', 'id': 'Ticket Count'},
                    {'name': 'Average Days', 'id': 'Average Days'}
                ],
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px'
                }
            )
        ]

        return [fig, table_data]

    return app
