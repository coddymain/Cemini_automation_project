from playwright.sync_api import Locator
from pages.base_page import BasePage
from loguru import logger

class CheckoutCompletePage(BasePage):
    """
    Page Object для финальной страницы успешного заказа.
    """
    # --- Локаторы ---
    @property
    def title(self) -> Locator:
        return self.page.locator('span.title')
        
    @property
    def complete_header(self) -> Locator:
        """Заголовок с текстом благодарности за заказ (Публичный локатор для проверок)."""
        return self.page.locator('h2.complete-header')

    @property
    def _back_home_button(self) -> Locator:
        return self.page.locator('[data-test="back-to-products"]')

    # --- Действия ---
    def go_back_home(self) -> None:
        logger.info("Возвращаемся на главную страницу (нажимаем 'Back Home')")
        self._back_home_button.click()