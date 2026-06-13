# Шпаргалка 8: Внедрение зависимостей (Dependency Injection) через фикстуры Pytest

В предыдущей шпаргалке мы узнали про Page Object Model (POM). Наши тесты стали чище, но появилась новая проблема — дублирование кода. В каждом тесте мы вынуждены вручную создавать объекты страниц (инициализировать их).

## 1. Проблема: Тест работает как "Фабрика"

Посмотрим на то, как мы писали тесты раньше:

```python
# test_login.py
def test_successful_login(page: Page):
    # Тест сам "собирает" нужные ему инструменты (страницы)
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    
    # И только потом делает свою основную работу
    login_page.open(config.BASE_URL)
    ...
```

**Почему это плохо?**
*   **Нарушение принципа DRY (Don't Repeat Yourself):** Если у нас 100 тестов, мы 100 раз напишем `login_page = LoginPage(page)`.
*   **Лишняя ответственность:** Тест должен только проверять логику. Он не должен заниматься подготовкой и сборкой объектов. Представьте, что вы пришли в ресторан (тест), а вам говорят: "Вот мука, яйца и сковородка (page), приготовьте себе блинчики (LoginPage) сами". 

## 2. Решение: Фикстуры Pytest как "Поставщики"

В Pytest есть гениальный механизм — **Фикстуры (Fixtures)**. Это специальные функции-помощники, которые живут в файле `conftest.py`.

*   **Как это работает в ресторане:** Вы (тест) садитесь за стол и говорите официанту: "Принеси мне готовые блинчики (`login_page`)". Официант (Pytest) идет на кухню (`conftest.py`), там повар (фикстура) берет ингредиенты (`page`), готовит блинчики и приносит их вам.
*   Это называется **Dependency Injection (Внедрение зависимостей)**. Тест просто *требует* то, что ему нужно (зависимость), а система (Pytest) сама это находит, создает и *внедряет* (передает) в тест.

---

## 3. Как мы это настраиваем (Пошагово)

### Шаг 1: Учим `conftest.py` готовить страницы

Открываем центральный файл конфигурации тестов — `conftest.py`. Мы добавим туда функции, которые знают, как создать нужную страницу.

```python
# conftest.py

import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

# Декоратор говорит Pytest: "Эй, это не простая функция, это поставщик (фикстура)!"
@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """
    Эта функция создает и отдает готовый объект LoginPage.
    """
    # Фикстура сама просит у Pytest объект браузера (page),
    # создает класс страницы и возвращает (return) его.
    return LoginPage(page)

@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    """
    Эта функция создает и отдает готовый объект InventoryPage.
    """
    return InventoryPage(page)
```

**Разбор магии:**
1.  `@pytest.fixture`: Это клеймо. Без него Pytest не увидит функцию. По умолчанию Pytest запускает эту функцию заново для *каждого* теста. Это значит, что у каждого теста будет свой, свежий и независимый объект страницы.
2.  `def login_page(...)`: Имя функции очень важно! Именно по этому имени тест будет просить эту фикстуру.
3.  `(page: Page)`: Наша фикстура сама нуждается в браузере (`page`), чтобы передать его в `LoginPage`. Pytest это понимает: он сначала создает базовую фикстуру `page` (которая встроена в Playwright), отдает её нашей фикстуре `login_page`, а уже потом результат отдает тесту. Это называется *цепочка фикстур*.
4.  `-> LoginPage`: Это просто подсказка для нас и для редактора кода (Type Hinting), чтобы он знал, что именно возвращает эта функция.

### Шаг 2: Чистим тесты (`test_login.py`)

Теперь тесту не нужно самому ничего собирать. Он просто просит то, что ему нужно, в своих аргументах (в скобочках `def test_...`).

**Было (грязно):**
```python
from pages.login_page import LoginPage # ❌ Тесту больше не нужен сам класс

def test_locked_out_user(page: Page): # ❌ Запрашивает сырой браузер
    login_page = LoginPage(page)      # ❌ Сам собирает страницу
    login_page.open(config.BASE_URL)
```

**Стало (чисто):**
```python
# ✔️ Классы LoginPage и InventoryPage мы больше не импортируем! 
# Они создаются за кулисами в conftest.py

def test_locked_out_user(page: Page, login_page: LoginPage):
    # ✔️ Тест просто просит готовую фикстуру login_page. 
    # (page: Page мы оставляем, если внутри теста хотим проверить URL через expect(page))
    
    login_page.open(config.BASE_URL) 
    login_page.login(config.LOCKED_OUT_USER, config.VALID_PASSWORD)
```

**Откуда редактор знает, что такое `login_page`?**
Запись `login_page: LoginPage` означает: переменная называется `login_page` (это имя ищет Pytest), а её тип (класс) — это `LoginPage` (это ищет ваш редактор кода, чтобы показывать подсказки после точки, например `login_page.login()`). 

> **Важно:** Чтобы подсказки работали, нам всё-таки придется импортировать сами классы `LoginPage` и `InventoryPage` в файл `test_login.py`, но *только* для аннотаций типов, а не для создания объектов!

---

## Итог: Что мы получили?

1.  **Чистота:** Тесты стали короче. Ушел мусорный код инициализации.
2.  **Масштабируемость:** Если завтра конструктор `LoginPage` изменится (например, ему потребуется передавать не только `page`, но и какие-то настройки базы данных), мы изменим это **только в одном месте** — внутри `conftest.py`. Тысячи тестов даже не заметят изменений, так как они просто получают готовый результат.
3.  **Изоляция:** Каждая страница создается заново для каждого теста благодаря стандартному поведению (scope) фикстур Pytest.

---

## 4. Полный итоговый код

Вот как должны выглядеть ваши файлы после внедрения фикстур:

### `conftest.py`
```python
import pytest
from typing import Dict, Any
from playwright.sync_api import Page
from core.settings import config
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Переопределяем встроенную фикстуру pytest-playwright.
    Здесь мы задаем настройки для контекста браузера (всех новых страниц).
    """
    return {
        **browser_context_args,
        "base_url": config.BASE_URL,
        "viewport": {"width": 1920, "height": 1080},
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
```

### `tests/test_login.py`
```python
import pytest
from playwright.sync_api import Page, expect
from core.settings import config
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

def test_successful_login(page: Page, login_page: LoginPage, inventory_page: InventoryPage):
    login_page.open(config.BASE_URL)
    login_page.login(config.STANDARD_USER, config.VALID_PASSWORD)
    expect(page).to_have_url(f"{config.BASE_URL}inventory.html")
    expect(inventory_page.title).to_have_text("Products")

def test_locked_out_user(page: Page, login_page: LoginPage):
    login_page.open(config.BASE_URL)
    login_page.login(config.LOCKED_OUT_USER, config.VALID_PASSWORD)
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_message).to_have_text("Epic sadface: Sorry, this user has been locked out.")

def test_invalid_password(page: Page, login_page: LoginPage):
    login_page.open(config.BASE_URL)
    login_page.login(config.STANDARD_USER, "wrong_password_123")
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_message).to_have_text("Epic sadface: Username and password do not match any user in this service")
```
