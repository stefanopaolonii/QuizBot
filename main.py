from app.bot_runner import QuizBot
from config import QUESTIONS_JSON_PATH
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram.ext.Application").setLevel(logging.CRITICAL)

def main():
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        logger.critical("The TOKEN environment variable is not set! Cannot start the bot.")
        return

    bot = QuizBot(TOKEN, QUESTIONS_JSON_PATH, logger)
    logger.info("Bot started")
    bot.start_bot()

if __name__ == "__main__":
    main()