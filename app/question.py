# app/question.py

class Question:
    
    def __init__(self, text: str, options: list, correct_index: int, verified: bool, explanation: str, topic: str, id : int, language : str):
        self.text = text
        self.options = options
        self.correct_index = correct_index
        self.verified = verified
        self.explanation = explanation
        self.topic = topic
        self.id=id
        self.language=language

    def question_to_string(self, scramble_option_map: dict=None) -> str:
        if scramble_option_map:
            options = [self.options[scramble_option_map.get(i, i)] for i in range(len(self.options))]
        return f"*{self.text}* \n\n" + "\n".join([f"{chr(65+i)} - {options[i]}" for i in range(len(options))]) + f"\n\n_Question ID: {self.id}_"
    
    def question_details_to_string(self) -> str:
        return f"_Question ID : {self.id}_\n\n*{self.text}* \n\n" + "\n".join([f"{chr(65+i)} - {self.options[i]}" for i in range(len(self.options))]) + f"\n\n*Correct Answer:* {chr(65+self.correct_index)}\n*Explanation:* {self.explanation}\n*Topic:* {self.topic}\n*Language:* {self.language}"
    
    def question_to_string_for_review(self) -> str:
        return  f"*{self.text}* \n\n" + "\n".join([f"{chr(65+i)} - {self.options[i]}" for i in range(len(self.options))]) + f"\n\n_Question ID: {self.id} _" + f"\n\n*Correct Answer:* ||{chr(65+self.correct_index)}|| \n*Explanation:* ||{self.explanation}|| \n"