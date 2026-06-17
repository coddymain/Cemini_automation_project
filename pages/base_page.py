from playwright.sync_api import Page
from loguru import logger

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
        logger.info(f"Открываем страницу: {url}")
        self.page.goto(url)