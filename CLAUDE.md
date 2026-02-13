# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a workspace for processing Telegram chat exports. The primary functionality is converting Telegram HTML export files to readable text format without information loss.

## Project Structure

```
masterskaya/
├── .claude/              # Claude Code configuration
│   └── instructions.md   # Project-specific instructions
├── app/                  # Telegram bot application
│   ├── config/           # Bot configuration
│   │   └── system_prompt.txt
│   ├── bot_config.py     # Configuration loader
│   ├── context_loader.py # Context file loader
│   ├── hydra_client.py   # Hydra AI API client
│   ├── message_handler.py # Message processing
│   └── telegram_bot.py   # Main bot entry point
├── utils/                # Utility scripts
│   └── html_to_txt.py   # Telegram HTML to TXT converter
├── data/                 # Processed output files
├── result/               # Analysis results (bot context)
├── ChatExport_*/         # Raw Telegram exports (HTML + media)
└── .env                  # Environment variables (API keys)
```

**Important:** All new utility scripts must be created in `utils/` directory per project conventions defined in `.claude/instructions.md`.

## Running Utilities

### HTML to TXT Converter

Convert Telegram HTML exports to text format:

```bash
# Basic usage
PYTHONIOENCODING=utf-8 python utils/html_to_txt.py "path/to/messages.html"

# Specify custom output path
PYTHONIOENCODING=utf-8 python utils/html_to_txt.py "path/to/messages.html" "path/to/output.txt"
```

**Critical:** Always use `PYTHONIOENCODING=utf-8` prefix on Windows when running Python scripts that output Cyrillic text. Without this, the script will fail with `UnicodeEncodeError` due to Windows console encoding (cp1252).

## Dependencies

- **Python 3.x** (tested with 3.12)
- **beautifulsoup4** (4.13.4+) - Required for HTML parsing

Install dependencies:
```bash
pip install beautifulsoup4
```

## Platform Considerations

This project is developed on Windows (`win32`). Be aware of:

1. **Character Encoding:** Windows console uses cp1252 by default. Always set `PYTHONIOENCODING=utf-8` when running Python scripts with Cyrillic or other non-ASCII output.

2. **Path Separators:** Use appropriate path handling for Windows (backslashes or Path objects from pathlib).

## Architecture Notes

### HTML to TXT Converter (`utils/html_to_txt.py`)

The converter parses Telegram's HTML export structure and extracts:
- Message metadata (date, time, sender, message ID)
- Regular and service messages
- Forwarded messages and replies
- Text content with preserved formatting (line breaks)
- Media references (photos, videos, audio, documents, stickers)
- Reactions with counts

**Key functions:**
- `parse_message(msg_div)` - Extracts all information from a message div element
- `process_text_element(text_elem)` - Preserves text formatting by handling `<br>` tags
- `process_media(media_wrap)` - Handles all media types with appropriate icons
- `convert_html_to_txt(html_path, output_path)` - Main conversion orchestrator

The parser uses BeautifulSoup4 with CSS class selectors to navigate Telegram's HTML structure (`message`, `body`, `from_name`, `text`, `media_wrap`, etc.).

## Telegram Bot (app/)

### Overview

Telegram-бот с интеграцией Hydra AI для ответов на вопросы на основе анализа чата проекта "Майя". Бот загружает все файлы из `result/` в качестве контекста и использует Hydra AI API для генерации ответов.

### Quick Start

1. **Установить зависимости:**
```bash
pip install python-telegram-bot requests python-dotenv
```

2. **Настроить .env файл:**
```env
# Hydra AI
API_URL=https://api.hydraai.ru/v1/chat/completions
API_KEY=sk-hydra-ai-your-key-here
HYDRA_MODEL=gpt-4o-mini
TEMPERATURE=0.7
MAX_TOKENS=2000

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Paths
RESULT_DIR=result
SYSTEM_PROMPT_FILE=app/config/system_prompt.txt
```

3. **Запустить бота:**
```bash
cd app
python telegram_bot.py
```

### Архитектура

**Stateless Design:**
- Каждый запрос независим, нет истории диалога
- Весь контекст из `result/` загружается при старте бота в память (~87 KB)
- На каждый вопрос отправляется: system prompt + полный контекст + вопрос пользователя

**Компоненты:**

1. **[bot_config.py](app/bot_config.py)** - Загрузка и валидация конфигурации из .env
2. **[context_loader.py](app/context_loader.py)** - Загрузка всех 7 markdown файлов из result/
3. **[hydra_client.py](app/hydra_client.py)** - HTTP клиент для Hydra AI API (OpenAI-compatible)
4. **[message_handler.py](app/message_handler.py)** - Форматирование запросов и разделение длинных ответов
5. **[telegram_bot.py](app/telegram_bot.py)** - Основная логика бота, обработка команд и сообщений

**Поток обработки:**
```
Пользователь → Telegram → Валидация → "typing..." →
→ Формирование запроса → Hydra AI API → Обработка ответа →
→ Разделение (если >4096 символов) → Отправка пользователю
```

### Конфигурация

**System Prompt ([app/config/system_prompt.txt](app/config/system_prompt.txt)):**
Определяет поведение AI - отвечать только на основе контекста, ссылаться на файлы, не придумывать информацию.

**Переменные окружения (.env):**
- `API_KEY` - API ключ Hydra AI (обязательно)
- `API_URL` - URL эндпоинта (обязательно)
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота (обязательно)
- `HYDRA_MODEL` - модель AI (по умолчанию: gpt-4o-mini)
- `TEMPERATURE` - креативность ответов 0.0-2.0 (по умолчанию: 0.7)
- `MAX_TOKENS` - максимум токенов в ответе (по умолчанию: 2000)

### Команды бота

- `/start` - Приветствие и описание возможностей
- `/help` - Справка по использованию
- Любое текстовое сообщение - вопрос к AI

### Обработка ошибок

Бот gracefully обрабатывает:
- **Timeout** - превышение времени ожидания ответа
- **401 Unauthorized** - неверный API ключ
- **429 Rate Limit** - превышение лимита запросов
- **5xx Server Error** - ошибки сервера Hydra AI
- **Длинные ответы** - автоматическое разделение на части по границам параграфов

### Логирование

Бот логирует:
- Запросы пользователей (ID, username, первые 100 символов)
- Статистику токенов (prompt + completion + total)
- Ошибки с полным traceback
- Успешные ответы (количество частей сообщения)

### Особенности

**Windows-специфичные:**
- UTF-8 encoding для всех файловых операций
- Использование pathlib.Path для кроссплатформенности
- PYTHONIOENCODING не требуется (бот работает как сервис)

**Безопасность:**
- API ключи хранятся в .env (не коммитить!)
- Секреты никогда не логируются
- Публичный доступ (без авторизации)

### Развертывание

**На сервере:**

1. Клонировать репозиторий
2. Установить зависимости: `pip install python-telegram-bot requests python-dotenv`
3. Настроить .env файл
4. Запустить: `cd app && python telegram_bot.py`

**Как сервис (Windows):**
- Использовать NSSM (Non-Sucking Service Manager)
- Или Task Scheduler с "Run whether user is logged on or not"

**Мониторинг:**
- Логи выводятся в console (можно перенаправить в файл)
- Статистика API доступна на dashboard.hydraai.ru
