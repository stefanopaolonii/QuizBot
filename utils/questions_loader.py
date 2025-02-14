# utils/questions_loader.py

from app.question import Question
from typing import Dict
import json, logging


class QuestionsLoader:

    def __init__(self,logger: logging.Logger):
        self.logger = logger

    def load_from_file(self, path: str) -> Dict[int, Question]:
        """
        Load questions from a JSON file.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                questions_list = json.load(f)

            questions_dict = {}
            for q in questions_list:
                text = q.get("text", "Domanda non disponibile")
                options = q.get("options", [])
                correct_index = q.get("correct_index", 0)
                verified = q.get("verified", False)
                explanation = q.get("explanation", "")
                topic = q.get("topic", None)
                id=q.get("id",-1)
                language=q.get("language","it")
                q = Question(text, options, correct_index, verified, explanation, topic,id,language)
                questions_dict[id] = q
            self.logger.info(f"Loaded {len(questions_dict)} questions from {path}")
            return questions_dict
        except FileNotFoundError:
            self.logger.error(f"File {path} not found")
            return {}
        
    
    def save_to_file(self, path: str, questions_dict: Dict[int, Question]):
        """
        Save questions to a JSON file.
        """
        questions_list = []
        for question in questions_dict.values():
            q_data = {
                "id": question.id,
                "language": question.language,
                "text": question.text,
                "options": question.options,
                "correct_index": question.correct_index,
                "verified": question.verified,
                "explanation": question.explanation,
                "topic": question.topic
            }
            questions_list.append(q_data)
        try:
            logging.info(f"Saving {len(questions_list)} questions to {path}")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(questions_list, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            self.logger.error(f"File {path} not found")
        
        
        