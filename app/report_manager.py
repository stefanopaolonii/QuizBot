# app/report_manager.py

from typing import Dict, List
from .report import Report
from utils import ReportLoader
from app import set_last_report_id

class ReportManager:
    
    def __init__(self, report_json_path: str, logger):
        self.report_loader = ReportLoader(logger)
        self.reports_db :Dict[int, Report] = self.report_loader.load_from_file(report_json_path)
        set_last_report_id(max(self.reports_db.keys(), default=0))
        self.logger = logger
        self.report_json_path = report_json_path

    def report_get_data(self, report_id: int) -> Report:
        return self.reports_db.get(report_id, None)
    
    def report_add_data(self, report: Report):
        self.reports_db[report.id] = report
        self.report_save_dictionary(self.report_json_path)

    def report_save_dictionary(self, path: str):
        self.report_loader.save_to_file(path, self.reports_db)

    def report_list(self) -> List[Report]:
        return list(self.reports_db.values())
        
    def report_delete_completed_or_viewed_reports(self):
        self.reports_db = {k: v for k, v in self.reports_db.items() if not (v.report_is_completed() or v.report_is_viewed())}
        self.report_save_dictionary(self.report_json_path)

    def report_delete_report(self, report_id: int):
        if report_id in self.reports_db:
            del self.reports_db[report_id]
            self.report_save_dictionary(self.report_json_path)
            return True
        return False
    
    def report_list_for_user(self, user_id: str) -> list:
        return [report for report in self.reports_db.values() if report.user_id == user_id]

    def report_list_to_string(self, report_list : List[Report]) -> str:
        return "📋 *Report List*\n\n" + "\n\n".join([report.report_to_string() for report in report_list])
    
    def report_mark_reports(self, report_list: List[Report], status: int):
        for report in report_list:
            if report.status == status - 1:
                report.status = status
                self.reports_db[report.id] = report
        self.report_save_dictionary(self.report_json_path)