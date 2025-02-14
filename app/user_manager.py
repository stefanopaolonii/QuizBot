# app/user_manager.py

from typing import Dict, List
from .staff import Staff
from utils import StaffLoader
import hashlib

role_hierarchy = {
            "User": ["User"],
            "Mod": ["User", "Mod"],
            "Admin": ["User", "Mod", "Admin"],
            "Owner": ["User", "Mod", "Admin", "Owner"]

}

class UserManager:

    def __init__(self, staff_json_path:str, logger):
        self.staff_loader = StaffLoader(logger)
        self.staff_db : Dict[int, Staff] = self.staff_loader.load_from_file(staff_json_path)
        self.logger = logger
        self.staff_json_path = staff_json_path

    def staff_get_data(self, staff_id : str) -> Dict[int, Staff]:
        return self.staff_db.get(staff_id, None)
    
    def staff_add_data(self, staff: Staff):
        self.staff_db[staff.id] = staff
        self.staff_save_dictionary(self.staff_json_path)
    
    def staff_save_dictionary(self, path: str):
        self.staff_loader.save_to_file(path, self.staff_db)

    def staff_extract_list_ids(self) -> list:
        return self.staff_db.keys()

    def user_get_id(self, user_id: int) -> str:
        return self.user_mask_id(user_id)

    def user_get_role(self, user_id: str) -> str:
        return self.staff_db.get(user_id).role if user_id in self.staff_db else "User"

    def user_mask_id(self, user_id, salt="salt_fisso_123456789"):
        data = str(user_id) + salt
        hash_object = hashlib.sha256(data.encode())
        hash_hex = hash_object.hexdigest()
        return hash_hex
    
    def user_allowed_roles(self, role: str) -> list:
        return role_hierarchy.get(role, [])
    
    def user_is_staff(self, user_id: str) -> bool:
        return user_id in self.staff_db