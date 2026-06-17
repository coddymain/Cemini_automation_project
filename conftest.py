import pytest
import allure
from urllib.parse import urlparse
from slugify import slugify
from typing import Dict, Any
from core.settings import config
from core.logger import setup_logger
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.checkout_overview_page import CheckoutOverviewPage
from pages.checkout_complete_page import CheckoutCompletePage
from loguru import logger

# Инициализируем настройки логгера для всего проекта при старте тестов
setup_logger()

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Переопределяем встроенную фикстуру pytest-playwright.
    Здесь мы задаем настройки для контекста браузера (всех новых страниц).
    """
    return {
        **browser_context_args,
        "base_url": config.BASE_URL,
        "viewport": {"width": 1512, "height": 982},
        "ignore_https_errors": True,
    }

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """Фикстура для инициализации LoginPage."""
    return LoginPage(page)

@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    """Фикстура для инициализации InventoryPage."""
    return InventoryPage(page)

@pytest.fixture
def cart_page(page: Page) -> CartPage:
    """Фикстура для инициализации CartPage."""
    return CartPage(page)

@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    """Фикстура для инициализации"""
    return CheckoutPage(page)

@pytest.fixture
def checkout_overview_page(page: Page) -> CheckoutOverviewPage:
    """Фикстура для инициализации страницы Checkout Overview."""
    return CheckoutOverviewPage(page)

@pytest.fixture
def checkout_complete_page(page: Page) -> CheckoutCompletePage:
    """Фикстура для инициализации страницы успешного завершения заказа."""
    return CheckoutCompletePage(page)

@pytest.fixture
def authenticated_page(page: Page) -> Page:
    logger.debug("Устанавливаем cookie 'session-username' для обхода UI-логина")
    
    # Сначала открываем базовый URL, чтобы уйти со страницы 'about:blank'. 
    # Иначе headless Chromium в CI блокирует установку кук для чужого домена.
    page.goto(config.BASE_URL)

    # =====================================================================
    # РЕШЕНИЕ ПРОБЛЕМЫ CI/CD: "Protocol error (Storage.setCookies)"
    # =====================================================================
    # В CI/CD (GitHub Actions) при вставке секретов часто случайно 
    # захватываются невидимые символы переноса строки (\n) или пробелы.
    # Строгий Headless Chromium моментально падает с ошибкой "Invalid cookie fields", 
    # если попытаться передать такое значение в Cookie.
    # Метод .strip() железобетонно очищает строку от этого "мусора" по краям.
    cookie_value = config.STANDARD_USER.strip()

    # Автоматически извлекаем домен из BASE_URL, чтобы не хардкодить его.
    # Это стало безопасным после решения проблем с CI/CD.
    parsed_domain = urlparse(config.BASE_URL).hostname
    if not parsed_domain:
        raise ValueError(f"Не удалось извлечь домен из BASE_URL: {config.BASE_URL}")

    # === DEBUG LOGGING FOR CI ===
    # Логируем значения, чтобы убедиться, что секреты GitHub прочитаны верно.
    logger.info(f"Attempting to set cookie for domain '{parsed_domain}' with value: '{cookie_value}'")
    if not cookie_value:
        raise ValueError("CRITICAL: Cookie value is empty. Check the STANDARD_USER GitHub Secret.")

    page.context.add_cookies([
        {
            "name": "session-username",
            "value": cookie_value,
            "domain": parsed_domain,
            "path": "/"
        }
    ])
    return page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук (перехватчик) Pytest. Вызывается на разных стадиях жизненного цикла теста (setup, call, teardown).
    Мы используем его, чтобы автоматически делать скриншот при падении теста и передавать его в Allure.
    """
    # Ждем, пока Pytest выполнит текущую фазу теста и отдаст нам результат
    outcome = yield
    report = outcome.get_result()

    # Фаза 'call' - это выполнение самого тела теста. 
    # Проверяем: если мы находимся в фазе 'call' и тест завершился с ошибкой (failed)
    if report.when == "call" and report.failed:
        # Пытаемся получить объект 'page' (инстанс браузера Playwright) из фикстур упавшего теста
        page = item.funcargs.get('page')
        if page:
            try:
                # Просим Playwright сделать скриншот текущего состояния страницы прямо в оперативную память
                screenshot = page.screenshot(type='png', full_page=True)
                
                # Прикрепляем полученный байтовый массив скриншота к Allure отчету, 
                # используя безопасное имя файла (slugify) на основе имени теста
                allure.attach(
                    screenshot,
                    name=f"Screenshot_{slugify(item.name)}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"Не удалось сделать скриншот для Allure: {e}")
                
            try:
                # Также прикрепляем файл с нашими логами
                allure.attach.file(
                    "logs/test_run.log",
                    name=f"Logs_{slugify(item.name)}",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as e:
                print(f"Не удалось прикрепить логи для Allure: {e}")