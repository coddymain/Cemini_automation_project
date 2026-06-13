import pytest
from playwright.sync_api import  Page, expect
from core.settings import config

def test_successful_login(page: Page):
    """
    Тест успешной авторизации стандартным пользователем.
    """
    # Открываем страницу входа
    page.goto("/")

    # Вводим логин и пароль
    page.locator('[data-test="username"]').fill(config.STANDARD_USER)
    page.locator('[data-test="password"]').fill(config.VALID_PASSWORD)
    page.locator('[data-test="login-button"]').click()

    # Проверяем, что мы пришли на главную страницу.

    expect(page).to_have_url(f"{config.BASE_URL}inventory.html")
    expect(page.locator('span.title')).to_have_text("Products")

def test_locked_out_user(page: Page):
    """
    Тест авторизации заблокированного пользователя.
    """
    # Открываем страницу входа
    page.goto("/")

    # Вводим логин заблокированного пользователя и валидный пароль
    page.locator('[data-test="username"]').fill(config.LOCKED_OUT_USER)
    page.locator('[data-test="password"]').fill(config.VALID_PASSWORD)
    page.locator('[data-test="login-button"]').click()

    # Проверяем, что отображается сообщение об ошибке
    error_message = page.locator('[data-test="error"]')
    expect(error_message).to_be_visible()

    # Проверяем точный текст ошибки
    expect(error_message).to_have_text("Epic sadface: Sorry, this user has been locked out.")

def test_invalid_password(page: Page):
    """
    Тест авторизации с неправильным паролем.
        """
    # Arrange (Подготовка)
    page.goto("/")
    invalid_password = "wrong_password_123"


    #Act (Действия)
    page.locator('[data-test="username"]').fill(config.STANDARD_USER)
    page.locator('[data-test="password"]').fill(invalid_password)
    page.locator('[data-test="login-button"]').click()

    #Assert (Проверки)
    error_message = page.locator('[data-test="error"]')

    expect(error_message).to_be_visible()
    expect(error_message).to_have_text("Epic sadface: Username and password do not match any user in this service")