from telegram import ReplyKeyboardMarkup

# Conversation states
SELECTING_ACTION, IFLANGUAGE, SELECT_LANGUAGE, IFTOPIC, SELECT_TOPIC, IFNUMBERQUESTION, SELECT_CUSTOM_NQUESTION, SELECT_NUMQUESTION, ANSWERING_QUESTION, QUESTION_TEXT, OPTIONS, CORRECT_OPTION, EXPLANATION, TOPICQ, LANGUAGE, CONFIRMATION, REVIEW, CHANGE_QUESTION, CUSTOM_CHANGING, CHANGING_CORRECT_ANSWER, CHANGING_EXPLANETION, CHANGING_TOPIC, CHANGING_LANGUAGE = range(23)

# Function for the main menu keyboard
def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    button_labels = [["Start Quiz"], ["Add Question"], ["Review Question"],["Change Question"]]
    return ReplyKeyboardMarkup(button_labels, one_time_keyboard=True, resize_keyboard=True)

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
def make_keybord_for_choice() -> ReplyKeyboardMarkup:
    rows = [["Yes", "No"]]
    return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)
