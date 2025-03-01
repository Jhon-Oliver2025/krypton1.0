from dash import html, dash_table, dcc
from dash.dependencies import Input, Output
from dash import html, dash_table

def create_projection_container(active_signals):
    if not active_signals:
        return html.Div("Sem sinais ativos para projeção", style={
            'color': '#ffffff',
            'textAlign': 'center',
            'padding': '20px'
        })
    
    projection_data = []
    for signal in active_signals:
        try:
            entry_price = float(signal.get('entry_price', signal.get('price', 0)))
            current_price = float(signal.get('current_price', signal.get('price', 0)))
            signal_type = signal.get('type', 'UNKNOWN')
            is_long = signal_type == 'LONG'
            
            # Calcula variação percentual
            if entry_price > 0:
                if is_long:
                    variation = ((current_price - entry_price) / entry_price) * 100
                else:
                    variation = ((entry_price - current_price) / entry_price) * 100
            else:
                variation = 0
            
            # Aplica alavancagem 50x
            leveraged_result = variation * 50
            
            # Calcula lucro/prejuízo em $1000
            initial_investment = 1000
            profit_loss = initial_investment * (leveraged_result / 100)
            
            projection_data.append({
                'Par': signal.get('symbol', '').replace('.P', ''),
                'Tipo': signal_type,
                'Preço Entrada': f"{entry_price:.8f}",
                'Preço Atual': f"{current_price:.8f}",
                'Variação': f"{variation:.2f}%",
                'Resultado 50x': f"{leveraged_result:.2f}%",
                'Lucro/Prejuízo': f"${profit_loss:.2f}"
            })
        except Exception as signal_error:
            print(f"Erro ao processar sinal individual: {signal_error}")
            continue
    
    if not projection_data:
        return html.Div("Sem dados válidos para projeção", style={
            'color': '#ffffff',
            'textAlign': 'center',
            'padding': '20px'
        })
    
    return html.Div([
        dash_table.DataTable(
            data=projection_data,
            columns=[
                {'name': col, 'id': col} for col in [
                    'Par', 'Tipo', 'Preço Entrada', 'Preço Atual', 
                    'Variação', 'Resultado 50x', 'Lucro/Prejuízo'
                ]
            ],
            style_header={
                'backgroundColor': '#1a3958',
                'color': '#ffffff',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_cell={
                'backgroundColor': '#0f2744',
                'color': '#ffffff',
                'textAlign': 'center',
                'padding': '10px',
                'fontSize': '14px'
            },
            style_data_conditional=[
                {
                    'if': {
                        'column_id': 'Resultado 50x',
                        'filter_query': '{Resultado 50x} contains "-"'
                    },
                    'color': '#ff4444'
                },
                {
                    'if': {
                        'column_id': 'Resultado 50x',
                        'filter_query': '{Resultado 50x} > "0"'
                    },
                    'color': '#00ff00'
                },
                {
                    'if': {
                        'column_id': 'Variação',
                        'filter_query': '{Variação} contains "-"'
                    },
                    'color': '#ff4444'
                },
                {
                    'if': {
                        'column_id': 'Variação',
                        'filter_query': '{Variação} > "0"'
                    },
                    'color': '#00ff00'
                },
                {
                    'if': {
                        'column_id': 'Lucro/Prejuízo',
                        'filter_query': '{Lucro/Prejuízo} contains "-"'
                    },
                    'color': '#ff4444'
                },
                {
                    'if': {
                        'column_id': 'Lucro/Prejuízo',
                        'filter_query': '{Lucro/Prejuízo} > "$0"'
                    },
                    'color': '#00ff00'
                }
            ]
        )
    ])

def update_projection_table(active_signals):
    if not active_signals:
        return html.Div("Sem sinais ativos para projeção", style={
            'color': '#ffffff',
            'textAlign': 'center',
            'padding': '20px'
        })
    
    projection_data = []
    for signal in active_signals:
        try:
            entry_price = float(signal.get('entry_price', signal.get('price', 0)))
            current_price = float(signal.get('current_price', signal.get('price', 0)))
            signal_type = signal.get('type', 'UNKNOWN')
            is_long = signal_type == 'LONG'
            
            # Calcula variação e resultados financeiros
            # Calcula variação percentual
            if entry_price > 0:
                if is_long:
                    # Para LONG: lucro quando preço sobe
                    variation = ((current_price - entry_price) / entry_price) * 100
                else:
                    # Para SHORT: lucro quando preço desce
                    variation = ((entry_price - current_price) / entry_price) * 100
            else:
                variation = 0
            
            # Aplica alavancagem 50x na variação
            leveraged_result = variation * 50
            
            # Calcula lucro/prejuízo em $1000
            initial_investment = 1000
            profit_loss = initial_investment * (leveraged_result / 100)
            
            projection_data.append({
                'Par': signal.get('symbol', '').replace('.P', ''),
                'Tipo': signal_type,
                'Preço Entrada': f"{entry_price:.8f}",
                'Preço Atual': f"{current_price:.8f}",
                'Variação': f"{variation:.2f}%",
                'Resultado 50x': f"{leveraged_result:.2f}%",
                'Lucro/Prejuízo': f"${profit_loss:.2f}"
            })
        except Exception as signal_error:
            print(f"Erro ao processar sinal individual: {signal_error}")
            continue
    
    if not projection_data:
        return html.Div("Sem dados válidos para projeção", style={
            'color': '#ffffff',
            'textAlign': 'center',
            'padding': '20px'
        })
    
    return dash_table.DataTable(
        data=projection_data,
        columns=[
            {'name': col, 'id': col} for col in [
                'Par', 'Tipo', 'Preço Entrada', 'Preço Atual', 
                'Variação', 'Resultado 50x', 'Lucro/Prejuízo'
            ]
        ],
        style_header={
            'backgroundColor': '#1a3958',
            'color': '#ffffff',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_cell={
            'backgroundColor': '#0f2744',
            'color': '#ffffff',
            'textAlign': 'center',
            'padding': '10px',
            'fontSize': '14px'
        },
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'Resultado 50x',
                    'filter_query': '{Resultado 50x} contains "-"'
                },
                'color': '#ff4444'
            },
            {
                'if': {
                    'column_id': 'Resultado 50x',
                    'filter_query': '{Resultado 50x} > "0"'
                },
                'color': '#00ff00'
            },
            {
                'if': {
                    'column_id': 'Variação',
                    'filter_query': '{Variação} contains "-"'
                },
                'color': '#ff4444'
            },
            {
                'if': {
                    'column_id': 'Variação',
                    'filter_query': '{Variação} > "0"'
                },
                'color': '#00ff00'
            },
            {
                'if': {
                    'column_id': 'Lucro/Prejuízo',
                    'filter_query': '{Lucro/Prejuízo} contains "-"'
                },
                'color': '#ff4444'
            },
            {
                'if': {
                    'column_id': 'Lucro/Prejuízo',
                    'filter_query': '{Lucro/Prejuízo} > "$0"'
                },
                'color': '#00ff00'
            }
        ]
    )