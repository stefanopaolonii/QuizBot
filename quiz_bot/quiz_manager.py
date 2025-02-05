# quiz_manager.py

from typing import Dict, Tuple, Optional, List

from quiz_bot.question import Question
from utils.json_loader import JSONQuestionsLoader
import random

class QuizManager:
    """
    Manages the question database and the logic for verifying answers.
    """
    # Inizialization of the QuizManager class
    def __init__(self, json_path: str):
        loader = JSONQuestionsLoader()
        self.questions_db: Dict[int, Question] = loader.load_from_file(json_path)
    
# Methods to get the number of questions
    def get_number_of_questions(self, topic=None, language=None) -> int:
        if topic is None and language is None: 
            return len(self.questions_db)
        elif topic is None and language is not None:
            return sum(1 for question in self.questions_db.values() if question.language.lower() == language.lower())
        elif topic is not None and language is None:
            return sum(1 for question in self.questions_db.values() if question.topic.lower() == topic.lower())
        else: 
            return sum(1 for question in self.questions_db.values() if question.topic.lower() == topic.lower() and question.language.lower() == language.lower())

# Methods to get the random questions
    def pick_questions(self, n: int, excludet=None, excludel=None) -> list:
        if excludet is None:
            excludet = []
        if excludel is None:
            excludel = []
        available_questions = [k for k, question in self.questions_db.items() 
                               if question.id not in excludet 
                               and question.id not in excludel]
        random.seed()
        random.shuffle(available_questions)
        return random.sample(available_questions, min(n, len(available_questions)))

# Methods to check the answer
    def check_answer(self, question_id: int, answer_index: int, scramble_map: dict) -> bool:
        question = self.questions_db.get(question_id)
        ans = answer_index
        if scramble_map:
            ans = scramble_map.get(answer_index)
        return question and question.correct_index == ans
    
# Methods to get the question data
    def get_question_data(self, question_id: int) -> Question:
        return self.questions_db.get(question_id)

# Methods to add a question
    def add_question_data(self, question: Question):
        self.questions_db[len(self.questions_db)] = question

# Methods to get the question by id
    def get_question_index_by_id(self, question_id: int) -> Optional[int]:
        for i, question in self.questions_db.items():
            if question.id == question_id:
                return i
        return None

# Methods to get list of topics 
    def extract_list_of_all_topics(self) -> list:
        return list({question.topic.lower() for question in self.questions_db.values()})
        
# Methods to get list of languages
    def extract_list_of_all_languages(self) -> list:
        languages_list=list({question.language.lower() for question in self.questions_db.values()})
        return languages_list
    
# Methods to get questiens id not related to selected topic 
    def exclude_questions_not_related_to_selected_topic(self, topic: str) -> list:
        return [question.id for question in self.questions_db.values() if question.topic.lower() != topic.lower()]
    
# Methods to get questiens id not related to selected language
    def exclude_questions_not_related_to_selected_language(self, language: str) -> list:
        return [question.id for question in self.questions_db.values() if question.language.lower() != language.lower()]
    
# Methods to save the dictionary to json
    def save_dictioanry_to_json(self, path: str):
        loader = JSONQuestionsLoader()
        loader.save_to_file(path, self.questions_db)