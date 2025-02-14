# app/handlers.py

from app import (
    main_operation, change_question_operation, report_operation, question_operation, staff_report_operation, single_report_operation
)
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

# Conversation states
SELECTING_ACTION, IFLANGUAGE, SELECT_LANGUAGE, IFTOPIC, SELECT_TOPIC, SELECT_CUSTOM_NQUESTION, SELECT_NUMQUESTION, ANSWERING_QUESTION, QUESTION_TEXT, OPTIONS, CORRECT_OPTION, EXPLANATION, TOPICQ, LANGUAGE, CONFIRMATION, REVIEW, CHANGE_QUESTION, CUSTOM_CHANGING, CHANGING_CORRECT_ANSWER, CHANGING_EXPLANETION, CHANGING_TOPIC, CHANGING_LANGUAGE, DELETE_QUESTION, REPORT_RECEIVED, REPORT_CONFIRMATION, REPORT_MENU, QUESTION_MENU , STAFF_REPORT_MENU, REVIEW_REPORT, SINGLE_REPORT_MENU, MESSAGE_RECEIVED= range(31)
NOT_TAKEN,IN_PROGRESS,COMPLETED, VIEWED = range(4)



# Function for the main menu keyboard
def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    rows= [["Start Quiz"]]
    button_labels = [["Start Quiz"], ["Add Question"], ["Review Question"],["Change Question"]]
    return ReplyKeyboardMarkup(button_labels, one_time_keyboard=True, resize_keyboard=True)

def make_inline_keyboard_from_list(list_options: list, row_size: int = 2) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(option[1], callback_data=option[0]) for option in list_options]
    rows = [buttons[i:i + row_size] for i in range(0, len(buttons), row_size)]
    return InlineKeyboardMarkup(rows)

def make_inline_keyboard_for_list(list_topics: list, row_size: int = 2) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(topic, callback_data=topic) for topic in list_topics]
    rows = [buttons[i:i + row_size] for i in range(0, len(buttons), row_size)]
    return InlineKeyboardMarkup(rows)

def make_inline_keyboard_for_choice() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton("Yes", callback_data="Yes"), InlineKeyboardButton("No", callback_data="No")]
    return InlineKeyboardMarkup([buttons])

def make_inline_keyboard_for_question_quiz(num_options: int, row_size: int = 2) -> InlineKeyboardMarkup:
    letters = [chr(ord('A') + i) for i in range(num_options)]
    buttons = [InlineKeyboardButton(letter, callback_data=letter) for letter in letters]
    rows = [buttons[i:i + row_size] for i in range(0, len(buttons), row_size)]
    rows.append([InlineKeyboardButton("Skip", callback_data="Skip")])
    return InlineKeyboardMarkup(rows)

def make_inline_keyboard_for_question(num_options: int, row_size: int = 2) -> InlineKeyboardMarkup:
    letters = [chr(ord('A') + i) for i in range(num_options)]
    buttons = [InlineKeyboardButton(letter, callback_data=letter) for letter in letters]
    rows = [buttons[i:i + row_size] for i in range(0, len(buttons), row_size)]
    return InlineKeyboardMarkup(rows)


# Function to create a keyboard for the quiz
def make_keyboard_for_question(num_options: int, row_size: int = 2) -> ReplyKeyboardMarkup:
    letters = [chr(ord('A') + i) for i in range(num_options)]
    rows = [letters[i:i + row_size] for i in range(0, len(letters), row_size)]
    rows.append(["Skip", "Cancel"])
    return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)

# Function to create a keyboard from a list of topics
def make_keyboard_for_topics(list_topics) -> ReplyKeyboardMarkup:
    rows = [[topic] for topic in list_topics]
    return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)

# Function to create a keyboard from a list of options
def make_keyboard_from_list(list_options) -> ReplyKeyboardMarkup:
    rows = [[option] for option in list_options]
    return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)
    
# Function to create a keyboard for choice
def make_keyboard_for_choice() -> ReplyKeyboardMarkup:
    rows = [["Yes", "No"]]
    return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)

def _escape_markdown(text: str) -> str:
    escape_chars = r'\[]()~`>#+-={}.!?'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def extract_list_of_main_operations(roles: list) -> list:
    return [(operation, main_operation[operation][0]) for operation in main_operation.keys() if main_operation[operation][1] in roles]

def extract_list_of_question_operations(roles: list) -> list:
    return [(operation, question_operation[operation][0]) for operation in question_operation.keys() if question_operation[operation][1] in roles]

def extract_list_of_question_changing_operations(roles: list) -> list:
    return [(operation, change_question_operation[operation][0]) for operation in change_question_operation.keys() if change_question_operation[operation][1] in roles]

def extract_list_of_report_operations(roles: list) -> list:
    return [(operation, report_operation[operation][0]) for operation in report_operation.keys() if report_operation[operation][1] in roles]

def extract_list_of_staff_report_operations(roles: list) -> list:
    return [(operation, staff_report_operation[operation][0]) for operation in staff_report_operation.keys() if staff_report_operation[operation][1] in roles]

def extract_list_of_single_report_operations(roles: list) -> list:
    return [(operation, single_report_operation[operation][0]) for operation in single_report_operation.keys() if single_report_operation[operation][1] in roles]