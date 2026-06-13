# Шпаргалка 6: Разбор первого E2E теста (Playwright + Pytest)

В этом разделе мы детально разбираем анатомию нашего первого автотеста (`tests/test_login.py`), чтобы понимать, как именно Playwright взаимодействует с браузером и как Pytest управляет запуском.

## 1. Анатомия теста и фикстуры
```python
def test_successful_login(page: Page):
```
*   **Имя функции:** Начинается с `test_`. Это обязательное требование Pytest. Если назвать функцию `check_login`, Pytest её просто проигнорирует.
*   **Внедрение зависимостей (Dependency Injection):** Мы запрашиваем фикстуру `page: Page`. Pytest + pytest-playwright автоматически создают новую чистую вкладку браузера (с изолированным контекстом) и передают её прямо в наш тест.

## 2. Навигация и использование Config
```python
# Открываем страницу входа
page.goto("/")
```
Здесь мы используем относительный путь `/`. Почему это работает? 
В `conftest.py` мы задали `base_url` через фикстуру `browser_context_args`. Playwright автоматически подклеивает `/` к нашему `config.BASE_URL` (https://www.saucedemo.com/).

## 3. Локаторы: Поиск элементов
```python
page.locator('[data-test="username"]').fill(config.STANDARD_USER)
```
*   **Локаторы (Locators):** Это способ сказать Playwright, с каким элементом на странице мы хотим взаимодействовать.
*   **Enterprise-стандарт:** Использование атрибутов вроде `data-test`, `data-testid` или `id`. Это самые надежные селекторы, так как они не меняются при редизайне (в отличие от классов `.login_input` или сложных XPath). Разработчики специально оставляют их для тестировщиков.
*   **Действие:** Метод `.fill()` не просто вводит текст, он сначала дожидается, когда элемент станет видимым, доступным для клика (enabled) и не перекрытым другими элементами. Playwright делает это автоматически (Auto-waiting).

## 4. Умные проверки (Assertions)
```python
from playwright.sync_api import expect

expect(page).to_have_url(f"{config.BASE_URL}inventory.html")
expect(page.locator('span.title')).to_have_text("Products")
```
*   Вместо стандартного питоновского `assert` мы используем `expect` из Playwright.
*   **Почему `expect` лучше?** Это "умные" проверки с авто-ожиданием (Auto-retrying assertions). Если после клика на кнопку "Login" страница грузится полсекунды, обычный `assert` мгновенно бы упал с ошибкой (элемент еще не появился). `expect` будет **ждать и пробовать снова** (до 5 секунд по умолчанию), пока условие не выполнится или не выйдет таймаут (Timeout). Это избавляет нас от нестабильных тестов (flaky tests) и жестких пауз типа `time.sleep()`.

## 5. Безопасность данных (Секреты)
Заметьте, мы нигде не пишем пароли прямо в коде теста:
`config.STANDARD_USER` и `config.VALID_PASSWORD` приходят из нашего класса `Settings` (Pydantic), который, в свою очередь, безопасно читает их из скрытого файла `.env`.
## 6. Негативные проверки и паттерн Arrange-Act-Assert (AAA)
Помимо позитивного (успешного) сценария, в `tests/test_login.py` добавлены негативные тесты:

### Тест заблокированного пользователя
```python
def test_locked_out_user(page: Page):
    page.goto("/")
    page.locator('[data-test="username"]').fill(config.LOCKED_OUT_USER)
    page.locator('[data-test="password"]').fill(config.VALID_PASSWORD)
    page.locator('[data-test="login-button"]').click()
    
    error_message = page.locator('[data-test="error"]')
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text("Epic sadface: Sorry, this user has been locked out.")
```
Здесь мы проверяем не только то, что элемент с ошибкой появился (`to_be_visible()`), но и то, что он содержит конкретный, ожидаемый текст.

### Тест неверного пароля и паттерн AAA
```python
def test_invalid_password(page: Page):
    # Arrange (Подготовка)
    page.goto("/")
    invalid_password = "wrong_password_123"

    # Act (Действия)
    page.locator('[data-test="username"]').fill(config.STANDARD_USER)
    page.locator('[data-test="password"]').fill(invalid_password)
    page.locator('[data-test="login-button"]').click()

    # Assert (Проверки)
    error_message = page.locator('[data-test="error"]')
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text("Epic sadface: Username and password do not match any user in this service")
```
Этот тест наглядно демонстрирует классический паттерн структурирования автотестов **AAA (Arrange, Act, Assert)**:
1.  **Arrange (Подготовка):** Устанавливаем начальное состояние. Открываем страницу, генерируем или подготавливаем тестовые данные (например, `invalid_password`).
2.  **Act (Действие):** Выполняем шаги, которые мы тестируем (ввод данных, клики).
3.  **Assert (Проверка):** Проверяем, что система отреагировала ожидаемым образом.

Такое разделение делает тесты легко читаемыми и поддерживаемыми.