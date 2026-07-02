from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# 1. Инициализируем приложение FastAPI
app = FastAPI(title="Swag Labs Mock API")

# 2. Создаем Pydantic модель покупателя
class Customer(BaseModel):
    first_name: str
    last_name: str
    postal_code: str

# 3. Имитация базы данных в оперативной памяти (In-Memory DB)
fake_db: Dict[int, Customer] = {}
current_id: int = 1

# 4. Эндпоинт POST (Создание сущности)
@app.post("/customers", status_code=201)
def create_customer(customer: Customer) -> Dict[str, Any]:
    """
    Создает нового покупателя в базе данных.
    """
    global current_id
    
    # Сохраняем данные
    fake_db[current_id] = customer
    
    # Формируем ответ
    response = {"id": current_id, **customer.model_dump()}
    
    # Увеличиваем счетчик ID для следующего покупателя
    current_id += 1
    
    return response

# 5. Эндпоинт GET (Получение сущности)
@app.get("/customers/{customer_id}")
def get_customer(customer_id: int) -> Customer:
    """
    Возвращает данные покупателя по его ID.
    """
    # Проверяем, существует ли пользователь
    if customer_id not in fake_db:
        # Генерируем HTTP ошибку 404
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Возвращаем данные
    return fake_db[customer_id]