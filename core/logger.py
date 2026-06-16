import sys
from loguru import logger

def setup_logger() -> None:
    """
    Настройка кастомного логгера для всего проекта.
    """
    # Удаляем стандартный обработчик, чтобы логи не дублировались
    logger.remove()

    # 1. Обработчик для консоли (stdout) - цветной, красивый вывод
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # 2. Обработчик для записи в файл (сохраняем полную историю тестов)
    logger.add(
        "logs/test_run.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="5 MB",    # Создавать новый файл, когда старый достигнет 5 Мегабайт
        compression="zip"   # Старые логи автоматически архивируются
    )