import datetime
import os
import requests
from ics import Calendar

# Configurações de Telegram e iCal
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# URL Privada do iCal (obtida nas configurações da sua agenda Google)
ICAL_URL = os.environ.get("GOOGLE_ICAL_URL")

def send_telegram_message(message):
    """Envia uma mensagem para o Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Erro ao enviar: {response.text}")

def main():
    if not ICAL_URL:
        print("Erro: GOOGLE_ICAL_URL não configurada.")
        return

    try:
        # Baixa o arquivo .ics da agenda
        print("Baixando agenda...")
        response = requests.get(ICAL_URL)
        calendar = Calendar(response.text)

        # Define o período de "Hoje"
        now = datetime.datetime.now(datetime.timezone.utc)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        events_today = []
        for event in calendar.events:
            # O ics trabalha com objetos arrow/datetime
            # Verifica se o evento ocorre hoje
            if start_of_today <= event.begin.datetime <= end_of_today:
                events_today.append(event)

        # Ordena por horário
        events_today.sort(key=lambda x: x.begin)

        if not events_today:
            message = "📅 *Agenda de Hoje*\n\nNenhum compromisso para hoje! 🎉"
        else:
            message = f"📅 *Agenda de Hoje ({now.strftime('%d/%m/%Y')})*\n\n"
            for event in events_today:
                # Formata o horário (ajustando para o fuso local se necessário)
                # Aqui usamos o formato simples HH:MM
                time_str = event.begin.format('HH:mm')
                message += f"⏰ {time_str} - *{event.name}*\n"
                if event.location:
                    message += f"📍 {event.location}\n"
                message += "\n"

        send_telegram_message(message)

    except Exception as e:
        print(f"Erro ao processar agenda: {e}")

if __name__ == "__main__":
    main()
