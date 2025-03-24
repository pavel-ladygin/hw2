import dataclasses

from app.quiz.models import Question, Answer
from app.quiz.schemes import ThemeSchema
from app.web.app import View
from app.web.middlewares import ThemeTitleError, QestionError, NoValueError
from app.web.utils import json_response, error_json_response
from app.store.quiz.accessor import QuizAccessor
from app.store.database import database
from tests.conftest import application

# TODO: добавить проверку авторизации для этого View
class ThemeAddView(View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    async def post(self):
        data = await self.request.json()
        title = data["title"]
        # TODO: заменить на self.data["title"] после внедрения валидации
        for theme in database.Database.themes:
            if theme.title == title:
                raise ThemeTitleError("Title is already exist")
        # TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        theme = await QuizAccessor.create_theme(self=QuizAccessor, title=data["title"])
        return json_response(data={
            "id" : theme.id,
            "title" : theme.title
        })


class ThemeListView(View):
    async def get(self):
        themes = await QuizAccessor.list_themes(self=QuizAccessor)
        data = []
        for thema in themes:
            cur = {"id" : thema.id, "title" : thema.title}
            data.append(cur)

        return json_response(data={
            "themes" : data
        })
class QuestionAddView(View):
    async def post(self):
        data = await self.request.json()
        cnt_ans = 0
        for ans in data["answers"]:
            if "title" not in ans or "is_correct" not in ans:
                raise KeyError
            if ans["is_correct"] == True:
                cnt_ans += 1
        if cnt_ans > 1:
            raise QestionError("More than one answer")
        if cnt_ans == 0:
            raise QestionError("no one right answer")
        if len(data["answers"]) <= 1:
            raise QestionError("only one answer")
        flag_1 = True
        for cur in database.Database.themes:
            if data["theme_id"] == cur.id:
                flag_1 = False
        if flag_1:
            raise NoValueError("no theme with this id")
        flag_2 = False
        for cur in database.Database.questions:
            if data["title"] == cur.title:
                flag_2 = True
        if flag_2:
            raise ThemeTitleError("its no unical question")
        question_ = await QuizAccessor.create_question(self=QuizAccessor, theme_id=data["theme_id"], title=data["title"], answers=data["answers"])
        return json_response(status="ok", data={
            "id" : question_.id,
            "title" : question_.title,
            "theme_id" : question_.theme_id,
            "answers" : question_.answers
        })




class QuestionListView(View):
    async def get(self):
        theme_id =  self.request.query.get("theme_id")
        question_ = await QuizAccessor.list_questions(self=QuizAccessor,theme_id=theme_id)
        data1 = list()
        answ = list()
        for cur in range(len(question_)):
            for i in question_[cur].answers:
                answ.append({
                    "title": i.title,
                    "is_correct" : i.is_correct
                })

            var = {
                "id" : question_[cur].id,
                "title" : question_[cur].title,
                "theme_id" : question_[cur].theme_id,
                "answers" : answ
            }
            data1.append(var)
            answ = []
        return json_response({
            "questions" : data1
        })
