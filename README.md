# MayaVox

Инструментарий для анализа Telegram-чатов и Telegram-бот для ответов на вопросы по результатам анализа.

## Что это?

Проект решает задачу извлечения структурированной информации из истории Telegram-чата:

1. **Подготовка данных** — конвертация экспорта в текст, транскрибация аудио/видео
2. **Анализ содержания** — выделение участников, проектов, позиций, эволюции идей
3. **Доступ к результатам** — Telegram-бот для вопросов по анализу

## Методология

### Фаза 1: Подготовка данных

| Шаг | Описание | Инструмент |
|-----|----------|------------|
| HTML → TXT | Конвертация Telegram-экспорта в текст | BeautifulSoup4 |
| Голосовые → текст | Транскрибация голосовых сообщений | Whisper |
| Видео → текст | Извлечение аудио и транскрибация | FFmpeg + Whisper |
| Документы → MD | Конвертация вложений | Pandoc |

### Фаза 2: Анализ содержания

- **Участники** — кто есть кто, роли, активность
- **Проекты** — что обсуждалось, описания
- **Эволюция концепции** — как менялось видение проекта
- **Позиции участников** — кто что думал и когда

## Быстрый старт

### Установка

```bash
pip install python-telegram-bot requests python-dotenv beautifulsoup4
```

### Настройка

```bash
cp .env.example .env
# Заполните API_KEY и TELEGRAM_BOT_TOKEN
```

### Запуск бота

```bash
cd app && python telegram_bot.py
```

## Утилиты

```bash
# Конвертация HTML экспорта в текст
PYTHONIOENCODING=utf-8 python utils/html_to_txt.py "ChatExport/messages.html"

# Извлечение аудио из экспорта
python utils/extract_audio.py "ChatExport/"

# Транскрибация аудио
python utils/transcribe_audio.py

# Конвертация PDF в Markdown
python utils/pdf_to_md.py "document.pdf"
```

## Структура

```
mayavox/
├── app/                  # Telegram-бот (Hydra AI)
├── utils/                # Утилиты обработки
├── result/               # Результаты анализа
└── site/                 # Документация (Docusaurus)
```

## Технологии

- **Python 3.12** — основной язык
- **BeautifulSoup4** — парсинг HTML
- **Whisper** — транскрибация аудио
- **FFmpeg** — обработка видео
- **Hydra AI** — LLM для бота (OpenAI-совместимый API)
- **python-telegram-bot** — Telegram API

## Лицензия

MIT
