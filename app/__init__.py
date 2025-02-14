# app/__init__.py

main_operation={
    "start_quiz": ["🎲 Start Quiz", "User"],
    "question_menu": ["❓ Question Menu", "User"],
    "report_menu": ["📝 Report Menu", "User"]
}
question_operation = {
    "review_question": ["🔍 Review Question", "User"],
    "add_question": ["🛡️ Add Question", "Mod"],
    "change_question": ["🛡️ Change Question", "Mod"],
    "main_menu": ["🔙 Back", "User"]
}

change_question_operation = {
    "correct_answer": ["🛡️ Correct Answer", "Admin"],
    "explanation": ["🛡️ Explanation", "Mod"],
    "topic": ["🛡️ Topic", "Mod"],
    "language": ["🛡️ Language", "Mod"],
    "delete": ["🛑 Delete", "Admin"],
    "nothing": ["Nothing", "Mod"]
}

report_operation = {
    "send_report": ["📝 Send Report", "User"],
    "view_reports_user" :["📂 View Reports", "User"],
    "view_reports": ["🛡️ View Reports", "Mod"],
    "main_menu": ["🔙 Back", "User"]
}

staff_report_operation = {
    "select_report": ["📝 Select Report", "Mod"],
    "delete_completed_report": ["🛑 Delete Completed/Viewed Report", "Admin"],
    "main_menu": ["🔘 Main Menu", "User"],
    "report_menu": ["🔙 Back", "User"]
}

single_report_operation = {
    "status_nottaken": ["❌ Not Taken", "Mod"],
    "status_inprogress": ["⏳ In Progress", "Mod"],
    "status_completed": ["✅ Completed", "Mod"],
    "send_message": ["🚀 Send Message", "Mod"],
    "delete_report": ["🛑 Delete Report", "Admin"],
    "main_menu": ["🔘 Main Menu", "User"],
    "view_reports": ["🔙 Back", "User"]
}

last_question_id = -1
last_report_id = -1
default_number_of_questions = 33
correct_answer_weight = 1
wrong_answer_weight = 0.33

main_menu_text = (
    f"📋 *Main Menu*\n\n"
    f"_Please select an action from the button:_"
)

question_menu_text = (
    f"📋 *Question Menu*\n\n"
    f"_Please select an action from the button:_"
)

report_menu_text = (
    f"📋 *Report Menu*\n\n"
    f"_Please select an action from the button:_"
)

def get_next_question_id():
    global last_question_id
    last_question_id += 1
    return last_question_id

def get_next_report_id():
    global last_report_id
    last_report_id += 1
    return last_report_id

def set_last_question_id(question_id):
    global last_question_id
    last_question_id = question_id

def set_last_report_id(report_id):
    global last_report_id
    last_report_id = report_id