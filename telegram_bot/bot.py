import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes
from subprocess import check_output

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CustomContext(CallbackContext):
    # Add any custom attributes or methods here if needed
    pass

class ChatData:
    # Add any chat-specific data you need to manage
    pass

# Define your commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(f'Assalamu Alayk {user.first_name}! Welcome to Al-Mokhbir. How can I assist you today?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Here are some commands you can use:\n'
                                    '/start - Welcome message\n'
                                    '/help - List of commands\n'
                                    '/news - Get the latest news summary')

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a news summary."""
    summary = fetch_and_summarize_news()
    await update.message.reply_text(summary)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages."""
    text = update.message.text
    response = f'You said: {text}'
    await update.message.reply_text(response)

def fetch_and_summarize_news() -> str:
    """Fetch and summarize news using the news_fetcher command from the news_manager app."""
    try:
        output = check_output(['python', 'manage.py', 'fetch_news'])
        summary = output.decode('utf-8')
    except Exception as e:
        summary = f"Failed to fetch news: {e}"
    return summary

def main() -> None:
    """Start the bot."""
    context_types = ContextTypes(context=CustomContext, chat_data=ChatData)
    application = Application.builder().token("6761334443:AAE7RuouhdEVsc5gL9jLg_iLJBr_6box_v0").context_types(context_types).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
