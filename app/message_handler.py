"""
Обработка сообщений для Telegram-бота.

Форматирование запросов к AI и обработка ответов.
"""


def build_messages(system_prompt, context, user_question):
    """
    Построить массив сообщений для Hydra AI API.

    Args:
        system_prompt: System prompt для AI
        context: Контекст из markdown файлов
        user_question: Вопрос пользователя

    Returns:
        list: Массив сообщений в формате OpenAI
    """
    messages = [
        {
            "role": "system",
            "content": f"{system_prompt}\n\n# КОНТЕКСТ\n\n{context}"
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    return messages


def split_long_message(text, max_length=4000):
    """
    Разделить длинное сообщение на части по границам параграфов.

    Telegram имеет лимит 4096 символов на сообщение.
    Разбиваем на части по 4000 символов с учетом границ параграфов.

    Args:
        text: Текст для разделения
        max_length: Максимальная длина одной части (по умолчанию 4000)

    Returns:
        list: Список частей сообщения
    """
    # Если сообщение короткое, возвращаем как есть
    if len(text) <= max_length:
        return [text]

    parts = []
    current_part = ""

    # Разбиваем по параграфам (двойной перенос строки)
    paragraphs = text.split('\n\n')

    for paragraph in paragraphs:
        # Если добавление параграфа не превысит лимит
        if len(current_part) + len(paragraph) + 2 <= max_length:
            if current_part:
                current_part += '\n\n' + paragraph
            else:
                current_part = paragraph
        else:
            # Сохраняем текущую часть
            if current_part:
                parts.append(current_part.strip())

            # Если параграф сам по себе слишком длинный, разбиваем его
            if len(paragraph) > max_length:
                # Разбиваем по предложениям
                sentences = paragraph.split('. ')
                temp_part = ""

                for sentence in sentences:
                    if len(temp_part) + len(sentence) + 2 <= max_length:
                        if temp_part:
                            temp_part += '. ' + sentence
                        else:
                            temp_part = sentence
                    else:
                        if temp_part:
                            parts.append(temp_part.strip())
                        temp_part = sentence

                if temp_part:
                    current_part = temp_part
            else:
                current_part = paragraph

    # Добавляем последнюю часть
    if current_part:
        parts.append(current_part.strip())

    return parts


def format_error_message(error_type, details=None):
    """
    Форматировать сообщение об ошибке для пользователя.

    Args:
        error_type: Тип ошибки ('timeout', 'auth', 'rate_limit', 'server', 'unknown')
        details: Дополнительные детали (опционально)

    Returns:
        str: Отформатированное сообщение об ошибке
    """
    error_messages = {
        'timeout': "⏱ Превышено время ожидания ответа от сервера. Попробуйте позже.",
        'auth': "🔐 Ошибка авторизации API. Обратитесь к администратору.",
        'rate_limit': "⏰ Превышен лимит запросов. Подождите немного и попробуйте снова.",
        'server': "🔧 Ошибка сервера API. Попробуйте позже.",
        'unknown': "❌ Произошла ошибка при обработке запроса."
    }

    message = error_messages.get(error_type, error_messages['unknown'])

    if details:
        message += f"\n\nДетали: {details}"

    return message
