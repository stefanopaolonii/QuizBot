# app/handlers.py

from app import main_operation
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from enum import Enum, auto

# Conversation states
class State(Enum):
    SELECTING_ACTION = auto()
    IF_LANGUAGE = auto()
    SELECT_LANGUAGE = auto()
    IF_TOPIC = auto()
    SELECT_TOPIC = auto()
    SELECT_CUSTOM_NQUESTION = auto()
    SELECT_NUMQUESTION = auto()
    ANSWERING_QUESTION = auto()
    REVIEW = auto()

# Callback Data Constants
CALLBACK_YES = "Yes"
CALLBACK_NO = "No"
CALLBACK_SKIP = "Skip"
CALLBACK_MAIN_MENU = "main_menu"

def make_inline_keyboard_from_list(list_options: list, row_size: int = 2) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(option[1], callback_data=option[0]) for option in list_options]
    rows = [buttons[i:i + row_size] for i in range(0, len(buttons), row_size)]
    return InlineKeyboardMarkup(rows)

def make_inline_keyboard_for_list(list_topics: list, row_size: int = 2) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(topic, callback_data=topic) for topic in list_topics]
    rows = [buttons[i:i + row_size] for i in range(0, len(buttons), row_size)]
    return InlineKeyboardMarkup(rows)

def make_inline_keyboard_for_choice() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(CALLBACK_YES, callback_data=CALLBACK_YES), InlineKeyboardButton(CALLBACK_NO, callback_data=CALLBACK_NO)]
    return InlineKeyboardMarkup([buttons])

def make_inline_keyboard_for_question_quiz(num_options: int, row_size: int = 2) -> InlineKeyboardMarkup:
    letters = [chr(ord('A') + i) for i in range(num_options)]
    buttons = [InlineKeyboardButton(letter, callback_data=letter) for letter in letters]
    rows = [buttons[i:i + row_size] for i in range(0, len(buttons), row_size)]
    rows.append([InlineKeyboardButton(CALLBACK_SKIP, callback_data=CALLBACK_SKIP)])
    return InlineKeyboardMarkup(rows)

def _escape_markdown(text: str) -> str:
    escape_chars = r'\[]()~`>#+-={}.!?'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def extract_list_of_main_operations() -> list:
    return [(operation, main_operation[operation][0]) for operation in main_operation.keys()]