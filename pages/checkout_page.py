from playwright.sync_api import Locator
from pages.base_page import BasePage
from data.models import Customer
from loguru import logger

class CheckoutPage(BasePage):
    """Локаторы: Шаг 1 (Ввод данных)"""
    @property
    def first_name_input(self) -> Locator:
        return self.page.locator('[data-test="firstName"]')
    
    @property
    def last_name_input(self) -> Locator:
        return self.page.locator('[data-test="lastName"]')
    
    @property
    def postal_code_input(self) -> Locator:
        return self.page.locator('[data-test="postalCode"]')
    
    @property
    def continue_button(self) -> Locator:
        return self.page.locator('[data-test="continue"]')
    
    """Локаторы Шаг 2 (Потверждение)"""
    @property
    def finish_button(self) -> Locator:
        return self.page.locator('[data-test="finish"]')
    
    """Локаторы: Шаг 3 (Завершение)"""
    @property
    def complete_header(self) -> Locator:
        return self.page.locator('.complete-header')
    
    """Методы (Действия)"""
    def fill_personal_info(self, customer: Customer) -> None:
        logger.info(f"Заполняем данные покупателя: {customer.first_name} {customer.last_name}")
        self.first_name_input.fill(customer.first_name)
        self.last_name_input.fill(customer.last_name)
        self.postal_code_input.fill(customer.postal_code)
        self.continue_button.click()
        logger.success("Данные покупателя заполнены, перешли к обзору заказа")

    def click_finish(self) -> None:
        logger.info("Нажимаем кнопку 'Finish'")
        self.finish_button.click()
