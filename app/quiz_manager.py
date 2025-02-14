# app/quiz_manager.py

from typing import Dict, List
from .question import Question
from utils import QuestionsLoader
from app import set_last_question_id, correct_answer_weight, wrong_answer_weight
import random

class QuizManager:
    
    def __init__(self, questions_json_pat: str,logger):
        self.question_loader = QuestionsLoader(logger)
        self.questions_db: Dict[int, Question] = self.question_loader.load_from_file(questions_json_pat)
        set_last_question_id(max(self.questions_db.keys(), default=0))
        self.logger = logger
        self.question_file=questions_json_pat
        
    def get_number_of_questions(self, topic=None, language=None) -> int:
        if topic is None and language is None: 
            return len(self.questions_db)
        elif topic is None and language is not None:
            return sum(1 for question in self.questions_db.values() if question.language.lower() == language.lower())
        elif topic is not None and language is None:
            return sum(1 for question in self.questions_db.values() if question.topic.lower() == topic.lower())
        else: 
            return sum(1 for question in self.questions_db.values() if question.topic.lower() == topic.lower() and question.language.lower() == language.lower())

    def pick_questions(self, n: int, excludet=None, excludel=None) -> list:
        if excludet is None:
            excludet = []
        if excludel is None:
            excludel = []
        available_questions = [q_id for q_id in self.questions_db.keys()
                               if q_id not in excludet 
                               and q_id not in excludel]
        random.seed()
        random.shuffle(available_questions)
        return random.sample(available_questions, min(n, len(available_questions)))

    def check_answer(self, question_id: int, answer_index: int, scramble_map: dict) -> bool:
        question = self.questions_db.get(question_id)
        ans = answer_index
        if scramble_map:
            ans = scramble_map.get(answer_index)
        return question and question.correct_index == ans
    
    def get_question_data(self, question_id: int) -> Question:
        return self.questions_db.get(question_id, None)

    def add_question_data(self,question: Question):
        self.questions_db[question.id] = question
        self.save_dictioanry_to_json(self.question_file)

    def extract_list_of_all_topics(self) -> list:
        return list({question.topic.lower() for question in self.questions_db.values()})
        
    def extract_list_of_all_languages(self) -> list:
        languages_list=list({question.language.lower() for question in self.questions_db.values()})
        return languages_list
    
    def exclude_questions_not_related_to_selected_topic(self, topic: str) -> list:
        return [question.id for question in self.questions_db.values() if question.topic.lower() != topic.lower()]
    
    def exclude_questions_not_related_to_selected_language(self, language: str) -> list:
        return [question.id for question in self.questions_db.values() if question.language.lower() != language.lower()]
    
    def save_dictioanry_to_json(self, path: str):
        print("OK savedict")
        self.question_loader.save_to_file(path, self.questions_db)

    def quiz_delete_question(self, question_id: int):
        print("OK delete")
        self.questions_db.pop(question_id, None)
        print("OK delete2")
        self.save_dictioanry_to_json(self.question_file)

    def quiz_score(self, correct: int, wrong: int):
        score = wrong*(-wrong_answer_weight) + correct*(correct_answer_weight)
        return score

    def scramble_options(self, options: List[str]) -> Dict[int, int]:
        scrambled_map = {}
        available_indices = list(range(len(options)))
        for i in range(len(options)):
            random_index = random.choice(available_indices)
            scrambled_map[i] = random_index
            available_indices.remove(random_index)
        return scrambled_map