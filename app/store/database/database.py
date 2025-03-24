from dataclasses import dataclass


@dataclass
class Database:
    # TODO: добавить поля admins и questions

    themes = list()
    admins = list()
    questions = list()
    @property
    def next_theme_id(self) -> int:
        return len(self.themes) + 1

    def clear(self):
        self.themes.clear()
        self.questions.clear()
