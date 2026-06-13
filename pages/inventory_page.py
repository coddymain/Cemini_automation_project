from playwright.sync_api import Locator
from pages.base_page import BasePage

class InventoryPage(BasePage):
    """
    Page Object для страницы инвентаря.
    Содержит методы для взаимодействия с элементами страницы инвентаря.
    """
    # Локаторы
    @property
    def title(self) -> Locator:
        return self.page.locator('span.title')

    @property
    def _add_backpack_button(self) -> Locator:
        return self.page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')
    
    @property
    def _cart_icon(self) -> Locator:
        return self.page.locator('[data-test="shopping-cart-link"]')
    
    # Методы
    def add_backpack_to_cart(self) -> None:
       self._add_backpack_button.click()

    def go_to_cart(self) -> None:
        self._cart_icon.click()
        

    
