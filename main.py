from app.bot_runner import QuizBot
from config import TOKEN, QUESTIONS_JSON_PATH, STAFF_JSON_PATH,REPORT_JSON_PATH
from os import environ
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram.ext.Application").setLevel(logging.CRITICAL)
def main():
    bot = QuizBot(TOKEN, QUESTIONS_JSON_PATH,STAFF_JSON_PATH,REPORT_JSON_PATH,logger)
    logger.info("Bot started")
    bot.start_bot()

if __name__ == "__main__":
    main()