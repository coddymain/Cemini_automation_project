# Шпаргалка 19: Локальный Mock-сервер на FastAPI (Ультра-подробный разбор)

В автоматизации уровня Enterprise нельзя тестировать систему только через графический интерфейс (UI). Нам нужно уметь работать с **API (Application Programming Interface)** — "невидимым" мостом, по которому передаются данные.

Так как наш тестовый сайт (Swag Labs) не имеет публичного API, мы создаем **свой собственный Mock-сервер** (Имитатор бэкенда). Он позволит нам тренировать API-тесты локально.

В этой документации мы разберем каждую строку созданного нами сервера и автотестов к нему.

---

## 1. Структура проекта (Важное правило!)

Файл сервера **строго** должен лежать в отдельной папке. 
*   ❌ `docs/main.py` — **Неправильно** (серверу не место в документации).
*   ✅ `mock_server/main.py` — **Правильно** (выделенный модуль в корне проекта).

---

## 2. Разбор файла сервера: `mock_server/main.py`

Этот файл — "мозг" нашего сервера. Разберем каждую строчку.

### Блок импортов
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
```
*   `from fastapi import FastAPI` — Берем главный класс `FastAPI` из установленной библиотеки. Именно он умеет "слушать" сеть и принимать HTTP-запросы.
*   `from fastapi import HTTPException` — Берем специальный класс для ошибок. Если тест запросит несуществующие данные, мы вернем ему красивую ошибку (например, 404 Not Found), а не сломаем сервер.
*   `from pydantic import BaseModel` — Pydantic нужен для строгой валидации. `BaseModel` — это фундамент, на котором мы будем строить схемы (чертежи) наших данных.
*   `from typing import Dict, Any` — Встроенный в Python модуль для типизации. `Dict` означает словарь (ключ-значение), `Any` означает "любой тип данных" (строка, число, другой словарь).

### Блок 1. Инициализация
```python
app = FastAPI(title="Swag Labs Mock API")
```
*   `app = FastAPI(...)` — Мы создаем объект (инстанс) сервера и называем его `app`. Веб-сервер `Uvicorn` при запуске будет искать именно эту переменную.
*   `title="..."` — Заголовок. FastAPI автоматически сгенерирует для нас красивую веб-страничку с документацией по адресу `http://127.0.0.1:8000/docs`, и там будет красоваться это имя.

### Блок 2. Схема данных (Pydantic Контракт)
```python
class Customer(BaseModel):
    first_name: str
    last_name: str
    postal_code: str
```
*   **Что это:** Это схема (контракт) того, как должен выглядеть правильный JSON-объект, который тест отправляет на сервер.
*   **Как работает:** Если тест отправит JSON `{"first_name": "Ivan"}`, но забудет `last_name`, FastAPI не пропустит такой запрос внутрь функции. Он сам вернет тесту ошибку `422 Unprocessable Entity` (Ошибка валидации). Это спасает нас от написания кучи проверок `if not last_name: ...`.

### Блок 3. База данных (In-Memory)
```python
fake_db: Dict[int, Customer] = {}
current_id: int = 1
```
*   `fake_db` — Это наша "База данных", которая живет только в оперативной памяти компьютера. Это обычный Python словарь (`{}`). 
*   `Dict[int, Customer]` — Мы строго говорим, что ключом в этом словаре всегда будет число (`int` - ID покупателя), а значением — строго объект `Customer` из блока 2.
*   `current_id = 1` — Переменная-счетчик. Каждый новый покупатель будет получать уникальный ID: 1, 2, 3 и т.д.

### Блок 4. Создание данных: POST Запрос
```python
@app.post("/customers", status_code=201)
def create_customer(customer: Customer) -> Dict[str, Any]:
```
*   `@app.post` — **Декоратор (Маршрутизатор)**. Он говорит серверу: "Если к тебе придет запрос методом POST на адрес `/customers`, передай этот запрос в функцию ниже".
*   `status_code=201` — Если всё пройдет успешно, сервер автоматически ответит статусом "201 Created" (Создано), вместо стандартного 200 OK.
*   `def create_customer(...)` — Сама функция обработки. 
*   `customer: Customer` — Входящие данные. FastAPI берет сырой JSON из сети, проверяет его по классу `Customer` (Блок 2) и отдает нам в виде готового Python-объекта.
*   `-> Dict[str, Any]` — Обещание, что в конце функция вернет словарь, где ключи - строки (`str`), а значения - что угодно (`Any`).

```python
    global current_id
    fake_db[current_id] = customer
    response = {"id": current_id, **customer.model_dump()}
    current_id += 1
    return response
```
*   `global current_id` — Говорит функции: "Используй глобальный счетчик, который мы объявили выше".
*   `fake_db[current_id] = customer` — Сохраняем покупателя в нашу фейковую БД под текущим номером (например, `fake_db[1] = ...`).
*   `**customer.model_dump()` — Магия Pydantic. `.model_dump()` превращает объект `Customer` обратно в обычный словарь Python. А две звездочки `**` "распаковывают" этот словарь. Итог: мы объединяем ID и данные пользователя в один большой словарь `response`.
*   `return response` — Сервер берет этот словарь, автоматически превращает его в JSON и отдает по сети обратно нашему автотесту.

### Блок 5. Получение данных: GET Запрос
```python
@app.get("/customers/{customer_id}")
def get_customer(customer_id: int) -> Customer:
```
*   `@app.get` — Слушает запросы на получение данных.
*   `"/customers/{customer_id}"` — Динамический путь (Path Parameter). Если тест перейдет на `/customers/5`, FastAPI вытащит цифру `5` и передаст её в функцию в переменную `customer_id`.

```python
    if customer_id not in fake_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    return fake_db[customer_id]
```
*   `if customer_id not in fake_db:` — Проверка: есть ли такой ID (ключ) в нашей базе (словаре `fake_db`).
*   `raise HTTPException(...)` — Если нет, мы выбрасываем исключение. Тест получит ответ "404 Not Found" с текстом "Customer not found".
*   `return fake_db[...]` — Если есть, мы просто отдаем объект. FastAPI снова сам превратит его в правильный JSON.

---

## 3. Разбор настройки Playwright и автозапуска сервера (conftest.py)

Чтобы тестам было удобно стучаться в API, мы создали для них инструменты (фикстуры) в файле `conftest.py`.

Важное улучшение: тесты теперь **сами поднимают mock-сервер**. Это значит, что команда `poetry run pytest` является самодостаточной. Пользователю не нужно держать второй терминал с `uvicorn`.

### 3.1. Ожидание готовности сервера

```python
def _wait_for_mock_server(mock_url: str, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    healthcheck_url = f"{mock_url.rstrip('/')}/docs"

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(healthcheck_url, timeout=1):
                return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.2)

    raise RuntimeError(f"Mock API server did not start at {mock_url}")
```

*   `_wait_for_mock_server` — маленькая служебная функция, которая не дает тесту стартовать раньше сервера.
*   `healthcheck_url = ... /docs` — FastAPI автоматически создает страницу документации `/docs`; если она открывается, значит приложение уже живое.
*   `deadline` и `timeout` — защита от бесконечного ожидания. Если сервер не поднялся за 10 секунд, тест падает с понятной ошибкой.
*   `urllib.request.urlopen(...)` — стандартный HTTP-запрос без дополнительных зависимостей.
*   `time.sleep(0.2)` — небольшая пауза между попытками, чтобы не спамить локальный порт.

### 3.2. Фикстура `mock_api_server`

```python
@pytest.fixture(scope="session")
def mock_api_server() -> Generator[str, None, None]:
    mock_url = config.MOCK_SERVER_URL.rstrip("/")
    parsed_url = urlparse(mock_url)

    if not parsed_url.hostname or not parsed_url.port:
        raise ValueError(f"Некорректный MOCK_SERVER_URL: {mock_url}")

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "mock_server.main:app",
            "--host",
            parsed_url.hostname,
            "--port",
            str(parsed_url.port),
            "--log-level",
            "warning",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_mock_server(mock_url)
        yield mock_url
    finally:
        process.terminate()
        process.wait(timeout=5)
```

*   `scope="session"` — сервер поднимается один раз на всю тестовую сессию конкретного pytest worker, а не перед каждым тестом. Это быстрее и ближе к реальной инфраструктуре.
*   `config.MOCK_SERVER_URL` — адрес берется из единого конфигурационного слоя Pydantic, а не хардкодится в тесте.
*   `urlparse(mock_url)` — разбирает строку `http://127.0.0.1:8000` на hostname и port.
*   `subprocess.Popen(...)` — запускает `uvicorn` отдельным процессом, чтобы сервер работал параллельно с тестами.
*   `sys.executable` — гарантирует, что `uvicorn` запускается тем же Python из Poetry-окружения, а не случайным системным Python.
*   `python -m uvicorn mock_server.main:app` — стандартный способ запуска ASGI-приложения. `mock_server.main` — путь к файлу, `app` — объект FastAPI внутри файла.
*   `stdout=subprocess.DEVNULL` и `stderr=subprocess.DEVNULL` — скрывают шум сервера из тестового вывода. Если нужно расследовать проблему запуска, эти строки можно временно убрать.
*   `yield mock_url` — возвращает тестам готовый URL, а после завершения тестовой сессии выполняет блок `finally`.
*   `process.terminate()` — корректно останавливает локальный сервер, чтобы порт `8000` не оставался занятым после прогона.

### 3.3. Фикстура `mock_api_context`

```python
@pytest.fixture
def mock_api_context(
    playwright: Playwright,
    mock_api_server: str,
) -> Generator[APIRequestContext, None, None]:
    request_context = playwright.request.new_context(base_url=mock_api_server)
    yield request_context
    request_context.dispose()
```
*   `@pytest.fixture` — Делает эту функцию доступной для любого теста в проекте.
*   `(playwright: Playwright)` — Мы просим Pytest дать нам доступ к "движку" Playwright.
*   `mock_api_server: str` — Зависимость от серверной фикстуры. Pytest сначала поднимет сервер, потом создаст API-клиент.
*   `-> APIRequestContext` — Возвращаем специальный объект Playwright, который предназначен именно для работы с сетью без открытия браузера.
*   `.new_context(base_url=...)` — Создаем HTTP-клиента. Указывая `base_url`, мы избавляем себя от необходимости писать `http://127.0.0.1:8000/customers` в тестах. Мы будем писать просто `/customers`.
*   `yield request_context` — Отдаем инструмент тесту. Тест выполняется.
*   `.dispose()` — После того как тест завершился, закрываем все сетевые соединения, чтобы не засорять память.

---

## 4. Разбор API Теста: `tests/test_mock_api.py`

Теперь посмотрим, как тест общается с сервером по паттерну **AAA (Arrange, Act, Assert)**.

```python
def test_create_and_get_customer(mock_api_context: APIRequestContext) -> None:
```
*   В скобках мы требуем нашу фикстуру `mock_api_context` из `conftest.py`. Теперь у нас есть "пульт управления" API.

### 1. ARRANGE (Подготовка)
```python
    new_customer = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "postal_code": "123456"
    }
```
*   Формируем Python словарь с данными. Ключи строго совпадают с полями класса `Customer` на сервере.

### 2. ACT (Действие: Отправляем POST)
```python
    post_response = mock_api_context.post("/customers", data=new_customer)
```
*   `.post("/customers", ...)` — Отправляем данные. Playwright автоматически допишет спереди `http://127.0.0.1:8000`.
*   `data=new_customer` — Playwright сам превратит этот Python-словарь в строку формата JSON и прицепит заголовки (Headers) `Content-Type: application/json`.
*   `post_response` — В эту переменную сохраняется весь ответ от сервера (статус, заголовки, тело ответа).

### 3. ASSERT (Проверки: Что вернул POST)
```python
    assert post_response.ok, f"Ошибка: {post_response.status}"
    assert post_response.status == 201, "Ожидался статус 201 Created"
```
*   `assert post_response.ok` — Свойство `.ok` возвращает `True`, если сервер ответил статусом в диапазоне 200-299. Если статус 400 или 500, тест упадет с понятным текстом ошибки.
*   `assert post_response.status == 201` — Строгая проверка, что сервер ответил именно 201-м статусом, как мы прописали в `main.py` (`status_code=201`).

```python
    post_data = post_response.json()
    customer_id = post_data["id"]
```
*   `.json()` — Берет сырой текст ответа от сервера и превращает его в удобный словарь Python.
*   `customer_id` — Вытаскиваем сгенерированный сервером ID, чтобы использовать его в следующем шаге.

### 4. ACT (Действие: Запрашиваем GET)
```python
    get_response = mock_api_context.get(f"/customers/{customer_id}")
```
*   Отправляем GET запрос, подставляя в конец строки ID нашего созданного пользователя (например, `/customers/1`).

### 5. ASSERT (Проверки: Совпадают ли данные)
```python
    assert get_response.status == 200, "Ожидался статус 200 OK"
    get_data = get_response.json()
    
    assert get_data["first_name"] == new_customer["first_name"]
    assert get_data["last_name"] == new_customer["last_name"]
    assert get_data["postal_code"] == new_customer["postal_code"]
```
*   Проверяем, что сервер вернул статус 200.
*   Вытаскиваем JSON из ответа (`get_data`).
*   **Ключевая проверка:** Сравниваем то, что вернул сервер (`get_data`), с тем, что мы отправляли изначально в самом начале теста (`new_customer`).
*   **Почему мы используем питоновский `assert`, а не Playwright `expect`?** `expect()` нужен для работы с UI (браузером), так как он умеет "ждать" пока кнопка появится на экране. В API ждать не нужно — ответ приходит моментально и целиком, поэтому стандартный быстрый `assert` здесь подходит идеально.

---

## 5. Запуск (Workflow)

Основной способ запуска теперь один:

```bash
poetry run pytest tests/test_mock_api.py -v -s
```
Фикстура сама:
*   прочитает `MOCK_SERVER_URL`;
*   запустит `uvicorn`;
*   дождется доступности `/docs`;
*   создаст `APIRequestContext`;
*   остановит сервер после завершения тестов.

Если нужно вручную посмотреть Swagger UI FastAPI, сервер можно запустить отдельно:
```bash
poetry run uvicorn mock_server.main:app --reload
```

После этого откройте в браузере:
```text
http://127.0.0.1:8000/docs
```

## 6. Типичные ошибки и диагностика

### `ECONNREFUSED 127.0.0.1:8000`
Означает, что тест попытался обратиться к серверу, но на порту `8000` никто не слушает. Сейчас это чаще всего значит, что `uvicorn` не смог стартовать. Проверьте, установлен ли пакет `uvicorn` и нет ли ошибки импорта в `mock_server/main.py`.

### `Address already in use`
Означает, что порт `8000` уже занят другим процессом. Обычно это происходит, если вы вручную запустили `poetry run uvicorn mock_server.main:app --reload` и параллельно запустили тесты. Остановите ручной сервер или временно задайте другой `MOCK_SERVER_URL`.

### Тест проходит отдельно, но нестабилен в параллельном запуске
При `pytest-xdist` тесты выполняются в нескольких worker-процессах. Для большого количества API-тестов лучше выделять каждому worker свой порт или запускать один общий тестовый сервис заранее в CI. В текущем учебном проекте один API-тест проходит стабильно, но это ограничение важно помнить при масштабировании.
