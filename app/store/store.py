import typing


if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.bots_manager = None
        self.app = app

        from app.store.admin.accessor import AdminAccessor
        from app.store.bot.manager import BotManager
        from app.store.quiz.accessor import QuizAccessor
        from app.store.vk_api.accessor import VkApiAccessor

        self.vk_api = VkApiAccessor(app)
        self.quizzes = QuizAccessor(app)
        self.bots_manager = BotManager(app)

        self.admins = AdminAccessor(app)

def setup_store(app: "Application") -> None:
    from app.store.admin import setup_accessor
    app.store = Store(app)
    setup_accessor(app)