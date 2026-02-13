"""
Telegram-бот с интеграцией Hydra AI.

Отвечает на вопросы на основе контекста из директории result/.
"""

import sys
import io
import logging
from datetime import datetime

# Настройка UTF-8 для Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Импорт зависимостей с обработкой ошибок
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    from telegram.constants import ChatAction
except ImportError:
    print("Ошибка: Необходимо установить библиотеку python-telegram-bot")
    print("Установите её командой: pip install python-telegram-bot")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Ошибка: Необходимо установить библиотеку requests")
    print("Установите её командой: pip install requests")
    sys.exit(1)

# Импорт локальных модулей
from bot_config import BotConfig
from context_loader import load_all_context, get_context_stats
from hydra_client import HydraAIClient
from message_handler import build_messages, split_long_message, format_error_message


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Глобальные переменные (инициализируются при старте)
config = None
hydra_client = None
system_prompt = None
context = None


async def start_command(update: Update, context_obj):
    """Обработчик команды /start"""
    welcome_message = """
👋 Привет! Я бот-ассистент проекта Майя.

Я отвечаю на вопросы на основе анализа Telegram-чата разработчиков.

📚 Доступная информация:
• Методология анализа
• Участники проекта
• Описание проектов (MyBox, Personal AI, Бэкапы, Media Room, FAM)
• Эволюция видения проекта
• Позиции участников

Просто задайте мне вопрос!

Примеры вопросов:
• Кто является основным разработчиком?
• Что такое проект MyBox?
• Какие технологии используются?
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context_obj):
    """Обработчик команды /help"""
    help_message = """
ℹ️ Справка по боту

Я отвечаю на вопросы на основе предоставленного контекста.

**Доступные команды:**
/start - Приветствие и описание бота
/help - Эта справка

**Как пользоваться:**
Просто отправьте мне свой вопрос текстовым сообщением.

**Важно:**
• Я отвечаю только на основе информации из контекста
• Если информации нет, я честно об этом скажу
• Каждый вопрос обрабатывается независимо (без истории диалога)
"""
    await update.message.reply_text(help_message)


async def handle_message(update: Update, context_obj):
    """Обработчик текстовых сообщений от пользователей"""
    user_message = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"

    logger.info(f"[{user_id}] @{username}: {user_message[:100]}")

    # Отправляем действие "печатает..."
    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        # Формируем массив сообщений для API
        messages = build_messages(system_prompt, context, user_message)

        # Отправляем запрос к Hydra AI
        response = hydra_client.chat_completion(
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        # Извлекаем ответ
        answer = hydra_client.extract_message_content(response)

        # Логируем статистику
        usage = response.get('usage', {})
        logger.info(
            f"[{user_id}] Ответ получен. "
            f"Токены: {usage.get('prompt_tokens', 0)} + {usage.get('completion_tokens', 0)} "
            f"= {usage.get('total_tokens', 0)}"
        )

        # Разбиваем длинный ответ на части
        message_parts = split_long_message(answer)

        # Отправляем ответ (возможно несколько сообщений)
        for i, part in enumerate(message_parts):
            if i > 0:
                # Небольшая задержка между сообщениями
                await update.message.chat.send_action(ChatAction.TYPING)

            await update.message.reply_text(part)

        logger.info(f"[{user_id}] Ответ отправлен ({len(message_parts)} частей)")

    except requests.exceptions.Timeout:
        error_msg = format_error_message('timeout')
        await update.message.reply_text(error_msg)
        logger.error(f"[{user_id}] Timeout error")

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if hasattr(e.response, 'status_code') else None

        if status_code == 401:
            error_msg = format_error_message('auth')
        elif status_code == 429:
            error_msg = format_error_message('rate_limit')
        elif status_code and status_code >= 500:
            error_msg = format_error_message('server')
        else:
            error_msg = format_error_message('unknown', str(e))

        await update.message.reply_text(error_msg)
        logger.error(f"[{user_id}] HTTP error: {e}")

    except Exception as e:
        error_msg = format_error_message('unknown')
        await update.message.reply_text(error_msg)
        logger.error(f"[{user_id}] Unexpected error: {e}", exc_info=True)


async def error_handler(update: Update, context_obj):
    """Обработчик необработанных ошибок"""
    logger.error(f"Update {update} caused error {context_obj.error}", exc_info=context_obj.error)


def main():
    """Основная функция запуска бота"""
    global config, hydra_client, system_prompt, context

    print("=" * 80)
    print("🤖 Telegram Bot с Hydra AI интеграцией")
    print("=" * 80)

    # Загрузка конфигурации
    try:
        print("\n[1/4] Загрузка конфигурации...")
        config = BotConfig()
        print(f"  ✓ Модель: {config.model}")
        print(f"  ✓ Temperature: {config.temperature}")
        print(f"  ✓ Max tokens: {config.max_tokens}")
    except Exception as e:
        print(f"\n❌ Ошибка загрузки конфигурации: {e}")
        sys.exit(1)

    # Загрузка system prompt
    try:
        print("\n[2/4] Загрузка system prompt...")
        system_prompt = config.load_system_prompt()
        print(f"  ✓ Загружен из: {config.system_prompt_file}")
        print(f"  ✓ Длина: {len(system_prompt)} символов")
    except Exception as e:
        print(f"\n❌ Ошибка загрузки system prompt: {e}")
        sys.exit(1)

    # Загрузка контекста
    try:
        print("\n[3/4] Загрузка контекста...")
        context = load_all_context(str(config.result_dir))
        stats = get_context_stats(context)
        print(f"  ✓ Загружено файлов: 7")
        print(f"  ✓ Символов: {stats['chars']:,}")
        print(f"  ✓ Слов: {stats['words']:,}")
        print(f"  ✓ Строк: {stats['lines']:,}")
    except Exception as e:
        print(f"\n❌ Ошибка загрузки контекста: {e}")
        sys.exit(1)

    # Инициализация Hydra AI клиента
    try:
        print("\n[4/4] Инициализация Hydra AI клиента...")
        hydra_client = HydraAIClient(
            api_key=config.api_key,
            api_url=config.api_url,
            model=config.model
        )
        print(f"  ✓ API URL: {config.api_url}")
        print(f"  ✓ Модель: {config.model}")
    except Exception as e:
        print(f"\n❌ Ошибка инициализации клиента: {e}")
        sys.exit(1)

    # Создание приложения бота
    print("\n[*] Запуск Telegram бота...")
    application = Application.builder().token(config.telegram_token).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Запуск бота
    print(f"\n✅ Бот запущен успешно!")
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("\nБот работает. Нажмите Ctrl+C для остановки.\n")

    # Запуск polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹ Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)
