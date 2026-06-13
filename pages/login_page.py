from playwright.sync_api import Locator
from pages.base_page import BasePage

class LoginPage(BasePage):
    """
    Page Object для страницы входа.
    Содержит методы для взаимодействия с элементами страницы входа.
    """
    @property
    def _username_input(self) -> Locator:
        return self.page.locator('[data-test="username"]')
    
    @property
    def _password_input(self) -> Locator:
        return self.page.locator('[data-test="password"]')
    
    @property
    def _login_button(self) -> Locator:
        return self.page.locator('[data-test="login-button"]')
    
    @property
    def error_message(self) -> Locator:
        return self.page.locator('[data-test="error"]')
    
    def login(self, username: str, password: str) -> None: 
        """
        Метод для авторизации на сайте.
        Заполняет поля логина и пароля, затем нажимает кнопку входа.
        """
        self._username_input.fill(username)
        self._password_input.fill(password)
        self._login_button.click()