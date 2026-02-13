# Telegram Bot с Hydra AI

Telegram-бот для ответов на вопросы на основе анализа чата проекта "Майя".

## Быстрый старт

### 1. Установить зависимости

```bash
pip install python-telegram-bot requests python-dotenv
```

### 2. Настроить .env файл

Скопируйте `.env.example` в `.env` и заполните:

```bash
# В корне проекта
cp .env.example .env
```

Откройте `.env` и укажите:
- `API_KEY` - ваш API ключ от Hydra AI (https://dashboard.hydraai.ru/)
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота (получить у @BotFather)

### 3. Запустить бота

```bash
cd app
python telegram_bot.py
```

## Структура

```
app/
├── config/
│   └── system_prompt.txt    # Промпт для AI (можно редактировать)
├── bot_config.py            # Загрузка конфигурации из .env
├── context_loader.py        # Загрузка контекста из result/
├── hydra_client.py          # HTTP клиент для Hydra AI API
├── message_handler.py       # Обработка сообщений
└── telegram_bot.py          # Главный файл (точка входа)
```

## Как работает

1. При запуске бот загружает все 7 файлов из `result/` в память (~87 KB)
2. На каждый вопрос пользователя формируется запрос:
   - System prompt (правила поведения AI)
   - Полный контекст (все файлы из result/)
   - Вопрос пользователя
3. Запрос отправляется в Hydra AI API
4. Ответ возвращается пользователю (с разделением на части если >4096 символов)

**Важно:** Бот без истории диалога - каждый вопрос обрабатывается независимо.

## Команды бота

- `/start` - Приветствие и описание
- `/help` - Справка
- Любое текстовое сообщение - вопрос к AI

## Настройка

### System Prompt

Отредактируйте `config/system_prompt.txt` для изменения поведения AI.

### Параметры модели

В `.env` можно настроить:
- `HYDRA_MODEL` - модель (gpt-4o-mini, gpt-4o, и т.д.)
- `TEMPERATURE` - креативность ответов (0.0-2.0)
- `MAX_TOKENS` - максимум токенов в ответе

## Развертывание на сервере

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd masterskaya

# 2. Установить зависимости
pip install python-telegram-bot requests python-dotenv

# 3. Настроить .env
cp .env.example .env
nano .env  # или любой редактор

# 4. Запустить
cd app
python telegram_bot.py

# Для фонового запуска (Linux)
nohup python telegram_bot.py > bot.log 2>&1 &

# Для Windows - использовать NSSM или Task Scheduler
```

## Логи

Бот выводит логи в консоль:
- Запросы пользователей
- Статистика токенов
- Ошибки с traceback

Для сохранения в файл:
```bash
python telegram_bot.py > bot.log 2>&1
```

## Troubleshooting

**"TELEGRAM_BOT_TOKEN не найден в .env"**
- Проверьте, что `.env` файл существует в корне проекта
- Убедитесь, что переменная `TELEGRAM_BOT_TOKEN` заполнена

**"API_KEY не найден в .env"**
- Получите API ключ на https://dashboard.hydraai.ru/
- Добавьте в `.env` как `API_KEY=sk-hydra-ai-...`

**"Директория с контекстом не найдена: result"**
- Убедитесь, что директория `result/` существует
- Проверьте, что в ней есть все 7 markdown файлов

**Бот не отвечает**
- Проверьте логи на ошибки
- Убедитесь, что API ключ валиден
- Проверьте интернет-соединение

## Поддержка

Для дополнительной информации см. [CLAUDE.md](../CLAUDE.md) в корне проекта.
