from dash import html
import dash_bootstrap_components as dbc

def create_dora_tiles():
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Badge("", color="", id="lead-time-to-change-badge")
                    ], style={'backgroundColor': 'rgb(44, 62, 80)'}),
                    dbc.CardBody([
                        html.H5("Lead Time for Changes (Average)"),
                        html.H3("", id="lead-time-to-change-value")
                    ])
                ]),
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Badge("", color="", id="deployment-frequency-badge")
                    ], style={'backgroundColor': 'rgb(44, 62, 80)'}),
                    dbc.CardBody([
                        html.H5("Deployment Frequency"),
                        html.H3("", id="deployment-frequency-value")
                    ])
                ]),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Badge("", color="", id="change-failure-rate-badge")
                    ], style={'backgroundColor': 'rgb(44, 62, 80)'}),
                    dbc.CardBody([
                        html.H5("Change Failure Rate"),
                        html.H3("", id="change-failure-rate-value")
                    ])
                ]),
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Badge("", color="", id="time-to-restore-service-badge")
                    ], style={'backgroundColor': 'rgb(44, 62, 80)'}),
                    dbc.CardBody([
                        html.H5("Time to Restore Service"),
                        html.H3("", id="time-to-restore-service-value")
                    ])
                ]),
            ]),
        ], style={'marginTop': '20px'}),
    ])
