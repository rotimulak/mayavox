"""
Клиент для взаимодействия с Hydra AI API.

Обеспечивает отправку запросов к API и обработку ответов.
"""

import sys

try:
    import requests
except ImportError:
    print("Ошибка: Необходимо установить библиотеку requests")
    print("Установите её командой: pip install requests")
    sys.exit(1)


class HydraAIClient:
    """Клиент для Hydra AI API (OpenAI-compatible)"""

    def __init__(self, api_key, api_url, model='gpt-4o-mini'):
        """
        Инициализация клиента.

        Args:
            api_key: API ключ для авторизации
            api_url: URL эндпоинта API
            model: Название модели для использования
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

        # Создаем сессию с предустановленными заголовками
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def chat_completion(self, messages, temperature=0.7, max_tokens=2000):
        """
        Отправить запрос на генерацию текста.

        Args:
            messages: Массив сообщений в формате OpenAI
                      [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            temperature: Степень креативности (0.0-2.0)
            max_tokens: Максимальное количество токенов в ответе

        Returns:
            dict: Ответ от API в формате OpenAI

        Raises:
            requests.exceptions.HTTPError: При ошибках HTTP (401, 429, 500 и т.д.)
            requests.exceptions.Timeout: При превышении времени ожидания
            requests.exceptions.RequestException: При других ошибках сети
        """
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        try:
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=60  # 60 секунд таймаут
            )

            # Проверяем статус ответа
            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout("Превышено время ожидания ответа от API")

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if status_code == 401:
                raise requests.exceptions.HTTPError(
                    "Ошибка авторизации API (401). Проверьте API ключ.",
                    response=e.response
                )
            elif status_code == 429:
                raise requests.exceptions.HTTPError(
                    "Превышен лимит запросов (429). Попробуйте позже.",
                    response=e.response
                )
            elif status_code >= 500:
                raise requests.exceptions.HTTPError(
                    f"Ошибка сервера API ({status_code}). Попробуйте позже.",
                    response=e.response
                )
            else:
                raise requests.exceptions.HTTPError(
                    f"Ошибка API ({status_code}): {e.response.text}",
                    response=e.response
                )

    def extract_message_content(self, response):
        """
        Извлечь текст ответа из response объекта.

        Args:
            response: Ответ от chat_completion()

        Returns:
            str: Текст ответа от AI
        """
        try:
            return response['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise ValueError(f"Неверный формат ответа API: {e}")

    def __repr__(self):
        """Строковое представление клиента (без API ключа)"""
        return f"HydraAIClient(model={self.model}, api_url={self.api_url})"
