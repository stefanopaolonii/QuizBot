# app/bot_runner.py
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackContext, PicklePersistence, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from .quiz_manager import QuizManager
from .question import Question
from app import main_menu_text, get_next_question_id
from config import LANGUAGE_SELECTION, TOPIC_SELECTION, QUESTION_NUMBER_SELECTION, CORRECT_ANSWER_WEIGHT, WRONG_ANSWER_WEIGHT, DEFAULT_NUMBER_OF_QUESTIONS
from .handlers import (State,
    make_inline_keyboard_for_choice, make_inline_keyboard_for_question_quiz,
    _escape_markdown, make_inline_keyboard_from_list, make_inline_keyboard_for_list,
    extract_list_of_main_operations,
    CALLBACK_YES, CALLBACK_NO, CALLBACK_SKIP, CALLBACK_MAIN_MENU
)
import random, time


class QuizBot:
   
    def __init__(self, token, questions_json_path, logger):
        self.token = token
        self.quiz_manager = QuizManager(questions_json_path,logger)
        self.persistence = PicklePersistence('quiz_bot_data.pkl')
        self.application = Application.builder().token(self.token).persistence(self.persistence).build()
        self.logger = logger
        self.state_handlers = {
            State.SELECT_LANGUAGE: self.conv_quiz_selected_language,
            State.SELECT_TOPIC: self.conv_quiz_selected_topic,
            State.ANSWERING_QUESTION: self.conv_quiz_answer,
            State.IF_LANGUAGE: self.conv_quiz_language_selection,
            State.IF_TOPIC: self.conv_quiz_topic_selection,
            State.SELECT_CUSTOM_NQUESTION: self.conv_quiz_questions_selection,
        }

    def start_bot(self):
        self.application.add_handler(CommandHandler("start", self.command_start))
        self.application.add_handler(CommandHandler("cancel", self.command_start))
        self.application.add_handler(CommandHandler("quiz", self.command_quiz))
        self.application.add_handler(CommandHandler("review", self.command_review))
        self.application.add_handler(CommandHandler("restart", self.command_restart))
        self.application.add_handler(CallbackQueryHandler(self.button))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.make_conversation))
        self.application.run_polling()

# Functions for the main conversation

    async def button(self, update: Update, context: CallbackContext):
        query = update.callback_query
        state = context.user_data.get("state", State.SELECTING_ACTION)
        await query.answer()

        if 'last_message_id' in context.user_data:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['last_message_id'])
            del context.user_data['last_message_id']

        if query.data == CALLBACK_MAIN_MENU:
            await self.command_restart(update, context)
        elif query.data == "start_quiz":
            await self.conv_quiz_start(update, context)
        elif query.data == "review_question":
            await self.conv_review_question_start(update, context)
        else:
            handler = self.state_handlers.get(state)
            if handler:
                await handler(update, context)

    async def make_conversation(self, update: Update, context: CallbackContext):
        state = context.user_data.get("state", State.SELECTING_ACTION)
        if state in [
            State.SELECT_LANGUAGE, State.SELECT_TOPIC, 
            State.SELECT_CUSTOM_NQUESTION, State.SELECT_NUMQUESTION, 
            State.REVIEW
        ]:
            if 'last_message_id' in context.user_data:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_message_id'])
                del context.user_data['last_message_id']

        if update.message.text == "Cancel":
            await self.command_restart(update, context)
        elif state == State.SELECT_NUMQUESTION:
                await self.conv_quiz_selected_questions(update, context)
        elif state == State.REVIEW:
                await self.conv_review_question_selected_id(update, context)
            
    async def command_start(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        self.logger.info(f"Message : issued the /start command.")
        context.user_data.clear()
        message =await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown(main_menu_text),
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_from_list(extract_list_of_main_operations())
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = State.SELECTING_ACTION

    async def command_quiz(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        self.logger.info(f"Message : issued the /quiz command.")
        context.user_data.clear()
        await self.conv_quiz_start(update, context)

    async def command_review(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        self.logger.info(f"Message : issued the /review command.")
        context.user_data.clear()
        await self.conv_review_question_start(update, context)

    async def command_restart(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        self.logger.info(f"Message : issued a restart/cancel command.")
        context.user_data.clear()
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown(main_menu_text),
            parse_mode="MarkdownV2",
            reply_markup=make_inline_keyboard_from_list(extract_list_of_main_operations())
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = State.SELECTING_ACTION


# Functions for the Quiz conversation

    async def _handle_next_setup_step(self, update: Update, context: CallbackContext):
        """
        Router function to decide the next step in the quiz setup conversation.
        This centralizes the logic and avoids code duplication.
        """
        chat_id = update.effective_chat.id

        if LANGUAGE_SELECTION and "custom_language" not in context.user_data:
            message = await context.bot.send_message(
                chat_id=chat_id,
                text=_escape_markdown("_Do you want to choose a language?_"),
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_choice()
            )
            context.user_data["state"] = State.IF_LANGUAGE
            context.user_data["last_message_id"] = message.message_id
            return

        if TOPIC_SELECTION and "custom_topic" not in context.user_data:
            message = await context.bot.send_message(
                chat_id=chat_id,
                text=_escape_markdown("_Do you want to select a specific topic?_"),
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_choice()
            )
            context.user_data["state"] = State.IF_TOPIC
            context.user_data["last_message_id"] = message.message_id
            return

        if QUESTION_NUMBER_SELECTION and "custom_number" not in context.user_data:
            message = await context.bot.send_message(
                chat_id=chat_id,
                text=_escape_markdown("_Do you want to select the questions number?_"),
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_choice()
            )
            context.user_data["state"] = State.SELECT_CUSTOM_NQUESTION
            context.user_data["last_message_id"] = message.message_id
            return

        await self.conv_quiz_start_for_user(update, context, context.user_data.get("selected_n_questions", DEFAULT_NUMBER_OF_QUESTIONS))
        context.user_data["state"] = State.ANSWERING_QUESTION

    async def conv_quiz_start(self, update: Update, context: CallbackContext):  
        await self._handle_next_setup_step(update, context)
    
    async def conv_quiz_language_selection(self, update: Update, context: CallbackContext):
        query = update.callback_query
        if query.data == CALLBACK_YES:
            context.user_data["custom_language"] = True
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("_Select your language from the keyboard:_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_list(self.quiz_manager.extract_list_of_all_languages())
            )
            context.user_data["state"] = State.SELECT_LANGUAGE
            context.user_data["last_message_id"] = message.message_id
        else:
            context.user_data["custom_language"] = False
            context.user_data["selected_language"] = None
            await self._handle_next_setup_step(update, context)
        
    async def conv_quiz_selected_language(self, update: Update, context: CallbackContext):
        query = update.callback_query
        selected_language = query.data.lower()
        context.user_data["selected_language"] = selected_language
        await self._handle_next_setup_step(update, context)
        
    async def conv_quiz_topic_selection(self, update: Update, context: CallbackContext):
        query = update.callback_query
        if query.data == CALLBACK_YES:
            context.user_data["custom_topic"] = True
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("_Select your topic from the keyboard:_"), 
                parse_mode="MarkdownV2",
                reply_markup=make_inline_keyboard_for_list(self.quiz_manager.extract_list_of_all_topics())
            )
            context.user_data["state"] = State.SELECT_TOPIC
            context.user_data["last_message_id"] = message.message_id
        elif query.data == CALLBACK_NO:
            context.user_data["custom_topic"] = False
            context.user_data["selected_topic"] = None
            await self._handle_next_setup_step(update, context)

    async def conv_quiz_selected_topic(self, update: Update, context: CallbackContext):
        query = update.callback_query
        selected_topic = query.data.lower()
        context.user_data["selected_topic"] = selected_topic
        await self._handle_next_setup_step(update, context)
        
    async def conv_quiz_questions_selection(self, update: Update, context: CallbackContext):
        query = update.callback_query
        action = query.data

        if action == CALLBACK_YES:
            context.user_data["custom_number"] = True
            maxnumber = self.quiz_manager.get_number_of_questions(
                topic=context.user_data.get("selected_topic"),
                language=context.user_data.get("selected_language")
            )
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_escape_markdown("_Insert the number of questions (1 - " + str(maxnumber) + "):_"), 
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data["last_message_id"] = message.message_id
            context.user_data["state"] = State.SELECT_NUMQUESTION
        else :
            context.user_data["custom_number"] = False
            context.user_data["selected_n_questions"] = DEFAULT_NUMBER_OF_QUESTIONS
            await self._handle_next_setup_step(update, context)
        
    async def conv_quiz_selected_questions(self, update: Update, context: CallbackContext):
        try:
            num = int(update.message.text)
            maxnumber = self.quiz_manager.get_number_of_questions(
                topic=context.user_data.get("selected_topic"),
                language=context.user_data.get("selected_language")
            )

            if 1 <= num <= maxnumber:
                context.user_data["selected_n_questions"] = num
                await self.conv_quiz_start_for_user(update, context, num)
                context.user_data["state"] = State.ANSWERING_QUESTION
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
        user_id = update.effective_user.id
        selected_topic = context.user_data.get("selected_topic")
        selected_language = context.user_data.get("selected_language")
        excluded_keys_t = None
        excluded_keys_l = None
        if selected_topic:
            excluded_keys_t = self.quiz_manager.exclude_questions_not_related_to_selected_topic(selected_topic)
        if selected_language:
            excluded_keys_l = self.quiz_manager.exclude_questions_not_related_to_selected_language(selected_language)
        questions_ids = self.quiz_manager.pick_questions(n_questions, excluded_keys_t, excluded_keys_l)
        self.logger.info(f"Message : started a quiz with {len(questions_ids)} questions.")
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

        if action == CALLBACK_SKIP:
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

   # Functions for review questions

    async def conv_review_question_start(self, update: Update, context: CallbackContext):
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_escape_markdown("_Please provide the ID of the question you want to review:_"),
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data["state"] = State.REVIEW

    async def conv_review_question_selected_id(self, update: Update, context: CallbackContext):
        try:
            user_id = update.effective_user.id
            question_number = int(update.message.text)
            self.logger.info(f"Message : requested question {question_number}")
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
