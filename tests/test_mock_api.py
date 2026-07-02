from playwright.sync_api import APIRequestContext
from loguru import logger

def test_create_and_get_customer(mock_api_context: APIRequestContext) -> None:
    """
    Тест проверяет полный цикл работы с API: создание сущности (POST) 
    и последующее ее извлечение (GET) с проверкой сохраненности данных.
    """
    
    # 1. Arrange (Подготовка данных)
    # В реальном Enterprise проекте эти данные генерировались бы через библиотеку Faker 
    # или брались из pydantic-модели data/models.py
    new_customer = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "postal_code": "123456"
    }
    
    # 2. Act: Создание покупателя (POST-запрос)
    logger.info("Отправляем POST запрос для создания нового покупателя...")
    # Обрати внимание: мы используем аргумент `data`, Playwright сам добавит хедер 'Content-Type: application/json'
    post_response = mock_api_context.post("/customers", data=new_customer)
    
    # 3. Assert: Проверки ответа на POST
    # Встроенный метод .ok вернет True для статусов 200-299.
    assert post_response.ok, f"Ошибка POST запроса. Статус: {post_response.status}"
    assert post_response.status == 201, "Ожидался статус 201 Created"
    
    # Извлекаем JSON-ответ и сохраняем сгенерированный ID
    post_data = post_response.json()
    logger.debug(f"Ответ сервера при создании: {post_data}")
    customer_id = post_data["id"]
    
    # 4. Act: Запрос созданного покупателя (GET-запрос)
    logger.info(f"Отправляем GET запрос для извлечения покупателя с ID: {customer_id}")
    # Playwright подставит этот путь к base_url (http://127.0.0.1:8000/customers/1)
    get_response = mock_api_context.get(f"/customers/{customer_id}")
    
    # 5. Assert: Проверки ответа на GET
    assert get_response.ok, f"Ошибка GET запроса. Статус: {get_response.status}"
    assert get_response.status == 200, "Ожидался статус 200 OK"
    
    get_data = get_response.json()
    logger.success("Данные по покупателю успешно извлечены с сервера")
    
    # Сравниваем то, что вернул сервер, с тем, что мы отправляли изначально
    # Здесь встроенный питоновский assert работает отлично, так как это проверка данных, а не элементов UI.
    assert get_data["first_name"] == new_customer["first_name"]
    assert get_data["last_name"] == new_customer["last_name"]
    assert get_data["postal_code"] == new_customer["postal_code"]