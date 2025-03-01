from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from technical_analysis import TechnicalAnalysis
from database import SignalDatabase
from datetime import datetime, timedelta
import threading
import time
from notifications import TelegramNotifier
import os
import pytz
from projection_container import create_projection_container  # Movido para cá

# Inicialização
db = SignalDatabase()
app = Dash(__name__)
analyzer = TechnicalAnalysis()

# Configuração do Telegram
telegram_token = "7690455274:AAHB64l8csWoE5UpV1Pnn9c8chJzd5sZTXQ"
chat_id = "1249100206"
notifier = TelegramNotifier(telegram_token, chat_id)

# Layout definition
def create_layout():
    return html.Div([
        # Header with background image
        html.Div([
            # Overlay escuro
            html.Div([
                html.H1("KcryptoN", style={
                    'color': '#00ffff',
                    'fontSize': '48px',
                    'textShadow': '0 0 10px rgba(0,255,255,0.5)',
                    'marginBottom': '10px'
                }),
                html.H2("Disciplina e Persistência Levam ao Sucesso Financeiro", style={
                    'color': '#ffffff',
                    'fontSize': '18px',
                    'fontWeight': 'normal',
                    'textShadow': '0 0 5px rgba(255,255,255,0.5)'
                })
            ], style={
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'position': 'absolute',
                'top': 0,
                'left': 0,
                'right': 0,
                'bottom': 0,
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'alignItems': 'center'
            })
        ], style={
            'backgroundImage': 'url("/assets/header_bg.jpg")',
            'backgroundSize': 'cover',
            'backgroundPosition': 'center',
            'height': '200px',
            'position': 'relative',
            'marginBottom': '20px'
        }),
        
        # Status Info
        html.Div([
            html.Span("Sinais Ativos: ", style={'marginRight': '5px'}),
            html.Span(id='signal-count', style={'color': '#00ffff'}),
            html.Span(" | Última Atualização: ", style={'marginLeft': '10px', 'marginRight': '5px'}),
            html.Span(id='last-update', style={'color': '#00ffff'})
        ], style={
            'textAlign': 'center',
            'marginBottom': '20px',
            'color': '#ffffff'
        }),
        
        # Main content
        html.Div([
            # Coluna da esquerda - Sinais Ativos
            html.Div([
                html.H3("Sinais Ativos", style={
                    'color': '#ffffff',
                    'marginBottom': '15px'
                }),
                html.Div(id='signals-container', style={
                    'height': '330px',
                    'overflowY': 'auto',
                    'padding': '10px',
                    'backgroundColor': '#0f2744',
                    'borderRadius': '10px',
                    'minWidth': '300px'
                })
            ], style={
                'flex': '1',
                'marginRight': '10px',
                'width': '48%'  # Ajuste fixo da largura
            }),
            
            # Coluna da direita - Histórico
            html.Div([
                html.H3("Histórico", style={
                    'color': '#ffffff',
                    'marginBottom': '15px'
                }),
                html.Div(id='historical-container', style={
                    'height': '330px',
                    'overflowY': 'auto',
                    'padding': '10px',
                    'backgroundColor': '#0f2744',
                    'borderRadius': '10px',
                    'minWidth': '300px'
                })
            ], style={
                'flex': '1',
                'width': '48%'  # Ajuste fixo da largura
            })
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'flex-start',
            'width': '100%',
            'maxWidth': '1400px',
            'margin': '0 auto 20px auto',  # Adicionado margem inferior
            'padding': '0 20px'
        }),
        
        # Projeção de resultados
        html.Div([
            html.H3("Projeção de Resultados", style={
                'color': '#ffffff',
                'marginBottom': '15px',
                'textAlign': 'center'
            }),
            html.Div(id='results-projection-container', style={
                'height': 'auto',
                'maxHeight': '300px',
                'overflowY': 'auto',
                'overflowX': 'auto',
                'padding': '10px',
                'backgroundColor': '#0f2744',
                'borderRadius': '10px',
                'width': '100%'  # Garante largura total
            })
        ], style={
            'padding': '0 20px',
            'maxWidth': '1400px',
            'margin': '0 auto',
            'width': '100%'
        }),
        dcc.Interval(id='interval-component', interval=1000)
    ], style={
        'backgroundColor': '#0a1929',
        'minHeight': '100vh',
        'margin': 0,
        'padding': 0,
        'fontFamily': 'Arial',
        'overflowX': 'hidden'
    })

# Atribuir o layout ao app
app.layout = create_layout()

def start_monitoring():
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    return monitor_thread

def background_monitor():
    while True:
        try:
            print("\n=== Nova rodada de monitoramento ===")
            
            # Primeiro, atualizar preços dos sinais ativos
            active_signals = db.get_recent_signals(hours=24)
            for signal in active_signals:
                try:
                    symbol = signal['symbol'].replace('.P', '')
                    # Pegar o preço atual do par
                    current_price = analyzer.get_current_price(symbol)
                    if current_price:
                        # Atualizar o preço atual no banco de dados
                        db.update_signal_price(
                            signal['_id'], 
                            current_price,
                            datetime.now()
                        )
                except Exception as e:
                    print(f"Erro ao atualizar preço de {symbol}: {e}")
            
            current_time = datetime.now()
            print(f"Hora: {current_time.strftime('%H:%M:%S')}")
            
            print("\nVerificando pares:")
            total_pares = len(analyzer.futures_pairs)
            
            for idx, symbol in enumerate(analyzer.futures_pairs, 1):
                print(f"\rAnalisando: {symbol} [{idx}/{total_pares}]", end="", flush=True)
                
                for tf in analyzer.timeframes:
                    try:
                        df = analyzer.get_klines(symbol.replace('.P', ''), tf)
                        if df is not None and len(df) >= 20:
                            df = analyzer.calculate_supertrend(df)
                            signal = analyzer.check_signal(df)
                            
                            if signal and signal in ['LONG', 'SHORT']:
                                current_price = float(df['close'].iloc[-1])
                                timestamp = datetime.now()
                                signal_data = {
                                    'symbol': symbol,
                                    'type': signal,
                                    'price': current_price,
                                    'timeframe': tf,
                                    'timestamp': timestamp,
                                    'entry_price': current_price,
                                    'current_price': current_price,
                                    'monitoring_end_date': datetime.now() + timedelta(days=8),
                                    'is_historical': False,
                                    'days_active': 0,
                                    'current_variation': 0,
                                    'leveraged_result': 0,
                                    'profit_loss': 0,
                                    'last_price_update': datetime.now()
                                }
                                
                                try:
                                    db.add_signal(signal_data)
                                    print("\n🔔 SINAL ENCONTRADO!")
                                    print(f"   Par: {symbol}")
                                    print(f"   Tipo: {signal}")
                                    print(f"   TF: {tf}")
                                    print(f"   Preço: {current_price:.8f}")
                                    print("-" * 50)
                                    
                                    try:
                                        notifier.send_signal(signal_data)
                                        print("Sinal enviado para Telegram com sucesso!")
                                    except Exception as e:
                                        print(f"Erro ao enviar para Telegram: {e}")
                                except Exception as e:
                                    print(f"Erro ao salvar sinal no banco: {e}")
                    except Exception as e:
                        print(f"\nErro ao analisar {symbol} em {tf}: {str(e)}")
                        continue
            
            print("\n\nVerificação completa. Aguardando próximo ciclo...")
            time.sleep(300)  # Espera 5 minutos
            
        except Exception as e:
            print(f"\nErro no monitoramento: {e}")
            time.sleep(60)
# Adicione antes do if __name__ == '__main__':

@app.callback(
    [Output('signals-container', 'children'),
     Output('signal-count', 'children'),
     Output('historical-container', 'children'),
     Output('last-update', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_signals(_):
    try:
        tz_BR = pytz.timezone('America/Sao_Paulo')
        current_time = datetime.now(tz_BR).strftime('%H:%M:%S')
        active_signals = db.get_recent_signals(hours=24)
        
        signals = []
        for signal in active_signals:
            is_long = signal['type'] == 'LONG'
            emoji = "🟢" if is_long else "🔴"
            direction = "para cima" if is_long else "para baixo"
            
            card = html.Div([
                html.Div([
                    html.Span(f"{emoji} Ativo: {signal['symbol'].replace('.P', '')}", style={
                        'color': '#ffffff',
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'display': 'block',
                        'marginBottom': '5px'
                    }),
                    html.Span(f"⏱ Candle: {datetime.strptime(signal['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')}", style={
                        'color': '#8b9cc4',
                        'display': 'block',
                        'marginBottom': '5px'
                    }),
                    html.Span(f"🤖 KryptonBot confirmado {direction}", style={
                        'color': '#ffffff'
                    })
                ])
            ], style={
                'backgroundColor': '#1a3958',
                'padding': '15px',
                'borderRadius': '10px',
                'marginBottom': '10px'
            })
            
            signals.append(card)
        
        count = len(signals)
        
        historical_signals = db.get_historical_signals()
        historical_table = dash_table.DataTable(
            data=[{
                'Par': s['symbol'].replace('.P', ''),
                'Tipo': s['type'],
                'Preço': f"{s['price']:.8f}",
                'Data': datetime.strptime(s['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m %H:%M'),
                'Dia': s['days_active']
            } for s in historical_signals],
            columns=[
                {'name': 'Par', 'id': 'Par'},
                {'name': 'Tipo', 'id': 'Tipo'},
                {'name': 'Preço', 'id': 'Preço'},
                {'name': 'Data', 'id': 'Data'},
                {'name': 'Dia', 'id': 'Dia'}
            ],
            style_header={
                'backgroundColor': '#1a3958',
                'color': '#ffffff',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_cell={
                'backgroundColor': '#0f2744',
                'color': '#ffffff',  # Cor padrão do texto
                'textAlign': 'center',
                'padding': '10px',
                'fontSize': '14px'
            }
        )
        
        return signals, f"({count})", historical_table, current_time
    except Exception as e:
        print(f"Erro ao atualizar interface: {e}")
        return [], "(0)", [], datetime.now().strftime('%H:%M:%S')
@app.callback(
    Output('results-projection-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_results_projection(_):
    try:
        active_signals = db.get_recent_signals(hours=24)
        return create_projection_container(active_signals)
    except Exception as e:
        print(f"Erro ao atualizar projeção: {e}")
        return html.Div("Aguardando dados...", style={
            'color': '#ffffff',
            'textAlign': 'center',
            'padding': '20px'
        })
if __name__ == '__main__':
    print("\n=== Iniciando KryptoN Trading Bot ===")
    monitor = start_monitoring()
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)