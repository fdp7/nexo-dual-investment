import logging
from telegram import Update, BotCommand
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN, DEBUG
from calculator import calculate_net_gain

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
AWAITING_PARAMETERS = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f'Ciao {user.first_name}! Sono un bot per aiutarti a non farti fottere da Nexo Dual investment.\n\n'
        f'Usa il comando /help per investire responsabilmente.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'Questo bot calcola il guadagno netto di una trattativa Nexo Dual investment, considerando '
        'gli interessi guadagnati e la possibile perdita di acquisto\n\n'
        'Comandi disponibili:\n'
        '/start - Avvia il bot\n'
        '/help - Mostra questo messaggio di aiuto\n'
        '/calculate - Calcola guadagno netto, come interessi guadagnati meno perdita di acquisto: G = I - P'
    )

async def calculate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for parameters."""
    await update.message.reply_text(
        'Inserisci i parametri nel formato:'
        'investimento,APY,giorni trattativa,prezzo trattato,simbolo\n'
        'Esempio: 1000,57,3,1800,ETH-USD\n\n'
        'Puoi annullare con /cancel'
    )
    return AWAITING_PARAMETERS

async def process_parameters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        params = update.message.text.split(",")
        if len(params) != 5:
            raise ValueError("Numero errato di parametri")

        s = int(params[0])
        apy = int(params[1])
        t = int(params[2])
        deal = int(params[3])
        symbol = params[4]

        if s <= 0 or apy <= 0 or t <= 0 or deal <= 0 or len(symbol) < 3:
            raise ValueError("I parametri non sono validi")

        result = calculate_net_gain(s, apy, t, deal, symbol)

        response = (
            f"📊 *Risultato del calcolo*\n\n"
            f"💰 Importo investimento: {s}\n"
            f"📈 APY: {apy}%\n"
            f"⌛ Periodo: {t} giorni\n"
            f"🏷️ Prezzo target {symbol}: {deal}\n"
            f"---------------------------------------------------\n"
            f"💸 Interesse guadagnato: {result['interest']:.2f}\n"
            f"🥂 Prezzo di break-even: {result['breakeven_price']:.2f}\n"
            f"🔍 Prezzo previsto: {result['predicted_price']}\n"
            f"❌ Perdita su acquisto: {result['purchase_loss']:.2f}\n"
            f"---------------------------------------------------\n"
            f"💸 *Guadagno netto: {result['net_gain']:.2f}*\n"
            f"---------------------------------------------------\n\n"
            f"📊 *Feedback analisi tecnica:*\n"
            f"🎯 Score: {result['analysis_feedback']['score']:.2f}/{result['analysis_feedback']['max_score']:.2f}\n"
            f"{chr(10).join([f'⚠️ {warning}' for warning in result['analysis_feedback']['warnings']])}\n"
            f"🧠 Feedback: {result['analysis_feedback']['feedback']}\n"
            f"✨ Azioni suggerite: {result['analysis_feedback']['suggested_action']}\n"
        )

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

        # End conversation
        await update.message.reply_text(
            "Puoi calcolare di nuovo usando il comando /calculate"
        )
        return ConversationHandler.END

    except ValueError as e:
        await update.message.reply_text(
            f"Errore: {str(e)}\n"
            f"Per favore, inserisci i parametri nel formato corretto: S,APY,t,deal,symbol\n"
            f"Esempio: 1000,5,30,500,SOL"
        )
        return AWAITING_PARAMETERS
    except Exception as e:
        logger.error(f"Error processing parameters: {e}")
        await update.message.reply_text(
            "Si è verificato un errore durante l'elaborazione. Riprova con /calculate"
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text('Operazione annullata.')
    return ConversationHandler.END

async def set_commands(application):
    commands = [
        BotCommand("start", "Avvia il bot"),
        BotCommand("help", "Mostra aiuto"),
        BotCommand("calculate", "Calcola guadagno netto"),
        BotCommand("cancel", "Annulla l'operazione"),
    ]
    await application.bot.set_my_commands(commands)

def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('calculate', calculate_command)],
        states={
            AWAITING_PARAMETERS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_parameters)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)

    async def post_init(app):
        await set_commands(app)

    application.post_init = post_init

    logger.info("Bot started")
    application.run_polling()

if __name__ == '__main__':
    main()
