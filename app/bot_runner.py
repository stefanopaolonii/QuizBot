# app/bot_runner.py
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackContext, PicklePersistence, CommandHandler, ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from .quiz_manager import QuizManager
from .user_manager import UserManager
from .report_manager import ReportManager
from typing import Dict, List
from .question import Question
from .report import Report
from .staff import Staff
from app import main_menu_text, get_next_question_id,get_next_report_id, last_report_id, default_number_of_questions, question_menu_text, report_menu_text
from .handlers import(
    make_keyboard_from_list, make_keyboard_for_choice, make_inline_keyboard_for_choice, extract_list_of_single_report_operations,
    make_keyboard_for_question, SELECTING_ACTION,  make_inline_keyboard_for_question_quiz,
    IFLANGUAGE, SELECT_LANGUAGE, IFTOPIC, SELECT_TOPIC, make_inline_keyboard_for_question, extract_list_of_staff_report_operations,
    SELECT_CUSTOM_NQUESTION, SELECT_NUMQUESTION, ANSWERING_QUESTION, QUESTION_TEXT, STAFF_REPORT_MENU,
    OPTIONS, CORRECT_OPTION, EXPLANATION, TOPICQ, LANGUAGE, CONFIRMATION, REVIEW, REVIEW_REPORT, MESSAGE_RECEIVED,
    CHANGE_QUESTION, CUSTOM_CHANGING, CHANGING_CORRECT_ANSWER, CHANGING_EXPLANETION, SINGLE_REPORT_MENU,
    CHANGING_TOPIC, CHANGING_LANGUAGE, DELETE_QUESTION, REPORT_RECEIVED, REPORT_CONFIRMATION, REPORT_MENU,QUESTION_MENU,
    NOT_TAKEN,IN_PROGRESS,COMPLETED,VIEWED, _escape_markdown, make_inline_keyboard_from_list, make_inline_keyboard_for_list,
    extract_list_of_main_operations, extract_list_of_question_changing_operations, extract_list_of_report_operations, extract_list_of_question_operations
)
import random, time


class QuizBot:
   
    def __init__(self, token, questions_json_path, staff_json_path, reports_json_path, logger):
        self.token = token
        self.quiz_manager = QuizManager(questions_json_path,logger)
        self.user_manager = UserManager(staff_json_path,logger)
        self.report_manager = ReportManager(reports_json_path,logger)
        self.persistence = PicklePersistence('quiz_bot_data.pkl')
        self.application = Application.builder().token(self.token).persistence(self.persistence).build()
        self.logger = logger

    def start_bot(self):
        self.application.add_handler(CommandHandler("start", self.command_start))
        self.application.add_handler(CommandHandler("cancel", self.command_start))
        self.application.add_handler(CommandHandler("quiz", self.command_quiz))
        self.application.add_handler(CommandHandler("review", self.command_review))
        self.application.add_handler(CommandHandler("addq", self.command_add_question))
        self.application.add_handler(CommandHandler("cq", self.cq_command))
        self.application.add_handler(CommandHandler("restart", self.command_restart))
        self.application.add_handler(CallbackQueryHandler(self.button))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.make_conversation))
        self.application.run_polling()

# Functions for the main conversation

    async def button(self, update: Update, context: CallbackContext):
        query = update.callback_query
        state = context.user_data.get("state", SELECTING_ACTION)
        await query.answer()

        if 'last_message_id' in context.user_data:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
            del context.user_data['last_message_id']

        if query.data == "main_menu":
            await self.command_restart(update, context)
        elif state == SELECT_LANGUAGE:
            await self.conv_quiz_selected_language(update, context)
        elif state == SELECT_TOPIC:
            await self.conv_quiz_selected_topic(update, context)
        elif state == ANSWERING_QUESTION:
            await self.conv_quiz_answer(update, context)
        elif state == CHANGING_CORRECT_ANSWER:
            await self.conv_change_question_selected_correct_answer(update, context)
        elif state == CHANGING_TOPIC:
            await self.conv_change_question_selected_topic(update, context)
        elif state == CHANGING_LANGUAGE:
            await self.conv_change_question_selected_language(update, context)
        elif state == CUSTOM_CHANGING:
            if query.data == "correct_answer":
                await self.conv_change_question_change_correct_answer(update, context)
            elif query.data == "explanation":
                await self.conv_change_question_change_explanetion(update, context)
            elif query.data == "topic":
                await self.conv_change_question_change_topic(update, context)
            elif query.data == "language":
                await self.conv_change_question_change_language(update, context)
            elif query.data == "delete":
                await self.conv_change_question_change_delete(update, context)
            elif query.data == "nothing":
                await self.conv_change_question_details(update, context)
        elif query.data == "start_quiz":
            await self.conv_quiz_start(update, context)
        elif query.data == "question_menu":
            await self.conv_question_menu(update, context)
        elif query.data == "report_menu":
            await self.conv_report_menu(update, context)
        elif state == REPORT_MENU:
            if query.data == "send_report":
                await self.conv_report_send_report(update, context)
            elif query.data == "view_reports_user":
                await self.conv_report_view_reports_user(update, context)
            elif query.data == "view_reports":
                await self.conv_report_view_reports(update, context)
        elif state == STAFF_REPORT_MENU:
            if query.data == "select_report":
                await self.conv_report_select_report(update, context)
            elif query.data == "delete_completed_report":
                await self.conv_report_delete_completed_report(update, context)
        elif state == SINGLE_REPORT_MENU:
            if query.data == "send_message":
                await self.conv_report_send_message(update, context)
            elif query.data == "delete_report":
                await self.conv_report_delete_report(update, context)
            elif query.data == "view_reports" :
                await self.conv_report_view_reports(update, context)
            else:
                await self.conv_report_change_status(update, context)
        elif state == QUESTION_MENU:
            if query.data == "add_question":
                await self.conv_add_question_start(update, context)
            elif query.data == "review_question":
                await self.conv_review_question_start(update, context)
            elif query.data == "change_question":
                await self.conv_change_question_start(update, context)
        elif query.data == "Yes" or query.data == "No":
            if state == IFLANGUAGE:
                await self.conv_quiz_language_selection(update, context)
            elif state == IFTOPIC:
                await self.conv_quiz_topic_selection(update, context)
            elif state == SELECT_CUSTOM_NQUESTION:
                await self.conv_quiz_questions_selection(update, context)
            elif state == CONFIRMATION:
                await self.conv_add_question_confirmation(update, context)
            elif state == DELETE_QUESTION:
                await self.conv_change_question_delete(update, context)
            elif state == REPORT_CONFIRMATION:
                await self.conv_report_confirmation(update, context)

    async def make_conversation(self, update: Update, context: CallbackContext):
        state = context.user_data.get("state", SELECTING_ACTION)

        if state in [SELECT_LANGUAGE, SELECT_TOPIC, SELECT_CUSTOM_NQUESTION, SELECT_NUMQUESTION, QUESTION_TEXT, OPTIONS, CORRECT_OPTION, EXPLANATION, TOPICQ, LANGUAGE, REVIEW, CHANGE_QUESTION, CHANGING_EXPLANETION, REPORT_RECEIVED, REVIEW_REPORT,MESSAGE_RECEIVED]:
            if 'last_message_id' in context.user_data:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_message_id'])
                del context.user_data['last_message_id']

        if update.message.text == "Cancel":
            await self.command_restart(update, context)
        else:
            if state == SELECT_NUMQUESTION:
                await self.conv_quiz_selected_questions(update, context)
            elif state == QUESTION_TEXT:
                await self.conv_add_question_selected_text(update, context)
            elif state == OPTIONS:
                await self.conv_add_question_selected_options(update, context)
            elif state == CORRECT_OPTION:
                await self.conv_add_question_selected_correct_option(update, context)
            elif state == EXPLANATION:
                await self.conv_add_question_selected_explanetion(update, context)
            elif state == TOPICQ:
                await self.conv_add_question_selected_topic(update, context)
            elif state == LANGUAGE:
                await self.conv_add_question_selected_language(update, context)
            elif state == REVIEW:
                await self.conv_review_question_selected_id(update, context)
            elif state == CHANGE_QUESTION:
                await self.conv_change_question_selected_id(update, context)
            elif state == CHANGING_EXPLANETION:
                await self.conv_change_question_selected_explanation(update, context)
            elif state == REPORT_RECEIVED:
                await self.conv_report_review(update, context)
            elif state == REVIEW_REPORT:
                await self.conv_report_selected_report(update, context)
            elif state == MESSAGE_RECEIVED:
                await self.conv_report_received_message(update, context)
            
    async def command_start(self, update: Update, context: CallbackContext):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : issued the /start command.")
        context.user_data.clear()
        message =await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown(main_menu_text),
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_from_list(extract_list_of_main_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = SELECTING_ACTION

    async def command_restart(self, update: Update, context: CallbackContext):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        context.user_data.clear()
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown(main_menu_text),
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_from_list(extract_list_of_main_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = SELECTING_ACTION
        
    async def command_quiz(self, update: Update, context: CallbackContext):
        user_id = self.quiz_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : issued the /quiz command.")
        context.user_data.clear()
        await self.conv_quiz_start(update, context)

    async def command_review(self, update: Update, context: CallbackContext):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : issued the /review command.")
        context.user_data.clear()
        await self.conv_review_question_start(update, context)

    async def command_add_question(self, update: Update, context: CallbackContext):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : issued the /addq command.")
        context.user_data.clear()
        await self.conv_add_question_start(update, context)

    async def cq_command(self, update: Update, context: CallbackContext):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        if not self.user_manager.user_is_staff(user_id):
            self.logger.warning(f"User ID: {user_id} Role: {role}\nMessage : tried to add a question but is not authorized.")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="❌ *You are not authorized to change questions detalils.*", 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.command_restart(update, context)
            return
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : issued the /cq command.")
        context.user_data.clear()
        await self.conv_change_question_start(update, context)


# Functions for the Quiz conversation

    async def conv_quiz_start(self, update: Update, context: CallbackContext):  
        message= await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("_Do you want to choose a language?_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_for_choice()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = IFLANGUAGE
    
    async def conv_quiz_language_selection(self, update: Update, context: CallbackContext):
        query = update.callback_query
        action = query.data.lower()
        if action == "yes":
            context.user_data["custom_language"] = True
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("_Select your language from the keyboard:_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_list(self.quiz_manager.extract_list_of_all_languages())
            )
            context.user_data["state"] = SELECT_LANGUAGE
        else:
            context.user_data["custom_language"] = False
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("_Do you want to select a specific topic?_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_choice()
            ) 
            context.user_data["state"] = IFTOPIC
        context.user_data["last_message_id"] = message.message_id
        
    async def conv_quiz_selected_language(self, update: Update, context: CallbackContext):
        query = update.callback_query
        selected_language = query.data.lower()
        context.user_data["selected_language"] = selected_language
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("_Do you want to select a specific topic?_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_for_choice()
        ) 
        context.user_data["state"] = IFTOPIC
        context.user_data["last_message_id"] = message.message_id
        
    async def conv_quiz_topic_selection(self, update: Update, context: CallbackContext):
        query = update.callback_query
        action = query.data.lower()
        if action == "yes":
            context.user_data["custom_topic"] = True
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("_Select your topic from the keyboard:_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_list(self.quiz_manager.extract_list_of_all_topics())
            )
            context.user_data["state"] = SELECT_TOPIC
        elif action == "no":
            context.user_data["custom_topic"] = False
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("_Do you want to select the questions number?_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_choice()
            ) 
            context.user_data["state"] = SELECT_CUSTOM_NQUESTION
        context.user_data["last_message_id"] = message.message_id

    async def conv_quiz_selected_topic(self, update: Update, context: CallbackContext):
        query = update.callback_query
        selected_topic = query.data.lower()
        context.user_data["selected_topic"] = selected_topic
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("_Do you want to select the questions number?_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_for_choice()
        ) 
        context.user_data["state"] = SELECT_CUSTOM_NQUESTION
        context.user_data["last_message_id"] = message.message_id
        
    async def conv_quiz_questions_selection(self, update: Update, context: CallbackContext):
        query = update.callback_query
        action = query.data.lower()
        if context.user_data["custom_language"] and context.user_data["custom_topic"]:
            maxnumber = self.quiz_manager.get_number_of_questions(topic=context.user_data["selected_topic"],language=context.user_data["selected_language"])
        elif context.user_data["custom_language"] and not context.user_data["custom_topic"]:
            maxnumber = self.quiz_manager.get_number_of_questions(language=context.user_data["selected_language"])
        elif not context.user_data["custom_language"] and context.user_data["custom_topic"]:
            maxnumber = self.quiz_manager.get_number_of_questions(topic=context.user_data["selected_topic"])
        else :
            maxnumber = self.quiz_manager.get_number_of_questions()

        if action == "yes":
            context.user_data["custom_number"] = True
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("_Insert the number of questions (1 - " + str(maxnumber) + "):_"), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data["last_message_id"] = message.message_id
            context.user_data["state"] = SELECT_NUMQUESTION
        else :
            context.user_data["custom_number"] = False
            await self.conv_quiz_start_for_user(update, context, default_number_of_questions)
            context.user_data["state"] = ANSWERING_QUESTION
        
    async def conv_quiz_selected_questions(self, update: Update, context: CallbackContext):
        try:
            num = int(update.message.text)
            maxnumber=0
            if context.user_data["custom_language"] and context.user_data["custom_topic"]:
                maxnumber = self.quiz_manager.get_number_of_questions(topic=context.user_data["selected_topic"],language=context.user_data["selected_language"])
            elif context.user_data["custom_language"] and not context.user_data["custom_topic"]:
                maxnumber = self.quiz_manager.get_number_of_questions(language=context.user_data["selected_language"])
            elif not context.user_data["custom_language"] and context.user_data["custom_topic"]:
                maxnumber = self.quiz_manager.get_number_of_questions(topic=context.user_data["selected_topic"])
            else :
                maxnumber = self.quiz_manager.get_number_of_questions()

            if 1 <= num <= maxnumber:
                await self.conv_quiz_start_for_user(update, context, num)
                context.user_data["state"] = ANSWERING_QUESTION
            else:
                await update.message.reply_text(
                    text=_escape_markdown("_Number out of range (1 - {maxnumber}). Try again_"), 
                    parse_mode="MarkdownV2",
                    reply_markup=ReplyKeyboardRemove()
                )
        except ValueError:
            await update.message.reply_text(
                    text=_escape_markdown("_Please insert a valid number:_"), 
                    parse_mode="MarkdownV2",
                    reply_markup=ReplyKeyboardRemove()
                )
        
    async def conv_quiz_start_for_user(self, update: Update, context: CallbackContext, n_questions: int):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        selected_topic = context.user_data.get("selected_topic")
        selected_language = context.user_data.get("selected_language")
        excluded_keys_t = None
        excluded_keys_l = None
        if selected_topic:
            excluded_keys_t = self.quiz_manager.exclude_questions_not_related_to_selected_topic(selected_topic)
        if selected_language:
            excluded_keys_l = self.quiz_manager.exclude_questions_not_related_to_selected_language(selected_language)
        questions_ids = self.quiz_manager.pick_questions(n_questions, excluded_keys_t, excluded_keys_l)
        
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : started a quiz with {len(questions_ids)} questions.")
        context.user_data["quiz"] = {
            "questions_ids": questions_ids,
            "current_question_scramble_map": {},
            "current_index": 0,
            "correct_count": 0,
            "wrong_count" : 0
        }
        context.user_data["start_time"] = time.time()
        await self.conv_quiz_send_question(update, context)

    async def conv_quiz_send_question(self, update: Update, context: CallbackContext):
        user_quiz = context.user_data["quiz"]
        current_index = user_quiz["current_index"]
        question_ids = user_quiz["questions_ids"]

        if current_index >= len(question_ids):
            await self.conv_quiz_finish(update, context)
            return

        question_id = question_ids[current_index]
        question = self.quiz_manager.get_question_data(question_id)

        scrambled_options_map = self.quiz_manager.scramble_options(question.options)
        user_quiz["current_question_scramble_map"] = scrambled_options_map

        scrambled_options = [question.options[scrambled_options_map[i]] for i in range(len(question.options))]
        message_text = f"❓ *Question {current_index + 1}/{len(question_ids)}*\n\n{question.question_to_string(scrambled_options_map)}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text,
            parse_mode="Markdown",
            reply_markup=make_inline_keyboard_for_question_quiz(len(scrambled_options))
        )
        context.user_data["last_message_id"] = message.message_id

    async def conv_quiz_answer(self, update: Update, context: CallbackContext):
        query = update.callback_query
        action = query.data
        user_quiz = context.user_data.get("quiz")
        user_quiz = context.user_data["quiz"]
        current_index = user_quiz["current_index"]
        question_ids = user_quiz["questions_ids"]

        if action == "Skip":
            user_quiz["current_index"] += 1
        else:
            question_id = question_ids[current_index]
            question = self.quiz_manager.get_question_data(question_id)
            q = self.quiz_manager.get_question_data(question_id)
            scrambled_options_map = user_quiz["current_question_scramble_map"]
            chosen_option = ord(action) - ord('A')
            is_correct = self.quiz_manager.check_answer(question_id, chosen_option, scrambled_options_map)
            correct = next(fake_idx for fake_idx, real_idx in scrambled_options_map.items() if real_idx == q.correct_index)
            message_text = f"❓ *Question {current_index + 1}/{len(question_ids)}*\n\n{question.question_to_string(scrambled_options_map)}\n\n"
            if is_correct:
                user_quiz["correct_count"] += 1
                message_text += f"✅ *Correct answer!*\n\nYour answer: {action}\n"
            else:
                user_quiz["wrong_count"] += 1
                message_text += f"❌ *Wrong answer!*\n\nYour answer: {action}\nCorrect answer: ||{chr(correct + ord('A'))}||\n"
            if "None" not in q.explanation:
                message_text += f"_Comment: {q.explanation}_\n"
            else:
                message_text += f"_Comment not available._\n"

            message_text = _escape_markdown(message_text)

            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, parse_mode="MarkdownV2")

            user_quiz["current_index"] += 1

        await self.conv_quiz_send_question(update, context)

    async def conv_quiz_finish(self, update: Update, context: CallbackContext):
        user_quiz = context.user_data.get("quiz", {})
        correct = user_quiz.get("correct_count", 0)
        wrong = user_quiz.get("wrong_count", 0)
        total = len(user_quiz.get("questions_ids", []))
        score = self.quiz_manager.quiz_score(correct, wrong)
        start_time = context.user_data.get("start_time")
        if start_time:
            end_time = time.time()
            time_taken = end_time - start_time
            hours, remainder = divmod(time_taken, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_taken_formatted = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown(f"🏁 *Quiz finished!*\n\n"
                    f"⏳ Time taken: {time_taken_formatted}\n"
                    f"✅ Correct answers: {correct}/{total}\n"
                    f"👉 Final score: {score:.2f}"),
                parse_mode="MarkdownV2",
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown(f"🏁 *Quiz finished!*\n\n"
                    f"✅ Correct answers: {correct}/{total}\n"
                    f"👉 Final score: {score:.2f}"),
                parse_mode="MarkdownV2",
            )
        await self.command_restart(update, context)

# Method for question menu

    async def conv_question_menu(self, update: Update, context: CallbackContext):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("_Please select an action from the keyboard:_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_from_list(extract_list_of_question_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = QUESTION_MENU

# Functions for adding questions

    async def conv_add_question_start(self, update: Update, context: CallbackContext):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        if not self.user_manager.user_is_staff(user_id):
            self.logger.warning(f"User ID: {user_id} Role: {role}\nMessage : tried to add a question but is not authorized.")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="❌ *You are not authorized to change questions detalils.*", 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.command_restart(update, context)
            return
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : started adding a new question.")
        context.user_data["new_question"] = {} 
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide only the question text:_"), 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = QUESTION_TEXT

    async def conv_add_question_selected_text(self, update: Update, context: CallbackContext):
        context.user_data["new_question"]["text"] = update.message.text
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide the options for the question. In the format: option1;option2;option3 ... : _"), 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = OPTIONS

    async def conv_add_question_selected_options(self, update: Update, context: CallbackContext):
        context.user_data["new_question"]["options"] = update.message.text.split(";")
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide the correct option:_"), 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CORRECT_OPTION
    
    async def conv_add_question_selected_correct_option(self, update: Update, context: CallbackContext):
        context.user_data["new_question"]["correct_option"] = ord(update.message.text.upper()) - ord('A')
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide the explanation for the question:_"), 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = EXPLANATION

    async def conv_add_question_selected_explanetion(self, update: Update, context: CallbackContext):
        context.user_data["new_question"]["explanation"] = update.message.text
        topic_list = self.quiz_manager.extract_list_of_all_topics()
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide the topic for the question.\nChose one of the following topics or create a new one:_ \n\n" + "\n".join(topic_list)), 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = TOPICQ

    async def conv_add_question_selected_topic(self, update: Update, context: CallbackContext):
        context.user_data["new_question"]["topic"] = update.message.text
        language_list = self.quiz_manager.extract_list_of_all_languages()
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide the language for the question.\nChose one of the following languages or create a new one:_ \n\n" + "\n".join(language_list)), 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = LANGUAGE

    async def conv_add_question_selected_language(self, update: Update, context: CallbackContext):
        context.user_data["new_question"]["language"] = update.message.text.lower()

        new_question = context.user_data["new_question"]
        msg = (
            f"🔍 *Review the question details:*\n\n"
            f"*Question:* {new_question['text']}\n"
            f"*Options:*\n" +
            "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(new_question['options'])]) +
            f"\n*Correct Option:* {chr(new_question['correct_option'] + ord('A'))}\n"
            f"*Explanation:* {new_question['explanation']}\n"
            f"*Topic:* {new_question['topic']}\n"
            f"*Language:* {new_question['language']}\n\n"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown(msg), 
            parse_mode="MarkdownV2", 
            reply_markup=ReplyKeyboardRemove()
        )
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("_Do you want to add this question? Select Yes or No:_"),
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_for_choice()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CONFIRMATION

    async def conv_add_question_confirmation(self, update: Update, context: CallbackContext):
        query = update.callback_query
        action = query.data.lower()
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        q=Question(context.user_data["new_question"]["text"], context.user_data["new_question"]["options"], context.user_data["new_question"]["correct_option"], False, context.user_data["new_question"]["explanation"], context.user_data["new_question"]["topic"],get_next_question_id(),context.user_data["new_question"]["language"])
        if action == "yes":
            self.logger.info(f"User ID: {user_id} Role {role}\nMessage : added a new question. {q.id}")
            self.quiz_manager.add_question_data(q)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("✅ *Question added successfully!*"),
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        else :
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("❌ *Question not added.*"),
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        await self.command_restart(update, context)

# Functions for changing questions details

    async def conv_change_question_start(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        if not self.user_manager.user_is_staff(user_id):
            self.logger.warning(f"\nAnonymous ID: {user_id}\nRole: {role}\nMessage: tried to add a question but is not authorized.")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="❌ *You are not authorized to change questions detalils.*", 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.command_restart(update, context)
            return
        context.user_data["changing_question"] = {}
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide the ID of the question you want to change:_"), 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CHANGE_QUESTION

    async def conv_change_question_selected_id(self, update: Update, context: CallbackContext):
        try:
            user_id=self.user_manager.user_get_id(update.effective_user.id)
            role=self.user_manager.user_get_role(user_id)
            q_id = int(update.message.text)
            q = self.quiz_manager.get_question_data(q_id)
            if q is None:
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=_escape_markdown("_Please provide a valid question ID:_"),
                    parse_mode="MarkdownV2",
                    reply_markup=ReplyKeyboardRemove()  
                )
                context.user_data["last_message_id"] = message.message_id
                return
            self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : started changing a question with ID {q_id}")
            context.user_data["changing_question"] = q
            msg = f"🔍 *Review the question details:*\n\n" + q.question_details_to_string()
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,  
                text=_escape_markdown(msg), 
                parse_mode="MarkdownV2", 
                reply_markup=ReplyKeyboardRemove()
            )
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown("_What do you want to change?_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_from_list(extract_list_of_question_changing_operations(self.user_manager.user_allowed_roles(role)))
            )
            context.user_data["last_message_id"] = message.message_id
            context.user_data["state"] = CUSTOM_CHANGING
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid question ID. Please try again.")

    async def conv_change_question_change_correct_answer(self, update: Update, context: CallbackContext):
        q=context.user_data["changing_question"]
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Insert the new correct answer:_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_for_question(len(q.options)))
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CHANGING_CORRECT_ANSWER

    async def conv_change_question_selected_correct_answer(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        query = update.callback_query
        new_correct_option = ord(query.data) - ord('A')
        q=context.user_data["changing_question"]
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage: changed the correct answer of question {q.id} from {chr(q.correct_index + ord('A'))} to {chr(new_correct_option + ord('A'))}")
        context.user_data["changing_question"].correct_index = new_correct_option
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("✅*Correct answer changed successfully!*"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_What do you want to change?_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_from_list(extract_list_of_question_changing_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CUSTOM_CHANGING

    async def conv_change_question_change_explanetion(self, update: Update, context: CallbackContext):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Insert the new explanation:_"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CHANGING_EXPLANETION

    async def conv_change_question_selected_explanation(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        q=context.user_data["changing_question"]
        context.user_data["changing_question"].explanation = update.message.text
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : changed the explanation of question {q.id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("✅ *Explanetion changed successfully!*"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        message = await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown("_What do you want to change?_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_from_list(extract_list_of_question_changing_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CUSTOM_CHANGING
    
    async def conv_change_question_change_topic(self, update: Update, context: CallbackContext):
        topic_list = self.quiz_manager.extract_list_of_all_topics()
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide the new topic for the question.\nChoose one from the keyboard or enter a new topic:_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_for_list(topic_list)
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CHANGING_TOPIC
    
    async def conv_change_question_selected_topic(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        query = update.callback_query
        q=context.user_data["changing_question"]
        context.user_data["changing_question"].topic = query.data
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : changed the topic of question {q.id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("✅ *Topic changed successfully!*"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        message = await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown("_What do you want to change?_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_from_list(extract_list_of_question_changing_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CUSTOM_CHANGING

    async def conv_change_question_change_language(self, update: Update, context: CallbackContext):
        language_list = self.quiz_manager.extract_list_of_all_languages()
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Please provide the new language for the question.\nChose one of the following languages or create a new one:_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_for_list(language_list)
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CHANGING_LANGUAGE
    
    async def conv_change_question_selected_language(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        query = update.callback_query
        q=context.user_data["changing_question"]
        context.user_data["changing_question"].language = query.data.lower()
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : changed the language of question {q.id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("✅ *Language changed successfully!*"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        message = await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown("_What do you want to change?_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_from_list(extract_list_of_question_changing_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = CUSTOM_CHANGING

    async def conv_change_question_change_delete(self, update: Update, context: CallbackContext):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown("_Are you sure you want to delete this question?_"), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_for_choice()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = DELETE_QUESTION

    async def conv_change_question_delete(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        query= update.callback_query
        action = query.data.lower()
        q=context.user_data["changing_question"]
        if action == "yes":
            self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : deleted the question {q.id}")
            self.quiz_manager.quiz_delete_question(q.id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown("✅ *Question deleted successfully! *")
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown("❌ *Question not deleted.*")
            )  
        await self.command_restart(update, context)

    async def conv_change_question_details(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        q=context.user_data["changing_question"]
        msg = f"🔍 *Review the question details:*\n\n" + q.question_details_to_string() + f"\n\n✅ *Question changed successfully!*"
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : finished changing the question {q.id}")
        self.quiz_manager.add_question_data(q)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown(msg), 
            parse_mode="MarkdownV2", 
        )
        await self.command_restart(update, context)
   
   # Functions for review questions

    async def conv_review_question_start(self, update: Update, context: CallbackContext):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("_Please provide the ID of the question you want to review:_"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = REVIEW

    async def conv_review_question_selected_id(self, update: Update, context: CallbackContext):
        try:
            user_id = self.user_manager.user_get_id(update.effective_user.id)
            role = self.user_manager.user_get_role(user_id)
            question_number = int(update.message.text)
            self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : requested question {question_number}")
            q = self.quiz_manager.get_question_data(question_number)
            if q is None:
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=_escape_markdown("_Please provide a valid question ID:_"),
                    parse_mode="MarkdownV2",
                    reply_markup=ReplyKeyboardRemove()  
                )
                context.user_data["last_message_id"] = message.message_id
                return
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown(q.question_to_string_for_review()), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
                )
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="_Invalid question number!_",
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
                )
        await self.command_restart(update, context)

# Functions for send and view reports

    async def conv_report_menu(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=_escape_markdown(report_menu_text), 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_from_list(extract_list_of_report_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = REPORT_MENU
        
    async def conv_report_send_report(self, update: Update, context: CallbackContext):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="_Please write your report:_", 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = REPORT_RECEIVED

    async def conv_report_review(self, update: Update, context: CallbackContext):
        message=update.message.text
        context.user_data["report"]=message
        msg = (
            f"*Review your report:*\n\n"
            f"{context.user_data['report']}\n\n"
            f"_Do you want to send this report? _"
        )
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown(msg), 
            parse_mode="MarkdownV2", 
            reply_markup=make_inline_keyboard_for_choice()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = REPORT_CONFIRMATION

    async def conv_report_confirmation(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        query = update.callback_query
        action = query.data.lower()
        if action == "yes":
            r = Report(get_next_report_id(), user_id, context.user_data["report"],None,NOT_TAKEN)
            self.report_manager.report_add_data(r)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("✅ *Report sent successfully!*"),
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("❌ *Report not sent.*"),
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        await self.command_restart(update, context)
    
    async def conv_report_view_reports(self, update: Update, context: CallbackContext):
        user_id = self.user_manager.user_get_id(update.effective_user.id)
        role = self.user_manager.user_get_role(user_id)
        context.user_data["report"] = None
        report_list = self.report_manager.report_list()
        print(report_list)
        if not report_list:
            print("No reports available")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown("_No reports available._"), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
            
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown(self.report_manager.report_list_to_string(report_list)), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="_Select an operation from the buttons:_", 
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_from_list(extract_list_of_staff_report_operations(self.user_manager.user_allowed_roles(role)))
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = STAFF_REPORT_MENU

    async def conv_report_select_report(self, update: Update, context: CallbackContext):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="_Please provide the ID of the report you want to review:_", 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = REVIEW_REPORT
    
    async def conv_report_delete_completed_report(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : deleted completed report")
        self.report_manager.report_delete_completed_or_viewed_reports()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("✅ *Completed reports deleted successfully!*"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        await self.conv_report_menu(update, context)

    async def conv_report_selected_report(self, update: Update, context: CallbackContext):
        try:
            user_id=self.user_manager.user_get_id(update.effective_user.id)
            role=self.user_manager.user_get_role(user_id)
            report_id = int(update.message.text)
            r = self.report_manager.report_get_data(report_id)
            context.user_data["report"] = r
            if r is None:
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text="_Please provide a valid report ID:_",
                    parse_mode="MarkdownV2",
                    reply_markup=ReplyKeyboardRemove()  
                )
                context.user_data["last_message_id"] = message.message_id
                return
            self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : requested report {report_id}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown(r.report_to_string()), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
                )
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="_Select an operation from the buttons:_", 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_from_list(extract_list_of_single_report_operations(self.user_manager.user_allowed_roles(role)))
            )
            context.user_data["last_message_id"] = message.message_id
            context.user_data["state"] = SINGLE_REPORT_MENU
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="_Invalid report number!_",
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )

    async def conv_report_change_status(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        query = update.callback_query
        action = query.data.lower()
        r=context.user_data["report"]
        if action == "status_nottaken":
            self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : changed the status of report {r.id} to not taken")
            r.status = NOT_TAKEN
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("✅ *Status changed successfully!*"),
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        elif action == "status_inprogress":
            self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : changed the status of report {r.id} to in progress")
            r.status = IN_PROGRESS
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("✅ *Status changed successfully!*"),
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        else :
            self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : changed the status of report {r.id} to completed")
            r.status = COMPLETED
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("✅ *Status changed successfully!*"),
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        self.report_manager.report_add_data(r)
        await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown(r.report_to_string()), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
        )
        message = await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="_Select an operation from the buttons:_", 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_from_list(extract_list_of_single_report_operations(self.user_manager.user_allowed_roles(role)))
            )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = SINGLE_REPORT_MENU

    async def conv_report_delete_report(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        r=context.user_data["report"]
        self.logger.info(f"User ID: {user_id} Role: {role}\nMessage : deleted the report {r.id}")
        self.report_manager.report_delete_report(r.id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("✅ *Report deleted successfully!*"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        await self.conv_report_view_reports(update, context)

    async def conv_report_send_message(self, update: Update, context: CallbackContext):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="_Please write your message for the user:_", 
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = MESSAGE_RECEIVED

    async def conv_report_received_message(self, update: Update, context: CallbackContext):
        message=update.message.text
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        r=context.user_data["report"]
        r.report_set_staff_message(message)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("✅ *Message sent successfully!*"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        self.report_manager.report_add_data(r)
        await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown(r.report_to_string()), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
        )
        message = await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="_Select an operation from the buttons:_", 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_from_list(extract_list_of_single_report_operations(self.user_manager.user_allowed_roles(role)))
            )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = SINGLE_REPORT_MENU

    async def conv_report_view_reports_user(self, update: Update, context: CallbackContext):
        user_id=self.user_manager.user_get_id(update.effective_user.id)
        role=self.user_manager.user_get_role(user_id)
        report_list = self.report_manager.report_list_for_user(user_id)
        if not report_list :
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown("_No reports available._"), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=_escape_markdown(self.report_manager.report_list_to_string(report_list)), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
            self.report_manager.report_mark_reports(report_list,VIEWED)
        await self.conv_report_menu(update, context)
