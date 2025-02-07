from dash import Output, Input, callback, no_update
import plotly.express as px
import pandas as pd
from src.reporting_app.config.constants import THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS
from src.reporting_app.utils.stage_utils import to_stage_name
import dash

def init_callbacks(app, jira_tickets):
    @callback(
        [Output('ticket-progression-chart', 'figure')],
        [Input('tabs-component', 'value')]
    )
    def update_chart(active_tab):
        print(f"Active tab: {active_tab}")
        # Only update if we're on the teams dashboard tab
        if active_tab != 'teams-dashboard-tab':
            return no_update

        print(f"Num of tickets: {len(jira_tickets)}")
        # Calculate stage sums
        stage_sums = jira_tickets[THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS].sum()

        # Define stage mappings (add this according to your workflow)
        stage_mappings = {
            'In Progress': ['In Development', 'In Progress'],
            'In PR Test': ['Ready for PR Test', 'In PR Test'],
            'In SIT Test': ['Ready for SIT Test', 'In SIT Test', 'In Sit'],
            'Awaiting UAT Deployment': ['Awaiting UAT Deployment', 'Pending Deployment to UAT'],
            'In UAT Test': ['Ready for UAT Test', 'In UAT Test', 'In UAT', 'Deployed to UAT'],
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
        chart_data = pd.DataFrame({
            'Stage': list(merged_stages.keys()),
            'Days': list(merged_stages.values())
        })

        # Create bar chart with merged stages
        fig = px.bar(
            chart_data,
            x='Stage',
            y='Days',
            labels={'Stage': 'Stage', 'Days': 'Total Days'},
            title=f'Time Spent in Each Stage'
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            margin=dict(b=150),
            clickmode='event'
        )

        return [fig]

    return app
