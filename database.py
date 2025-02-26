import sqlite3
from datetime import datetime, timedelta
import threading

class SignalDatabase:
    def __init__(self):
        self._local = threading.local()
        self.connect()
        self.create_tables()

    def connect(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect('signals.db', check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row

    def get_connection(self):
        self.connect()
        return self._local.conn

    def create_tables(self):
        conn = self.get_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                type TEXT NOT NULL,
                price FLOAT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                entry_price FLOAT NOT NULL,
                max_price FLOAT DEFAULT NULL,
                min_price FLOAT DEFAULT NULL,
                best_result FLOAT DEFAULT NULL,
                monitoring_end_date TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                days_active INTEGER DEFAULT 0,
                is_historical BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()

    def add_signal(self, signal_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        monitoring_end = datetime.now() + timedelta(days=7)
        
        try:
            if isinstance(signal_data['timestamp'], datetime):
                timestamp_str = signal_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp_str = signal_data['timestamp']
            
            monitoring_end_str = monitoring_end.strftime('%Y-%m-%d %H:%M:%S')
            
            # Primeiro, vamos verificar se o sinal já existe
            cursor.execute('''
                SELECT COUNT(*) FROM signals 
                WHERE symbol = ? AND type = ? AND timestamp = ?
            ''', (signal_data['symbol'], signal_data['type'], timestamp_str))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO signals (
                        symbol, type, price, timeframe, timestamp, 
                        entry_price, monitoring_end_date, is_historical
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal_data['symbol'],
                    signal_data['type'],
                    signal_data['price'],
                    signal_data['timeframe'],
                    timestamp_str,
                    signal_data['price'],
                    monitoring_end_str,
                    False
                ))
                conn.commit()
                print(f"Novo sinal salvo com sucesso: {signal_data}")
            else:
                print("Sinal duplicado ignorado")
                
        except Exception as e:
            print(f"Erro ao salvar sinal: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()

    def get_recent_signals(self, hours=24):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Pega sinais das últimas 24 horas
        cutoff_time = datetime.now() - timedelta(hours=24)
        cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT * FROM signals 
            WHERE timestamp > ? 
            AND is_historical = FALSE
            ORDER BY timestamp DESC
        ''', (cutoff_str,))
        
        return [dict(row) for row in cursor.fetchall()]

    def get_historical_signals(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Pega sinais entre 24 horas e 8 dias atrás
        start_time = datetime.now() - timedelta(days=8)
        end_time = datetime.now() - timedelta(hours=24)
        
        cursor.execute('''
            SELECT * FROM signals 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_time.strftime('%Y-%m-%d %H:%M:%S'), 
              end_time.strftime('%Y-%m-%d %H:%M:%S')))
        
        return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_signals(self):
        """Remove sinais mais antigos que 8 dias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(days=8)
        cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('DELETE FROM signals WHERE timestamp < ?', (cutoff_str,))
        conn.commit()