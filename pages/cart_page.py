from playwright.sync_api import Locator
from pages.base_page import BasePage
from loguru import logger

class CartPage(BasePage):

    """Локаторы"""
    @property
    def item_name(self) -> Locator:
        return self.page.locator('.inventory_item_name')
    
    @property
    def checkout_button(self) -> Locator:
        return self.page.locator('[data-test="checkout"]')
    
    """Действия"""
    def click_checkout(self) -> None:
        logger.info("Нажимаем кнопку 'Checkout' в корзине")
        self.checkout_button.click()
