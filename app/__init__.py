# app/__init__.py

main_operation={
    "start_quiz": ["🎲 Start Quiz"],
    "review_question": ["🔍 Review Question"]
}

last_question_id = -1

main_menu_text = (
    f"📋 *Main Menu*\n\n"
    f"_Please select an action from the button:_"
)

def get_next_question_id():
    global last_question_id
    last_question_id += 1
    return last_question_id

def set_last_question_id(question_id):
    global last_question_id
    last_question_id = question_id
