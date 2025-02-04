from src.reporting_app.config.constants import COLORS

CARD_STYLE = {
    'padding': '20px',
    'margin': '10px',
    'border-radius': '8px',
    'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
    'background-color': COLORS['card']
}

TABLE_STYLE = {
    'overflowX': 'auto',
    'backgroundColor': COLORS['background']
}

TABLE_HEADER_STYLE = {
    'backgroundColor': COLORS['primary'],
    'color': 'white',
    'fontWeight': 'bold',
    'textAlign': 'left'
}

TABLE_CELL_STYLE = {
    'textAlign': 'left',
    'minWidth': '100px',
    'maxWidth': '300px',
    'whiteSpace': 'normal'
}