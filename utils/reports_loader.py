# utils/reports_loader.py

from app.report import Report, NOT_TAKEN
from typing import Dict
import json, logging

class ReportLoader:

    def __init__(self,logger: logging.Logger):
        self.logger = logger

    def load_from_file(self, path: str) -> Dict[int, Report]:
        """
        Load questions from a JSON file.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                report_list = json.load(f)

            reports_dic = {}
            for r in report_list:
                id=r.get("id",-1)
                user_id = r.get("user_id", None)
                text = r.get("text", None)
                staff_message = r.get("staff_message", None)
                status = r.get("status", NOT_TAKEN)
                r = Report(id,user_id,text,staff_message,status)
                reports_dic[id] = r
            self.logger.info(f"Loaded {len(reports_dic)} reports from {path}")
            return reports_dic
        except FileNotFoundError:
            self.logger.error(f"File {path} not found")
            return {}
        
    
    def save_to_file(self, path: str, reports_dic: Dict[int, Report]):
        """
        Save questions to a JSON file.
        """
        report_list = []
        for report in reports_dic.values():
            report_data = {
                "id": report.id,
                "user_id": report.user_id,
                "text": report.text,
                "staff_message": report.staff_message,
                "status": report.status,
            }
            report_list.append(report_data)
        try:
            logging.info(f"Saving {len(report_list)} reports to {path}")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(report_list, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            self.logger.error(f"File {path} not found")
        
        
        