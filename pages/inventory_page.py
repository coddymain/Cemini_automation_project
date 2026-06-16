from playwright.sync_api import Locator
from pages.base_page import BasePage
from loguru import logger

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
        logger.info("Добавляем рюкзак 'Sauce Labs Backpack' в корзину")
        self._add_backpack_button.click()
        logger.success("Рюкзак добавлен")

    def go_to_cart(self) -> None:
        logger.info("Кликаем по иконке корзины для перехода")
        self._cart_icon.click()

    
