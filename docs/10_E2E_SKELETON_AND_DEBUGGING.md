# Шпаргалка 10: Написание E2E тестов и Отладка типизации

В этом этапе мы успешно написали наш первый сквозной (End-to-End) тест и научились отлаживать частую ошибку с импортом в Playwright.

## 1. Что такое E2E (End-to-End) тест?

E2E тест проверяет весь путь пользователя целиком. В нашем случае это:
Авторизация -> Каталог -> Добавление товара -> Переход в корзину -> Оформление заказа.

Такие тесты самые ценные для бизнеса, потому что они гарантируют, что главный пользовательский сценарий (который приносит деньги) работает корректно.

## 2. Архитектура чистого теста

Посмотри, как чисто выглядит наш E2E тест:

```python
def test_full_checkout_flow(page: Page, login_page: LoginPage, inventory_page: InventoryPage, cart_page: CartPage):
    # 1. Авторизация
    login_page.open(config.BASE_URL)
    login_page.login(config.STANDARD_USER, config.VALID_PASSWORD)
    expect(page).to_have_url(f"{config.BASE_URL}inventory.html")

    # 2. Добавление товара
    inventory_page.add_backpack_to_cart()
    inventory_page.go_to_cart()

    # 3. Работа с корзиной
    expect(page).to_have_url(f"{config.BASE_URL}cart.html")
    cart_page.click_checkout()
```

Здесь **нет ни одного сырого локатора** вроде `page.locator('.btn').click()`. Все действия спрятаны внутри соответствующих объектов страниц (`inventory_page`, `cart_page`). Это называется **Инкапсуляцией**. Тест читается как обычный текст на английском языке.

## 3. Отладка: Синхронный vs Асинхронный Playwright

Во время написания теста мы столкнулись с классической ошибкой:
`ValueError: Unsupported type: <class 'playwright.sync_api._generated.Page'>` внутри `playwright/async_api/__init__.py`.

**Причина:** 
Playwright поддерживает два режима работы:
1. **Синхронный (`sync_api`)**: Код выполняется строчка за строчкой. Мы используем его в Pytest.
2. **Асинхронный (`async_api`)**: Код использует ключевые слова `async` и `await`.

**Правило:**
Если тест синхронный, **все** импорты из Playwright (`Page`, `Locator`, `expect`) должны идти **только из `playwright.sync_api`**. Смешивать их нельзя!

## 4. Ошибки вызова методов

Важное правило Python:
*   `cart_page.click_checkout` — это **ссылка** на функцию (ничего не происходит).
*   `cart_page.click_checkout()` — это **вызов** функции (происходит клик).

Локаторы со свойством `@property` (например, `cart_page.checkout_button`) вызываются без скобок.
Действия (методы) — всегда вызываются со скобками `()`.
