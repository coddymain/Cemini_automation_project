from playwright.sync_api import Locator
from pages.base_page import BasePage
from loguru import logger

class CheckoutOverviewPage(BasePage):
    """
    Page Object для страницы обзора перед подтверждением заказа.
    """
    # --- Локаторы ---
    @property
    def title(self) -> Locator:
        return self.page.locator('span.title')
        
    @property
    def _finish_button(self) -> Locator:
        return self.page.locator('[data-test="finish"]')
        
    # --- Действия ---
    def finish_checkout(self) -> None:
        """Нажимает кнопку завершения заказа."""
        logger.info("Подтверждаем заказ: нажимаем кнопку 'Finish'")
        self._finish_button.click()
        logger.success("Заказ успешно подтвержден")