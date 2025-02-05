import datetime
import random
import asyncio
from telegram import Update
from telegram.error import TimedOut
from telegram.ext import Application, CallbackContext, PicklePersistence, CommandHandler, MessageHandler, filters
from .quiz_manager import QuizManager
from .handlers import (
    make_keyboard_from_list, get_main_menu_keyboard, make_keybord_for_choice, 
    make_keyboard_for_question, make_keyboard_for_topics, SELECTING_ACTION, 
    IFLANGUAGE, SELECT_LANGUAGE, IFTOPIC, SELECT_TOPIC, IFNUMBERQUESTION,
    SELECT_CUSTOM_NQUESTION, SELECT_NUMQUESTION, ANSWERING_QUESTION, QUESTION_TEXT, 
    OPTIONS, CORRECT_OPTION, EXPLANATION, TOPICQ, LANGUAGE, CONFIRMATION, REVIEW, 
    CHANGE_QUESTION, CUSTOM_CHANGING, CHANGING_CORRECT_ANSWER, CHANGING_EXPLANETION,
    CHANGING_TOPIC, CHANGING_LANGUAGE
)
from quiz_bot.question import Question

class QuizBot:
   
# Functions for the bot runner
    def __init__(self, token, questions_json_path,allowed_user_ids):
        self.token = token
        self.quiz_manager = QuizManager(questions_json_path)
        self.persistence = PicklePersistence('quiz_bot_data.pkl')
        self.allowed_user_ids = allowed_user_ids
        self.application = Application.builder().token(self.token).persistence(self.persistence).build()

    def start_bot(self):
        """
        Start the bot and register the handlers.
        """
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] Starting the bot ...")
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("cancel", self.start_command))
        self.application.add_handler(CommandHandler("quiz", self.quiz_command))
        self.application.add_handler(CommandHandler("review", self.review_command))
        self.application.add_handler(CommandHandler("addq", self.addq_command))
        self.application.add_handler(CommandHandler("cq", self.cq_command))
        self.application.add_handler(CommandHandler("restart", self.restart_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.make_conversation))
        self.application.run_polling()

# Functions for the main conversation

    async def make_conversation(self, update: Update, context: CallbackContext):
        """
        Control user flow.
        """
        state = context.user_data.get("state", SELECTING_ACTION)

        if state == SELECTING_ACTION:
            if update.message.text == "Start Quiz":
                await self.start_quiz(update, context)
            elif update.message.text == "Add Question":
                await self.start_add_question(update, context)
            elif update.message.text == "Review Question":
                await self.handle_review(update, context)
            elif update.message.text == "Change Question":
                await self.change_question(update, context)
            else :
                await self.restart_command(update, context)

        if update.message.text == "Cancel":
            await self.restart_command(update, context)
        else:
            if state == IFLANGUAGE:
                await self.handle_if_language_selection(update, context)
            elif state == SELECT_LANGUAGE:
                await self.handle_language_selection(update, context)
            elif state == IFTOPIC:
                await self.handle_if_topic_selection(update, context)
            elif state == SELECT_TOPIC:
                await self.handle_topic_selection(update, context)
            elif state == SELECT_CUSTOM_NQUESTION:
                await self.handle_custom_num_questions(update, context)
            elif state == SELECT_NUMQUESTION:
                await self.handle_num_questions(update, context)
            elif state == ANSWERING_QUESTION:
                await self.handle_quiz_answer(update, context)
            elif state == QUESTION_TEXT:
                await self.handle_question_text(update, context)
            elif state == OPTIONS:
                await self.handle_options(update, context)
            elif state == CORRECT_OPTION:
                await self.handle_correct_option(update, context)
            elif state == EXPLANATION:
                await self.handle_explanetion(update, context)
            elif state == TOPICQ:
                await self.handle_topic(update, context)
            elif state == LANGUAGE:
                await self.handle_language(update, context)
            elif state == CONFIRMATION:
                await self.handle_confirmation(update, context)
            elif state == REVIEW:
                await self.get_question(update, context)
            elif state == CHANGE_QUESTION:
                await self.handle_question_id(update, context)
            elif state == CUSTOM_CHANGING:
                if update.message.text == "Correct Answer":
                    await self.handle_correct_answer_changing(update, context)
                elif update.message.text == "Explanation":
                    await self.handle_explanetion_changing(update, context)
                elif update.message.text == "Topic":
                    await self.handle_topic_changing(update, context)
                elif update.message.text == "Language":
                    await self.handle_language_changing(update, context)
                elif update.message.text == "Nothing":
                    await self.send_question_details(update, context)
            elif state == CHANGING_CORRECT_ANSWER:
                await self.change_correct_answer(update, context)
            elif state == CHANGING_EXPLANETION:
                await self.change_explanation(update, context)
            elif state == CHANGING_TOPIC:
                await self.change_topic(update, context)
            elif state == CHANGING_LANGUAGE:
                await self.change_language(update, context)
            
    async def start_command(self, update: Update, context: CallbackContext):
        """
        Welcome message with dynamic keyboard, but only if the user is authorized.
        """
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) issued the /start command.")
        context.user_data.clear()
        # Continua se l'utente è autorizzato
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Choose an option from the keyboard to get started!",
            reply_markup=get_main_menu_keyboard()
        )
        context.user_data["state"] = SELECTING_ACTION

    async def restart_command(self, update: Update, context: CallbackContext):
        """
        Restarts the bot and returns to the main menu.
        """
        # Continue if the user is authorized
        context.user_data.clear()
        context.user_data["state"] = SELECTING_ACTION
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Choose an option from the keyboard!",
            reply_markup=get_main_menu_keyboard()
        )
        
    async def quiz_command(self, update: Update, context: CallbackContext):
        """
        Handling the quiz command.
        """
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) issued the /quiz command.")
        context.user_data.clear()
        await self.start_quiz(update, context)

    async def review_command(self, update: Update, context: CallbackContext):
        """
        Handling the review command.
        """
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) issued the /review command.")
        context.user_data.clear()
        await self.handle_review(update, context)

    async def addq_command(self, update: Update, context: CallbackContext):
        """
        Handling the add question command.
        """
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) issued the /addq command.")
        context.user_data.clear()
        await self.start_add_question(update, context)

    async def cq_command(self, update: Update, context: CallbackContext):
        """
        Handling the change question command.
        """
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) issued the /cq command.")
        context.user_data.clear()
        await self.change_question(update, context)

# Functions for the Quiz conversation

    async def start_quiz(self, update: Update, context: CallbackContext):
        """
        Start a new quiz for the user.
        """    
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) started a quiz.")
        await update.message.reply_text("Do you want to choose a language?", reply_markup=make_keybord_for_choice())
        context.user_data["state"] = IFLANGUAGE
    
    async def handle_if_language_selection(self, update: Update, context: CallbackContext):
        """
        Select the language for the quiz, if the user wants.
        """
        action = update.message.text.lower()
        if action == "yes":
            context.user_data["custom_language"] = True
            await update.message.reply_text("Select your language from the keyboard ", reply_markup=make_keyboard_from_list(self.quiz_manager.extract_list_of_all_languages()))
            context.user_data["state"] = SELECT_LANGUAGE
        elif action == "no":
            context.user_data["custom_language"] = False
            await update.message.reply_text("Do you want to select a specific topic? ", reply_markup=make_keybord_for_choice()) 
            context.user_data["state"] = IFTOPIC
        else:
            await update.message.reply_text("Please select Yes or No", reply_markup=make_keybord_for_choice())
        
    async def handle_language_selection(self, update: Update, context: CallbackContext):
        """
        Handle the language selection.
        """
        selected_language = update.message.text.lower()
        list_languages = self.quiz_manager.extract_list_of_all_languages()
        if selected_language in list_languages:
            context.user_data["selected_language"] = selected_language
            await update.message.reply_text("Do you want to select a specific topic? ", reply_markup=make_keybord_for_choice()) 
            context.user_data["state"] = IFTOPIC
        else:
            await update.message.reply_text("Select your language from the keyboard ", reply_markup=make_keyboard_from_list(list_languages))
        
    async def handle_if_topic_selection(self, update: Update, context: CallbackContext):
        """
        Handle the topic selection.
        """
        action = update.message.text.lower()
        if action == "yes":
            context.user_data["custom_topic"] = True
            await update.message.reply_text("Select your topic from the keyboard ", reply_markup=make_keyboard_for_topics(self.quiz_manager.extract_list_of_all_topics()))
            context.user_data["state"] = SELECT_TOPIC
        elif action == "no":
            context.user_data["custom_topic"] = False
            await update.message.reply_text("Do you want to select the questions number?", reply_markup=make_keybord_for_choice())
            context.user_data["state"] = SELECT_CUSTOM_NQUESTION
        else:
            await update.message.reply_text("Please select Yes or No", reply_markup=make_keybord_for_choice())

    async def handle_topic_selection(self, update: Update, context: CallbackContext):
        """
        Handle the topic selection.
        """
        selected_topic = update.message.text.lower()
        list_topics = self.quiz_manager.extract_list_of_all_topics()
        if selected_topic in list_topics:
            context.user_data["selected_topic"] = selected_topic
            await update.message.reply_text("Do you want to select the questions number?", reply_markup=make_keybord_for_choice())
            context.user_data["state"] = SELECT_CUSTOM_NQUESTION
        else:
            await update.message.reply_text("Select your topic from the keyboard ", reply_markup=make_keyboard_for_topics(list_topics))
        
    async def handle_custom_num_questions(self, update: Update, context: CallbackContext):
        """
        Handle the custom number of questions selection.
        """
        action = update.message.text.lower()
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
            await update.message.reply_text("Insert the number of questions (1 - " + str(maxnumber) + "):")
            context.user_data["state"] = SELECT_NUMQUESTION
        elif action == "no":
            context.user_data["custom_number"] = False
            await self.handle_start_quiz(update, context, 33)
            context.user_data["state"] = ANSWERING_QUESTION
        else:
            await update.message.reply_text("Please select Yes or No", reply_markup=make_keybord_for_choice())
        
    async def handle_num_questions(self, update: Update, context: CallbackContext):
        """
        Handle the number of questions selection.
        """
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
                await self.handle_start_quiz(update, context, num)
                context.user_data["state"] = ANSWERING_QUESTION
            else:
                await update.message.reply_text(f"Number out of range (1 - {maxnumber}). Try again.")
        except ValueError:
            await update.message.reply_text("Please insert a valid number.")
        
    async def handle_start_quiz(self, update: Update, context: CallbackContext, n_questions: int):
        """
        Start the quiz for the user with the specified number of questions and topic.
        """
        selected_topic = context.user_data.get("selected_topic")
        selected_language = context.user_data.get("selected_language")
        excluded_keys_t = None
        excluded_keys_l = None
        if selected_topic:
            excluded_keys_t = self.quiz_manager.exclude_questions_not_related_to_selected_topic(selected_topic)
        if selected_language:
            excluded_keys_l = self.quiz_manager.exclude_questions_not_related_to_selected_language(selected_language)
        
        questions_ids = self.quiz_manager.pick_questions(n_questions, excluded_keys_t, excluded_keys_l)

        
        context.user_data["quiz"] = {
            "questions_ids": questions_ids,
            "current_question_scramble_map": {},
            "current_index": 0,
            "correct_count": 0,
            "wrong_count" : 0
        }
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) started a quiz with {n_questions} questions. Selected {len(questions_ids)} questions.")
        await self.handle_send_question(update, context)

    async def handle_send_question(self, update: Update, context: CallbackContext):
        """
        Send the current question to the user.
        """
        user_quiz = context.user_data["quiz"]
        idx = user_quiz["current_index"]
        q_ids = user_quiz["questions_ids"]

        if idx >= len(q_ids):
            # Quiz terminato
            await self.finish_quiz(update, context)
            return

        q_id = q_ids[idx]
        q = self.quiz_manager.get_question_data(q_id)
        text = q.text
        scrambled_options_map = user_quiz["current_question_scramble_map"]
        if not scrambled_options_map:
            scrambled_options_map = {}
        scrambled_options_map.clear()
        answers_set = [i for i in range(len(q.options))]
        cnt = 0
        while cnt < len(q.options):
            i = random.randint(0, len(answers_set)-1)
            val = answers_set.pop(i)
            scrambled_options_map[cnt] = val
            cnt += 1
        user_quiz["current_question_scramble_map"] = scrambled_options_map
        options = [q.options[scrambled_options_map[i]] for i in range(len(q.options))]
        text = f"Question {idx + 1}/{len(q_ids)}\n\n{text}"
        msg = f"*{text}*\n\n" + "\n\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)]) + f"\n\n_Question ID: {q.id}_"

        # Usa send_message invece di reply_text
        await context.bot.send_message(
            chat_id=update.effective_chat.id,  # Usa l'ID della chat dell'utente
            text=msg, 
            parse_mode="Markdown", 
            reply_markup=make_keyboard_for_question(len(options))
        )

    async def handle_quiz_answer(self, update: Update, context: CallbackContext):
        """
        Handles the user's response during the quiz.
        """
        action = update.message.text
        user_quiz = context.user_data.get("quiz")

        if action == "Skip":
            user_quiz["current_index"] += 1
        else:
            ans = update.message.text.upper()
            idx = user_quiz["current_index"]
            q_id = user_quiz["questions_ids"][idx]

            chosen_option = ord(ans) - ord('A')
            q = self.quiz_manager.get_question_data(q_id)

            if chosen_option < 0 or chosen_option >= len(q.options):
                msg = "Opzione non valida. Riprova!"
            else:
                is_correct = self.quiz_manager.check_answer(q_id, chosen_option, user_quiz["current_question_scramble_map"])
                correct = next(fake_idx for fake_idx, real_idx in user_quiz["current_question_scramble_map"].items() if real_idx == q.correct_index)
                if is_correct:
                    user_quiz["correct_count"] += 1
                    msg = "✅ *Correct answer!*"
                else:
                    user_quiz["wrong_count"] += 1
                    msg = f"❌ *Wrong answer!*\n\nCorrect answer: ||{chr(correct + ord('A'))}||"
                if "None" not in q.explanation:
                    msg += f"\n\n_Comment: {q.explanation}\nVerified : {q.verified}_"
                else:
                    msg += f"\n\n_Comment not available.\nVerified : {q.verified} _"

            # Aggiungi il timestamp per il log
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) responded to question ID {q_id} with option {chr(chosen_option + ord('A'))}. Correct option: {chr(correct + ord('A'))}")
            
            msg = self._escape_markdown(msg)

            # Invio del messaggio con retry in caso di timeout usando send_message
            for _ in range(3):
                try:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
                    break
                except TimedOut:
                    current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    print(f"[{current_time}] User {update.effective_user.id} {update.effective_user.username} timed out ... Retrying {3 - _} more times.")
                    await asyncio.sleep(0.1)

            # Incremento dell'indice per la domanda successiva
            user_quiz["current_index"] += 1

            # Invio della prossima domanda con retry in caso di timeout
        await self.handle_send_question(update, context)

    def handle_score(self, numOfCorrect, numOfWrong):
        score = numOfWrong*(-0.33) + numOfCorrect*(1)
        return score

    async def finish_quiz(self, update: Update, context: CallbackContext):
        """
        Finish the quiz, show the summary, and return to the main menu.
        """
        user_quiz = context.user_data.get("quiz", {})
        correct = user_quiz.get("correct_count", 0)
        wrong = user_quiz.get("wrong_count", 0)
        total = len(user_quiz.get("questions_ids", []))

        score = self.handle_score(numOfCorrect=correct, numOfWrong=wrong)
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} {update.effective_user.username} finished the quiz. Correct: {correct}/{total}")
        await update.message.reply_text(
            f"🏁 Quiz finished!\n\n"
            f"✅ Correct answers: {correct}/{total}\n\n"
            f"👉 Final score: {score:.2f}")
        await self.restart_command(update, context)

# Functions for adding questions

    async def start_add_question(self, update: Update, context: CallbackContext):
        """
         Start the process of adding a new question.
        """
        user_id = update.effective_user.id
        if user_id not in self.allowed_user_ids:
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{current_time}] Unauthorized access attempt by user {update.effective_user.id} ({update.effective_user.username}) to add a question.")
            await update.message.reply_text("You are not authorized to add questions")
            await self.restart_command(update, context)
        
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] Authorized user {update.effective_user.id} ({update.effective_user.username}) started adding a new question.")
        context.user_data["new_question"] = {}
        msg="_Please provide only the question text:_"
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = QUESTION_TEXT

    async def handle_question_text(self, update: Update, context: CallbackContext):
        """
        Receive the question text from the user.
        """
        context.user_data["new_question"]["text"] = update.message.text
        msg="_Please provide the options for the question. In the format: option1;option2;option3 ... _"
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = OPTIONS

    async def handle_options(self, update: Update, context: CallbackContext):
        """
        Receive the options from the user.
        """
        context.user_data["new_question"]["options"] = update.message.text.split(";")
        msg="_Please provide the correct option._"
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = CORRECT_OPTION
    
    async def handle_correct_option(self, update: Update, context: CallbackContext):
        """
        Receive the correct option from the user.
        """
        context.user_data["new_question"]["correct_option"] = ord(update.message.text.upper()) - ord('A')
        msg="_Please provide the explanation for the question:_"
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = EXPLANATION

    async def handle_explanetion(self, update: Update, context: CallbackContext):
        """
        Receive the explanation from the user.
        """
        context.user_data["new_question"]["explanation"] = update.message.text
        topic_list = self.quiz_manager.extract_list_of_all_topics()
        msg="_Please provide the topic for the question.\nChose one of the following topics or create a new one:_ \n\n" + "\n".join(topic_list)
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = TOPICQ

    async def handle_topic(self, update: Update, context: CallbackContext):
        """
        Receive the topic from the user.
        """
        context.user_data["new_question"]["topic"] = update.message.text
        language_list = self.quiz_manager.extract_list_of_all_languages()
        msg="_Please provide the language for the question.\nChose one of the following languages or create a new one:_ \n\n" + "\n".join(language_list)
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = LANGUAGE

    async def handle_language(self, update: Update, context: CallbackContext):
        """
        Receive the language from the user.
        """
        context.user_data["new_question"]["language"] = update.message.text.lower()

        new_question = context.user_data["new_question"]
        msg = (
            f"*Review the question details:*\n\n"
            f"*Question:* {new_question['text']}\n"
            f"*Options:*\n" +
            "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(new_question['options'])]) +
            f"\n*Correct Option:* {chr(new_question['correct_option'] + ord('A'))}\n"
            f"*Explanation:* {new_question['explanation']}\n"
            f"*Topic:* {new_question['topic']}\n"
            f"*Language:* {new_question['language']}\n"
            f"\n_Do you want to add this question? Select Yes or No_"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,  # Usa l'ID della chat dell'utente
            text=self._escape_markdown(msg), 
            parse_mode="MarkdownV2", 
            reply_markup=make_keybord_for_choice()
        )
        context.user_data["state"] = CONFIRMATION

    async def handle_confirmation(self, update: Update, context: CallbackContext):
        """
        Confirm the question and add it to the database.
        """
        action = update.message.text.lower()
        q=Question(context.user_data["new_question"]["text"], context.user_data["new_question"]["options"], context.user_data["new_question"]["correct_option"], False, context.user_data["new_question"]["explanation"], context.user_data["new_question"]["topic"],len(self.quiz_manager.questions_db),context.user_data["new_question"]["language"])
        if action == "yes":
            # Add the question to the database
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{current_time}] Authorized user {update.effective_user.id} ({update.effective_user.username}) added a new question with ID {q.id}.")
            self.quiz_manager.add_question_data(q)
            self.quiz_manager.save_dictioanry_to_json("questions.json")
            await update.message.reply_text("Question added successfully!")
        elif action == "no":
            await update.message.reply_text("Question not added.")
        else:
            await update.message.reply_text("Please select Yes or No", reply_markup=make_keybord_for_choice())
        await self.restart_command(update, context)

# Functions for changing questions details

    async def change_question(self, update: Update, context: CallbackContext):
        """
         Handling the change of a question.
        """
        if update.effective_user.id not in self.allowed_user_ids:
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{current_time}] Unauthorized access attempt by user {update.effective_user.id} ({update.effective_user.username}) to change a question.")
            await update.message.reply_text("You are not authorized to change questions")
            await self.restart_command(update, context)
        
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] Authorized user {update.effective_user.id} ({update.effective_user.username}) started changing a question.")
        context.user_data["changing_question"] = {}
        msg="_Please provide the ID of the question you want to change:_"
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = CHANGE_QUESTION

    async def handle_question_id(self, update: Update, context: CallbackContext):
        """
         Handle the question ID from the user.
        """
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) requested question ID {update.message.text}")
        try:
            q_id = int(update.message.text)
            index = self.quiz_manager.get_question_index_by_id(q_id)
            if index is None:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid question ID.")
                return
            q = self.quiz_manager.get_question_data(q_id)
            context.user_data["changing_question"] = q
            msg = (
                f"*Review the question details:*\n\n"
                f"*Question:* {q.text}\n"
                f"*Options:*\n" +
                "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(q.options)]) +
                f"\n*Correct Option:* {chr(q.correct_index + ord('A'))}\n"
                f"*Explanation:* {q.explanation}\n"
                f"*Topic:* {q.topic}\n"
                f"*Language:* {q.language}\n"
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,  # Usa l'ID della chat dell'utente
                text=self._escape_markdown(msg), 
                parse_mode="MarkdownV2", 
                reply_markup=make_keybord_for_choice()
            )
            await context.bot.send_message(chat_id=update.effective_chat.id, text="What do you want to change?", reply_markup=make_keyboard_from_list(["Correct Answer", "Explanation", "Topic", "Language","Nothing"]))
            context.user_data["state"] = CUSTOM_CHANGING
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid question ID. Please try again.")

    async def handle_correct_answer_changing(self, update: Update, context: CallbackContext):
        """
        Handle the changing of the correct answer.
        """
        q=context.user_data["changing_question"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Insert the new correct answer.", reply_markup=make_keyboard_for_question(len(q.options)))
        context.user_data["state"] = CHANGING_CORRECT_ANSWER

    async def change_correct_answer(self, update: Update, context: CallbackContext):
        """
        Change correct answer.
        """
        try:
            new_correct_option = ord(update.message.text.upper()) - ord('A')
            q=context.user_data["changing_question"]
            q.correct_index = new_correct_option
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) changed the correct answer of question ID {q.id} to option {chr(new_correct_option + ord('A'))}")
            self.quiz_manager.questions_db[q.id] = q
            self.quiz_manager.save_dictioanry_to_json("questions.json")
            await update.message.reply_text("Correct answer changed successfully!")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="What do you want to change?", reply_markup=make_keyboard_from_list(["Correct Answer", "Explanation", "Topic", "Language","Nothing"]))
            context.user_data["state"] = CUSTOM_CHANGING
        except ValueError:
            await update.message.reply_text("Invalid option. Please try again.")

    async def handle_explanetion_changing(self, update: Update, context: CallbackContext):
        """
        Handle the changing of the explanation.
        """
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Insert the new explanation.")
        context.user_data["state"] = CHANGING_EXPLANETION

    async def change_explanation(self, update: Update, context: CallbackContext):
        """
        Change the explanation.
        """
        q=context.user_data["changing_question"]
        q.explanation = update.message.text
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) changed the explanation of question ID {q.id}. New explanation: {update.message.text}")
        self.quiz_manager.questions_db[q.id] = q
        self.quiz_manager.save_dictioanry_to_json("questions.json")
        await update.message.reply_text("Explanation changed successfully!")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="What do you want to change?", reply_markup=make_keyboard_from_list(["Correct Answer", "Explanation", "Topic", "Language","Nothing"]))
        context.user_data["state"] = CUSTOM_CHANGING
    
    async def handle_topic_changing(self, update: Update, context: CallbackContext):
        """
        Handle the changing of the topic.
        """
        topic_list = self.quiz_manager.extract_list_of_all_topics()
        msg="_Please provide the new topic for the question.\nChose one of the following topics or create a new one:_ \n\n" + "\n".join(topic_list)
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = CHANGING_TOPIC
    
    async def change_topic(self, update: Update, context: CallbackContext):
        """
        Change the topic.
        """
        q=context.user_data["changing_question"]
        q.topic = update.message.text
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) changed the topic of question ID {q.id} to {q.topic}")
        self.quiz_manager.questions_db[q.id] = q
        self.quiz_manager.save_dictioanry_to_json("questions.json")
        await update.message.reply_text("Topic changed successfully!")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="What do you want to change?", reply_markup=make_keyboard_from_list(["Correct Answer", "Explanation", "Topic", "Language","Nothing"]))
        context.user_data["state"] = CUSTOM_CHANGING

    async def handle_language_changing(self, update: Update, context: CallbackContext):
        """
        Handle the changing of the language.
        """
        language_list = self.quiz_manager.extract_list_of_all_languages()
        msg="_Please provide the new language for the question.\nChoose one of the following languages or create a new one:_ \n\n" + "\n".join(language_list)
        msg=self._escape_markdown(msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
        context.user_data["state"] = CHANGING_LANGUAGE
    
    async def change_language(self, update: Update, context: CallbackContext):
        """
        Change the language.
        """
        q=context.user_data["changing_question"]
        q.language = update.message.text.lower()
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) changed the language of question ID {q.id} to {q.language}")
        self.quiz_manager.questions_db[q.id] = q
        self.quiz_manager.save_dictioanry_to_json("questions.json")
        await update.message.reply_text("Language changed successfully!")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="What do you want to change?", reply_markup=make_keyboard_from_list(["Correct Answer", "Explanation", "Topic", "Language","Nothing"]))
        context.user_data["state"] = CUSTOM_CHANGING
   
    async def send_question_details(self, update: Update, context: CallbackContext):
        """
        Send the question details to the user.
        """
        q=context.user_data["changing_question"]
        msg = (
            f"*Review the question details:*\n\n"
            f"*Question:* {q.text}\n"
            f"*Options:*\n" +
            "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(q.options)]) +
            f"\n*Correct Option:* {chr(q.correct_index + ord('A'))}\n"
            f"*Explanation:* {q.explanation}\n"
            f"*Topic:* {q.topic}\n"
            f"*Language:* {q.language}\n"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,  # Use the user's chat ID
            text=self._escape_markdown(msg), 
            parse_mode="MarkdownV2", 
        )
        await self.restart_command(update, context)
   # Function for review questions

    async def handle_review(self, update: Update, context: CallbackContext):
        """
        Handle the review of a question.
        """
        await update.message.reply_text("Insert the ID of the question you want to review.")
        context.user_data["state"] = REVIEW

    async def get_question(self, update: Update, context: CallbackContext):
        """
        Respond to the user when the /review command is issued.
        """
        try:
            question_number = int(update.message.text)
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) requested review for question ID {question_number}")

            index = self.quiz_manager.get_question_index_by_id(question_number)
            if index is None:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Question not found.")
                return
            q = self.quiz_manager.get_question_data(index)

            msg = (
                f"Question ID: {q.id}\n"
                f"{q.text}\n\n" +
                "\n\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(q.options)]) +
                f"\n\nAnswer: ||{chr(q.correct_index + ord('A'))}||" +
                f"\nComment: ||{q.explanation}||"
            )

            msg = self._escape_markdown(msg)
            
            # Send the message with retry in case of timeout using send_message
            for _ in range(3):
                try:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2")
                    break
                except TimedOut:
                    current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    print(f"[{current_time}] User {update.effective_user.id} ({update.effective_user.username}) timed out while reviewing question ID {question_number}. Retrying {3 - _} more times.")
                    await asyncio.sleep(0.2)

        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid question number.")
        await self.restart_command(update, context)

# Functions for character escaping

    def _escape_markdown(self, text: str) -> str:
        escape_chars = r'\[]()~`>#+-={}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)