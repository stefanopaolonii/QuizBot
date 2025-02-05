# json_loader.py

import json
import datetime
from typing import Dict, Any

from quiz_bot.question import Question


class JSONQuestionsLoader:

# Mwtgod to load the questions from the file
    def load_from_file(self, path: str) -> Dict[int, Question]:
        with open(path, "r", encoding="utf-8") as f:
            questions_list = json.load(f)

        questions_dict = {}
        for i, q in enumerate(questions_list):
            text = q.get("text", "Domanda non disponibile")
            options = q.get("options", [])
            correct_index = q.get("correct_index", 0)
            verified = q.get("verified", False)
            explanation = q.get("explanation", "")
            topic = q.get("topic", None)
            id=q.get("id",-1)
            language=q.get("language","it")
            q = Question(text, options, correct_index, verified, explanation, topic,id,language)
            questions_dict[i] = q
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] Loaded {len(questions_dict)} questions from {path}")
        return questions_dict
    
# Method to save the questions to the file
    def save_to_file(self, path: str, questions_dict: Dict[int, Question]):
        """
        Salva le domande nel file JSON.
        """
        # Prepara il formato dei dati da salvare
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

        # Scrivi nel file JSON
        with open(path, "w", encoding="utf-8") as f:
            json.dump(questions_list, f, ensure_ascii=False, indent=4)
        
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{current_time}] Saved {len(questions_dict)} questions to {path}")