"""
Модуль управления конфигурацией Telegram-бота.

Загружает настройки из .env файла и валидирует их.
"""

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("Ошибка: Необходимо установить библиотеку python-dotenv")
    print("Установите её командой: pip install python-dotenv")
    sys.exit(1)


class BotConfig:
    """Конфигурация бота из .env файла"""

    def __init__(self, env_path=None):
        """
        Загрузить конфигурацию из .env файла.

        Args:
            env_path: Путь к .env файлу (опционально)
        """
        # Загрузить .env файл
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        # Обязательные настройки
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.api_key = os.getenv('API_KEY')
        self.api_url = os.getenv('API_URL')

        # Опциональные настройки с значениями по умолчанию
        self.model = os.getenv('HYDRA_MODEL', 'gpt-4o-mini')
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))

        # Пути (относительно директории запуска)
        self.result_dir = Path(os.getenv('RESULT_DIR', '../result'))
        self.system_prompt_file = Path(os.getenv('SYSTEM_PROMPT_FILE', 'config/system_prompt.txt'))

        # Валидация
        self._validate()

    def _validate(self):
        """Валидировать обязательные параметры"""
        errors = []

        if not self.telegram_token:
            errors.append("TELEGRAM_BOT_TOKEN не найден в .env")

        if not self.api_key:
            errors.append("API_KEY не найден в .env")

        if not self.api_url:
            errors.append("API_URL не найден в .env")

        if not self.result_dir.exists():
            errors.append(f"Директория с контекстом не найдена: {self.result_dir}")

        if not self.system_prompt_file.exists():
            errors.append(f"Файл system prompt не найден: {self.system_prompt_file}")

        if errors:
            print("[ERROR] Ошибки конфигурации:")
            for error in errors:
                print(f"  - {error}")
            print("\nПроверьте файл .env и пути к файлам.")
            sys.exit(1)

    def load_system_prompt(self):
        """Загрузить system prompt из файла"""
        try:
            with open(self.system_prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"[ERROR] Ошибка чтения system prompt: {e}")
            sys.exit(1)

    def __repr__(self):
        """Строковое представление конфигурации (без секретов)"""
        return (
            f"BotConfig(\n"
            f"  model={self.model},\n"
            f"  temperature={self.temperature},\n"
            f"  max_tokens={self.max_tokens},\n"
            f"  result_dir={self.result_dir},\n"
            f"  system_prompt_file={self.system_prompt_file}\n"
            f")"
        )
