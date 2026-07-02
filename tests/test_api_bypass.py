import pytest
from playwright.sync_api import Page, expect
from core.settings import config
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from loguru import logger

def test_direct_inventory_access(authenticated_page: Page, inventory_page: InventoryPage):
    """Тест, который проверяет мгновенный доступ к инвентарю без UI-логина."""
    logger.info("=== Запуск теста: Прямой доступ к инвентарю (API Bypass) ===")
    
    # 1. Мы сразу переходим на внутреннюю страницу, логин не нужен!
    logger.info("Переходим напрямую на страницу инвентаря (логин пропущен)")
    authenticated_page.goto(f"{config.BASE_URL}inventory.html")
    
    # 2. Проверяем, что нас не выкинуло на страницу логина
    expect(inventory_page.title).to_have_text("Products")


def test_unauthorized_access_redirect(page: Page, login_page: LoginPage):
    """Тест: попытка зайти на внутреннюю страницу без авторизации (без куки)."""
    logger.info("=== Запуск теста: Редирект неавторизованного пользователя ===")
    
    # 1. Пытаемся зайти на инвентарь БЕЗ фикстуры authenticated_page (используем чистую page)
    logger.info("Попытка прямого перехода на inventory.html без куки авторизации")
    page.goto(f"{config.BASE_URL}inventory.html")
    
    # 2. Проверяем, что нас выкинуло на страницу входа и показали системную ошибку
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_message).to_have_text(
        "Epic sadface: You can only access '/inventory.html' when you are logged in."
    )


def test_direct_cart_access(authenticated_page: Page, cart_page: CartPage):
    """Тест: мгновенный доступ в корзину (Deep Linking) с помощью обхода логина."""
    logger.info("=== Запуск теста: Прямой доступ в корзину (Deep Link) ===")
    
    # 1. Сразу летим в корзину, минуя логин и страницу списка товаров
    logger.info("Переходим напрямую на страницу корзины (cart.html)")
    authenticated_page.goto(f"{config.BASE_URL}cart.html")
    
    # 2. Проверяем, что корзина открылась успешно
    expect(authenticated_page).to_have_url(f"{config.BASE_URL}cart.html")
    expect(cart_page.checkout_button).to_be_visible()