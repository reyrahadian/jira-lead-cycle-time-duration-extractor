from dash import Output, Input, callback, no_update, dash_table
import plotly.express as px
import pandas as pd
from config.constants import (
    THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS,
    COLUMN_NAME_TYPE,
    COLUMN_NAME_PROJECT,
    COLUMN_NAME_CREATED_DATE,
    COLUMN_NAME_SPRINT
)
from utils.stage_utils import to_stage_name

stage_mappings = {
    'Blocked': ['Blocked', 'Pending', 'Waiting for support'],
    'In Progress': ['Ready for Development', 'In Development', 'In Progress', 'In Code Review', 'In Design Review', 'In PR',
                    'Failed Test', 'Awaiting SIT Deployment', 'Awaiting UAT Deployment', 'Pending Deployment to UAT', 'Ready for Staging',
                    'PO Review','Ready for Release', 'Pre-Production', 'Awaiting Prod Deployment', 'Discovery', 'In Analysis'],
    'In QA': ['Ready for PR Test', 'In PR Test', 'In SIT Test', 'In UAT Test', 'In QA', 'In Test', 'In UAT Test', 'In Prod Test',
                'In SIT Test', 'In UAT Test', 'In Staging', 'Design Review', 'In Sit', 'Ready for QA', 'Ready for SIT Test', 'Deployed to UAT',
                'In UAT', 'Ready for UAT Test', 'Prod - Pre-check Deployment'],
}

def merged_stages_and_counts(jira_tickets):
    # Calculate stage sums and counts
    stage_sums = jira_tickets[THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS].sum()
    stage_counts = (jira_tickets[THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS] > 0).sum()

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

    return merged_stages, merged_counts

def create_avg_time_spent_figure(jira_tickets):
    merged_stages, merged_counts = merged_stages_and_counts(jira_tickets)

    # Calculate average days per stage
    avg_stages = {}
    for stage in merged_stages:
        if merged_counts[stage] > 0:  # Avoid division by zero
            avg_stages[stage] = merged_stages[stage] / merged_counts[stage]
        else:
            avg_stages[stage] = 0

    # Create DataFrame for the chart
    chart_data = pd.DataFrame({
        'Stage': list(avg_stages.keys()),
        'Days': list(avg_stages.values()),
        'Total': ['Average'] * len(avg_stages),
        'Label': [f"{stage}\n({days:.1f}d)" for stage, days in avg_stages.items()]
    })

    # Create category order based on stage_mappings keys
    category_order = [stage for stage in stage_mappings.keys() if stage in avg_stages]

    # Create horizontal bar chart
    fig = px.bar(
        chart_data,
        x='Days',
        y='Total',
        color='Stage',
        labels={'Days': 'Average Days'},
        title='Average Time Spent in Each Stage',
        category_orders={'Stage': category_order},
        orientation='h',
        text='Label'
    )

    fig.update_layout(
        height=300,
        margin=dict(l=150),
        showlegend=True,
        legend_title_text='Stages',
        yaxis_visible=False,
        xaxis_visible=False,
        xaxis_title=None
    )

    fig.update_traces(
        textposition='inside',
        insidetextanchor='middle',
        textangle=0
    )

    return fig

def create_total_time_spent_figure(jira_tickets):
    # Unpack both dictionaries from the tuple
    merged_stages, merged_counts = merged_stages_and_counts(jira_tickets)

    # Create DataFrame for the chart
    chart_data = pd.DataFrame({
        'Stage': list(merged_stages.keys()),
        'Days': list(merged_stages.values()),
        'Total': ['Total'] * len(merged_stages),
        'Label': [f"{stage}\n({days:.1f}d)" for stage, days in merged_stages.items()]
    })

    # Create category order based on stage_mappings keys
    category_order = [stage for stage in stage_mappings.keys() if stage in merged_stages]

    # Create stacked bar chart
    fig = px.bar(
        chart_data,
        x='Days',
        y='Total',
        color='Stage',
        labels={'Days': 'Total Days'},
        title='Total Time Spent in Each Stage',
        category_orders={'Stage': category_order},
        orientation='h',
        text='Label'  # Use the custom label column
    )

    fig.update_layout(
        height=300,
        margin=dict(l=150),
        showlegend=True,
        legend_title_text='Stages',
        yaxis_visible=False,
        xaxis_visible=False,
        xaxis_title=None  # Hide x-axis label
    )

    # Update text position and format
    fig.update_traces(
        textposition='inside',
        insidetextanchor='middle',
        textangle=0
    )

    return fig

def create_ticket_type_distribution_pie_chart(jira_tickets):
    # Calculate the count of each ticket type
    ticket_type_counts = jira_tickets[COLUMN_NAME_TYPE].value_counts()

    # Create DataFrame for pie chart
    pie_data = pd.DataFrame({
        'Type': ticket_type_counts.index,
        'Count': ticket_type_counts.values
    })

    # Create pie chart
    fig = px.pie(
        pie_data,
        values='Count',
        names='Type',
        title='Distribution of Ticket Types'
    )

    fig.update_layout(
        height=600,
        showlegend=True,
        legend_title_text='Ticket Types'
    )

    return fig

def init_callbacks(app, jira_tickets):
    @callback(
        [Output('ticket-progression-chart', 'figure'),
         Output('avg-ticket-progression-chart', 'figure'),
         Output('ticket-type-distribution-pie-chart', 'figure')],
        [Input('tabs-component', 'value'),
         Input('teams-tab-project-dropdown', 'value'),
         Input('teams-tab-date-range', 'start_date'),
         Input('teams-tab-date-range', 'end_date')]
    )
    def update_chart(active_tab, selected_project, start_date, end_date):
        if active_tab != 'teams-dashboard-tab':
            return no_update, no_update, no_update

        # Filter the data based on selected project and date range
        filtered_tickets = jira_tickets

        if selected_project:
            filtered_tickets = filtered_tickets[filtered_tickets[COLUMN_NAME_PROJECT] == selected_project]
        if start_date:
            filtered_tickets = filtered_tickets[filtered_tickets[COLUMN_NAME_CREATED_DATE] >= start_date]
        if end_date:
            filtered_tickets = filtered_tickets[filtered_tickets[COLUMN_NAME_CREATED_DATE] <= end_date]

        # Filter tickets to only include those assigned to a sprint
        filtered_tickets = filtered_tickets[filtered_tickets[COLUMN_NAME_SPRINT].notna()]

        fig = create_total_time_spent_figure(filtered_tickets)
        fig2 = create_avg_time_spent_figure(filtered_tickets)
        fig3 = create_ticket_type_distribution_pie_chart(filtered_tickets)

        return fig, fig2, fig3

    return app
