# Шпаргалка 18: Пропуск UI-логина и основы API-тестирования

В этом этапе мы переходим к одному из самых важных паттернов Enterprise-автоматизации — **обходу UI-авторизации (Bypass UI Login)**.

## 1. Зачем пропускать UI-логин?
В E2E сценарии мы логинимся через UI (как настоящий пользователь). Но если у нас 100 тестов на корзину, профиль и товары, логиниться через UI в каждом из них — это огромная потеря времени. 
UI-логин занимает 2-3 секунды, а в 100 тестах это уже 5 минут лишнего времени.
Поэтому в тестах, где логин не является главной целью проверок, мы "впрыскиваем" авторизацию мгновенно.

## 2. Как это работает в реальных API (Теория Playwright APIRequestContext)
В Playwright есть встроенный инструмент для работы с API — `request`. В настоящем проекте с бэкендом (REST API) мы бы сделали так:

```python
# Пример (не для нашего проекта)
api_context = playwright.request.new_context(base_url="https://api.example.com")
response = api_context.post("/login", data={"user": "admin", "pass": "123"})

# Сохраняем слепок куки/токенов в память
state = api_context.storage_state() 

# Создаем браузер уже с этими куками
context = browser.new_context(storage_state=state)
```

## 3. Особенность нашего проекта (Swag Labs)
Сайт `saucedemo.com` — это mock-приложение (симуляция). У него нет реального бэкенда и эндпоинта `/api/login`. Вся его "защита" заключается в том, что JavaScript просто устанавливает Cookie с именем `session-username`.

Следовательно, чтобы пропустить UI-логин, нам достаточно использовать методы Playwright и **вручную подложить эту куку в контекст браузера** перед открытием страницы!

## 4. Практика: Создание фикстуры `authenticated_page`
В файле `conftest.py` мы создаем новую фикстуру. Она берет чистую страницу, вставляет нужную куку, и отдает тесту уже залогиненный браузер.

```python
# conftest.py
@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """
    Фикстура, которая обходит UI-логин путем прямой установки Cookie.
    Отдает страницу (Page), уже готовую к работе с внутренними разделами сайта.
    """
    page.goto(config.BASE_URL)

    cookie_value = config.STANDARD_USER.strip()
    parsed_domain = urlparse(config.BASE_URL).hostname

    if not parsed_domain:
        raise ValueError(f"Не удалось извлечь домен из BASE_URL: {config.BASE_URL}")

    if not cookie_value:
        raise ValueError("Cookie value is empty. Check STANDARD_USER.")

    page.context.add_cookies([
        {
            "name": "session-username",
            "value": cookie_value,
            "domain": parsed_domain,
            "path": "/"
        }
    ])
    return page
```

### Почему фикстура выглядит именно так?
*   `page.goto(config.BASE_URL)` — переводит браузер с системной страницы `about:blank` на настоящий домен приложения. В CI/CD это важно: headless Chromium может отклонить установку Cookie для чужого домена, если текущая страница еще не открыта.
*   `config.STANDARD_USER.strip()` — очищает значение секрета от случайных пробелов и переносов строк. Это защищает от ошибки `Invalid cookie fields`, которая часто возникает в GitHub Actions.
*   `urlparse(config.BASE_URL).hostname` — извлекает домен динамически. Мы не хардкодим `www.saucedemo.com`, поэтому фикстура переживет переезд на другой стенд.
*   Проверка `if not parsed_domain` — быстро падает с понятной ошибкой, если `BASE_URL` задан некорректно.
*   Проверка `if not cookie_value` — помогает сразу увидеть проблему с пустым `STANDARD_USER`, вместо загадочного падения браузера ниже по стеку.

Итог: это уже не просто "подложить куку", а CI-ready вариант обхода логина.

## 5. Практика: Как выглядит тест
Теперь мы можем написать тест, который мгновенно открывает страницу инвентаря без авторизации:

```python
# tests/test_api_bypass.py
def test_direct_inventory_access(authenticated_page: Page, inventory_page: InventoryPage):
    # 1. Мы сразу переходим на внутреннюю страницу, логин не нужен!
    authenticated_page.goto(f"{config.BASE_URL}inventory.html")
    
    # 2. Проверяем, что нас не выкинуло на страницу логина
    expect(inventory_page.title).to_have_text("Products")
```

## 6. Расширенные сценарии и проверки

Чтобы убедиться, что наш метод обхода логина работает корректно и имеет смысл, мы добавляем еще два типа тестов.

### Негативный тест (Проверка защиты)
Мы должны доказать, что на сайт нельзя попасть по прямой ссылке без авторизации. Этот тест использует обычную, "чистую" фикстуру `page` и проверяет, что система безопасности сайта перенаправляет нас на страницу входа с сообщением об ошибке.

```python
# tests/test_api_bypass.py
def test_unauthorized_access_redirect(page: Page, login_page: LoginPage):
    """Тест: попытка зайти на внутреннюю страницу без авторизации (без куки)."""
    # 1. Пытаемся зайти на инвентарь БЕЗ фикстуры authenticated_page
    page.goto(f"{config.BASE_URL}inventory.html")
    
    # 2. Проверяем, что нас выкинуло на страницу входа и показали системную ошибку
    expect(login_page.error_message).to_have_text(
        "Epic sadface: You can only access '/inventory.html' when you are logged in."
    )
```

### Тест на "глубокие ссылки" (Deep Linking)
Этот тест демонстрирует всю мощь подхода: мы можем мгновенно "телепортироваться" на любую внутреннюю страницу приложения, например, в корзину, минуя все промежуточные шаги.

```python
def test_direct_cart_access(authenticated_page: Page, cart_page: CartPage):
    """Тест: мгновенный доступ в корзину (Deep Linking) с помощью обхода логина."""
    # 1. Сразу летим в корзину, минуя логин и страницу списка товаров
    authenticated_page.goto(f"{config.BASE_URL}cart.html")
    
    # 2. Проверяем, что корзина открылась успешно
    expect(cart_page.checkout_button).to_be_visible()
```
