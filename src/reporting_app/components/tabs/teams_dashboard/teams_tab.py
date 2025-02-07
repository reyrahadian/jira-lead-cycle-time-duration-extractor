from dash import html, dcc

def create_teams_tab():
    return dcc.Tab(
        label='Teams Dashboard',
        value='teams-dashboard-tab',
        children=[
            html.Div([
                dcc.Graph(id='ticket-progression-chart')
            ])
        ]
    )