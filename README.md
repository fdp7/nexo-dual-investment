# Telegram Bot per il Calcolo del Guadagno Netto

Questo bot Telegram calcola il guadagno netto basato su parametri di investimento forniti dall'utente, utilizzando la formula:

```
G = interessi - perdita d'acquisto
```

Dove:
- G è il guadagno netto

## Requisiti

- Python 3.7+
- python-telegram-bot
- python-dotenv

## Installazione

1. Clona il repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Installa le dipendenze:
```
pip install -r requirements.txt
```

3. Crea un file `.env` nella directory principale del progetto con il seguente contenuto:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DEBUG=False
```

Sostituisci `your_telegram_bot_token` con il token del tuo bot Telegram. Puoi ottenere un token parlando con [BotFather](https://t.me/botfather) su Telegram.

## Esecuzione del Bot

Per avviare il bot, esegui:

```
python main.py
```

## Utilizzo

Una volta avviato il bot, puoi interagire con esso su Telegram usando i seguenti comandi:

- `/start` - Avvia il bot e mostra un messaggio di benvenuto
- `/help` - Mostra un messaggio di aiuto con i comandi disponibili
- `/calculate` - Inizia il processo di calcolo del guadagno netto
- `/cancel` - Annulla l'operazione corrente

## Note

- Attualmente, il valore di dB è generato casualmente tra 0 e 100. In una versione futura, questo potrebbe essere calcolato in base a dati in tempo reale.
- Tutti i parametri di input (S, APY, t) devono essere numeri interi positivi.
