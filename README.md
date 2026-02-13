# MayaVox

Инструментарий для анализа Telegram-чатов проекта "Майя".

## Структура проекта

```
mayavox/
├── utils/                # 1. Анализ чата
├── site/                 # 2. Сайт документации
└── app/                  # 3. Telegram-бот
```

---

## 1. Анализ чата

Извлечение структурированной информации из истории Telegram-чата.

### Методология

**Фаза 1: Подготовка данных**

| Шаг | Описание | Инструмент |
|-----|----------|------------|
| HTML → TXT | Конвертация Telegram-экспорта в текст | BeautifulSoup4 |
| Голосовые → текст | Транскрибация голосовых сообщений | Whisper |
| Видео → текст | Извлечение аудио и транскрибация | FFmpeg + Whisper |
| Документы → MD | Конвертация вложений | Pandoc |

**Фаза 2: Анализ содержания**

- **Участники** — кто есть кто, роли, активность
- **Проекты** — что обсуждалось, описания
- **Эволюция концепции** — как менялось видение проекта
- **Позиции участников** — кто что думал и когда

### Использование

```bash
pip install beautifulsoup4

# Конвертация HTML экспорта в текст
PYTHONIOENCODING=utf-8 python utils/html_to_txt.py "ChatExport/messages.html"

# Извлечение аудио из экспорта
python utils/extract_audio.py "ChatExport/"

# Транскрибация аудио
python utils/transcribe_audio.py

# Конвертация PDF в Markdown
python utils/pdf_to_md.py "document.pdf"
```

---

## 2. Сайт документации

Статический сайт на Docusaurus с результатами анализа.

### Установка

```bash
cd site
npm install
```

### Разработка

```bash
npm start
```

### Сборка

```bash
npm run build
```

### Деплой

```bash
python ../utils/deploy.py
```

---

## 3. Telegram-бот

Бот для ответов на вопросы по результатам анализа через Hydra AI.

### Установка

```bash
pip install python-telegram-bot requests python-dotenv
```

### Настройка

```bash
cp .env.example .env
```

Заполните в `.env`:
- `API_KEY` — ключ Hydra AI
- `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather

### Запуск

```bash
cd app && python telegram_bot.py
```

### Команды

- `/start` — Приветствие
- `/help` — Справка
- Любой текст — Вопрос к AI

---

## Технологии

| Компонент | Стек |
|-----------|------|
| Анализ чата | Python 3.12, BeautifulSoup4, Whisper, FFmpeg |
| Сайт | Docusaurus, React, TypeScript |
| Бот | python-telegram-bot, Hydra AI API |

## Лицензия

MIT
