import requests

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_signal(self, signal_data):
        try:
            emoji = "🟢" if signal_data['type'] == 'LONG' else "🔴"
            direction = "COMPRA" if signal_data['type'] == 'LONG' else "VENDA"
            
            message = (
                f"🚨 NOVO SINAL DETECTADO!\n\n"
                f"{emoji} Par: {signal_data['symbol'].replace('.P', '')}\n"
                f"📊 Tipo: {direction}\n"
                f"💰 Preço: ${signal_data['price']:.8f}\n"
                f"⏱ Timeframe: {signal_data['timeframe']}\n"
                f"📅 Data: {signal_data['timestamp'].strftime('%d/%m/%Y %H:%M')}\n\n"
                f"🤖 KryptoN Trading Bot"
            )
            
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data)
            if response.status_code == 200:
                return True
            else:
                print(f"Erro ao enviar mensagem: {response.text}")
                return False
                
        except Exception as e:
            print(f"Erro ao enviar sinal para Telegram: {e}")
            return False