from dataclasses import dataclass
from typing import Optional


# Базовые структуры, для выполнения задания их достаточно,
# поэтому постарайтесь не менять их, пожалуйста, из-за возможных проблем с тестами
@dataclass
class Message:
    user_id: int
    text: str


@dataclass
class UpdateMessage:
    from_id: int
    text: str
    id: int


@dataclass
class UpdateObject:
    message: UpdateMessage


@dataclass
class Update:
    # Поддерживаем оба варианта
    user_id: int = None
    text: str = None
    type: str = None
    object: dict = None

    def __post_init__(self):
        if self.object and not self.user_id:
            # Извлекаем данные из сложной структуры
            self.user_id = self.object.get("message", {}).get("from_id")
            self.text = self.object.get("message", {}).get("text")