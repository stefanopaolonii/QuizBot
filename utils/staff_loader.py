# utils/staff_loader.py

from app.staff import Staff
from typing import Dict
import json, logging

class StaffLoader:

    def __init__(self,logger: logging.Logger):
        self.logger = logger

    def load_from_file(self, path: str) -> Dict[str, Staff]:
        """
        Load staff data from a JSON file.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                staff_data = json.load(f)
            staff_dict = {}
            for s in staff_data:
                id = s.get("id", None)
                role = s.get("role", None)
                staff=Staff(id,role)
                staff_dict[id] = staff
            self.logger.info(f"Loaded {len(staff_dict)} staff members from {path}")
            return staff_dict
        except FileNotFoundError:
            self.logger.error(f"File {path} not found")
            return {}
    
    def save_to_file(self, path: str, staff_dict: Dict[int, Staff]):
        """
        Save staff data to a JSON file.
        """
        staff_data = []
        for staff in staff_dict.values():
            s_data = {
                "id": staff.id,
                "role": staff.role
            }
            staff_data.append(s_data)

        try :
            self.logger.info(f"Saving {len(staff_data)} staff members to {path}")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(staff_data, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            self.logger.error(f"File {path} not found")