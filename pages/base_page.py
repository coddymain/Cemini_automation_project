from playwright.sync_api import Page

class BasePage:
    """
    Базовый класс для всех Page Objects.
    Содержит общие методы для взаимодействия с Playwright.
    """

    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str = ""):
        """
        Открывает страницу по заданному URL.
        Если URL не указан, открывает базовый URL, заданный в конфигурации.
        """
        self.page.goto(url)