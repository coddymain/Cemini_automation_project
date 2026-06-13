from pydantic import BaseModel

# Создаем "Чертеж" (Схему) нашего покупателя
class Customer(BaseModel):
    first_name: str
    last_name: str
    postal_code: str

# Создаем конкретного покупателя по этому чертежу
test_customer = Customer(first_name="Ivan", last_name="Ivanov", postal_code="123456")
# Теперь в тесте мы просто передаем весь объект:
# И редактор кода будет сам подсказывать тебе свойства: test_customer.first_name