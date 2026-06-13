import pytest
from playwright.sync_api import Page, expect
from core.settings import config
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from data.models import test_customer

def test_full_checkout_flow(page: Page, login_page: LoginPage, inventory_page: InventoryPage, cart_page: CartPage, checkout_page: CheckoutPage):
    """E2E тест: Полный цикл покупки товара."""

    # 1. Авторизация
    login_page.open(config.BASE_URL)
    login_page.login(config.STANDARD_USER, config.VALID_PASSWORD)
    # Проверяем что мы попаля на страницу товаров
    expect(page).to_have_url(f"{config.BASE_URL}inventory.html")

    # 2. Добавление товара
    inventory_page.add_backpack_to_cart()

    # Переход в корзину
    inventory_page.go_to_cart()

    # 3. Работа с корзиной. Проверяем что мы попали на страницу корзины
    expect(page).to_have_url(f"{config.BASE_URL}cart.html")

    # Кликаем по Checkout
    cart_page.click_checkout()

    # Проверяем что мы перешли на страницу оформление заказа
    expect(page).to_have_url(f"{config.BASE_URL}checkout-step-one.html")

    # 4. Оформление заказа: Шаг 1
    checkout_page.fill_personal_info(test_customer)
    expect(page).to_have_url(f"{config.BASE_URL}checkout-step-two.html")

    # 5. Оформление заказа: шаг 2
    checkout_page.click_finish()
    expect(page).to_have_url(f"{config.BASE_URL}checkout-complete.html")

    # 6. Проверка успешного завершения!
    expect(checkout_page.complete_header).to_have_text("Thank you for your order!")