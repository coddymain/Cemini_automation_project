from playwright.sync_api import Locator
from pages.base_page import BasePage

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
        self.checkout_button.click()
