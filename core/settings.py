from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Класс для управления конфигурацией проекта.
    Pydantic автоматически прочитает файл .env и подставит значения в эти переменные.
    """
    
    # URL сайта
    BASE_URL: str
    
    # Логины
    STANDARD_USER: str
    LOCKED_OUT_USER: str
    PROBLEM_USER: str
    
    # Пароли
    VALID_PASSWORD: str

    # Настройка Pydantic: говорим ему, какой файл читать и в какой кодировке
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Игнорировать переменные окружения, которые есть в системе, но не описаны в классе
        extra="ignore" 
    )

# Создаем экземпляр настроек, который будем импортировать в тестах
config = Settings()
