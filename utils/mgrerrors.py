from .errors import AztraError
from enum import Enum

# Global

class NotFound(AztraError):
    pass
        
class SettingNotFound(AztraError):
    def __init__(self, name: str):
        self.name = NameError
        super().__init__(f'설정을 찾을 수 없습니다! (NAME: "{name}")')