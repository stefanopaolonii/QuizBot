# app/report.py

NOT_TAKEN, IN_PROGRESS, COMPLETED, VIEWED = range(4)

class Report:

    def __init__(self, id: int, user_id: str, text: str,staff_message : str,status: int):
        self.id= id
        self.user_id = user_id
        self.text = text
        self.staff_message= staff_message
        self.status = status

    def report_is_completed(self):
        return self.status == COMPLETED
    
    def report_is_viewed(self):
        return self.status == VIEWED
    
    def report_to_string(self):
        staff_message_str = f"\n\n *Staff Message*\n{self.staff_message}" if self.staff_message else ""
        
        if self.status == NOT_TAKEN:
            return f"❌ - Report ID: {self.id}\n{self.text}{staff_message_str}"
        elif self.status == IN_PROGRESS:
            return f"⏳ - Report ID: {self.id}\n{self.text}{staff_message_str}"
        elif self.status == COMPLETED:
            return f"✅ - Report ID: {self.id}\n{self.text}{staff_message_str}"
        elif self.status == VIEWED:
            return f"👀 - Report ID: {self.id}\n{self.text}{staff_message_str}"
    
    def report_set_staff_message(self, message: str):
        self.staff_message = message