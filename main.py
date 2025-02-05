from quiz_bot.bot_runner import QuizBot
from config import TOKEN, QUESTIONS_JSON_PATH, ALLOWED_USER_IDS
from os import environ

def main():
    bot = QuizBot(TOKEN, QUESTIONS_JSON_PATH,ALLOWED_USER_IDS)
    bot.start_bot()

if __name__ == "__main__":
    main()