import app.store.database.database
from app.base.base_accessor import BaseAccessor
from app.quiz.models import Answer, Question, Theme
from app.web.app import Application
from app.store.database import database


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        theme = Theme(id=len(database.Database.themes)+1, title=title)
        database.Database.themes.append(theme)
        return theme


    async def get_theme_by_title(self, title: str) -> Theme | None:
        for theme in database.Database.themes:
            if theme.title == title:
                return theme
        return None

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        for theme in database.Database.themes:
            if theme.id == id_:
                return theme
        return None
    async def list_themes(self) -> list[Theme]:
        var = list()
        data = database.Database.themes
        for cur in data:
            var.append(cur)
        return var

    async def get_question_by_title(self, title: str) -> Question | None:
        raise NotImplementedError

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]) -> Question:
        question_ = Question(id=len(database.Database.questions) + 1, title=title, theme_id=theme_id, answers=answers)
        database.Database.questions.append(question_)
        return question_

    async def list_questions(
        self, theme_id: str | None = None
    ) -> list[Question]:
            data = database.Database.questions
            if not theme_id:
                return data
            var = list()
            theme_id = str(theme_id)[1:-1]
            for question in data:
                if question.theme_id == int(theme_id):
                    var.append(question)
            return var
