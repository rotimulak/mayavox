#!/usr/bin/env python3
"""
Конвертер HTML экспорта Telegram чатов в текстовый формат.
Сохраняет всю информацию без потерь в читаемом виде.
"""

import sys
import os
from pathlib import Path
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Ошибка: Необходимо установить библиотеку BeautifulSoup4")
    print("Установите её командой: pip install beautifulsoup4")
    sys.exit(1)


def parse_message(msg_div):
    """Извлекает информацию из одного сообщения"""
    result = []

    # Проверяем тип сообщения
    is_service = 'service' in msg_div.get('class', [])

    if is_service:
        # Служебное сообщение (дата, системные уведомления)
        body = msg_div.find('div', class_='body')
        if body:
            text = body.get_text(strip=True)
            result.append(f"[{text}]")
        return result

    # Обычное сообщение
    body = msg_div.find('div', class_='body')
    if not body:
        return result

    # Дата и время
    date_elem = body.find('div', class_='date')
    if date_elem:
        date_text = date_elem.get('title', date_elem.get_text(strip=True))
        result.append(f"Дата: {date_text}")

    # Имя отправителя
    from_name = body.find('div', class_='from_name')
    if from_name:
        result.append(f"От: {from_name.get_text(strip=True)}")

    # Проверяем, есть ли ответ на сообщение
    reply_to = body.find('div', class_='reply_to')
    if reply_to:
        reply_text = reply_to.get_text(strip=True)
        result.append(f"↩️ {reply_text}")

    # Проверяем, есть ли пересланное сообщение
    forwarded = body.find('div', class_='forwarded')
    if forwarded:
        result.append("--- Пересланное сообщение ---")
        fwd_from = forwarded.find('div', class_='from_name')
        if fwd_from:
            result.append(f"От: {fwd_from.get_text(strip=True)}")
        fwd_text = forwarded.find('div', class_='text')
        if fwd_text:
            # Обрабатываем текст с сохранением переносов строк
            text = process_text_element(fwd_text)
            result.append(f"Текст: {text}")
        result.append("--- Конец пересланного сообщения ---")

    # Основной текст сообщения
    text_elem = body.find('div', class_='text', recursive=False)
    if text_elem:
        text = process_text_element(text_elem)
        if text:
            result.append(f"Текст: {text}")

    # Медиафайлы
    media_wrap = body.find('div', class_='media_wrap')
    if media_wrap:
        result.append(process_media(media_wrap))

    # Реакции
    reactions = body.find('span', class_='reactions')
    if reactions:
        reaction_list = []
        for reaction in reactions.find_all('span', class_='reaction'):
            emoji = reaction.find('span', class_='emoji')
            if emoji:
                emoji_text = emoji.get_text(strip=True)
                # Подсчитываем количество пользователей, поставивших реакцию
                userpics = reaction.find('span', class_='userpics')
                count = len(userpics.find_all('div', class_='userpic')) if userpics else 1
                reaction_list.append(f"{emoji_text}×{count}")
        if reaction_list:
            result.append(f"Реакции: {', '.join(reaction_list)}")

    return result


def process_text_element(text_elem):
    """Обрабатывает текстовый элемент, сохраняя форматирование"""
    # Заменяем <br> на переносы строк
    for br in text_elem.find_all('br'):
        br.replace_with('\n')

    # Получаем текст
    text = text_elem.get_text()

    # Удаляем лишние пробелы, но сохраняем переносы строк
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def process_media(media_wrap):
    """Обрабатывает медиафайлы"""
    result = []

    # Фото
    photo = media_wrap.find('a', class_='photo_wrap')
    if photo:
        href = photo.get('href', '')
        result.append(f"📷 Фото: {href}")

    # Видео
    video = media_wrap.find('a', class_='video_file_wrap')
    if video:
        href = video.get('href', '')
        video_title = media_wrap.find('div', class_='title')
        title = video_title.get_text(strip=True) if video_title else ''
        result.append(f"🎥 Видео: {title} ({href})")

    # Аудио/Голосовое сообщение
    audio = media_wrap.find('a', class_='audio_file')
    if audio:
        href = audio.get('href', '')
        audio_title = media_wrap.find('div', class_='title')
        title = audio_title.get_text(strip=True) if audio_title else ''
        duration = media_wrap.find('div', class_='duration')
        dur = duration.get_text(strip=True) if duration else ''
        result.append(f"🎵 Аудио: {title} {dur} ({href})")

    # Документы/Файлы
    file_wrap = media_wrap.find('div', class_='file')
    if file_wrap:
        file_name = file_wrap.find('div', class_='name')
        file_size = file_wrap.find('div', class_='details')
        name = file_name.get_text(strip=True) if file_name else ''
        size = file_size.get_text(strip=True) if file_size else ''
        result.append(f"📎 Файл: {name} ({size})")

    # Стикеры
    sticker = media_wrap.find('div', class_='sticker')
    if sticker:
        result.append("🎨 Стикер")

    return '\n'.join(result) if result else "📎 Медиафайл"


def convert_html_to_txt(html_path, output_path=None):
    """
    Конвертирует HTML файл в текстовый формат

    Args:
        html_path: путь к HTML файлу
        output_path: путь для сохранения TXT (по умолчанию - то же имя с расширением .txt)
    """
    html_path = Path(html_path)

    if not html_path.exists():
        print(f"Ошибка: Файл {html_path} не найден")
        sys.exit(1)

    # Определяем путь для выходного файла
    if output_path is None:
        output_path = html_path.with_suffix('.txt')
    else:
        output_path = Path(output_path)

    print(f"Читаю файл: {html_path}")

    # Читаем HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Парсим HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Извлекаем заголовок чата
    header = soup.find('div', class_='page_header')
    chat_title = "Экспорт чата"
    if header:
        title_elem = header.find('div', class_='text')
        if title_elem:
            chat_title = title_elem.get_text(strip=True)

    # Находим все сообщения
    messages = soup.find_all('div', class_='message')

    print(f"Найдено сообщений: {len(messages)}")
    print(f"Конвертирую...")

    # Создаем текстовый файл
    with open(output_path, 'w', encoding='utf-8') as f:
        # Заголовок
        f.write("=" * 80 + "\n")
        f.write(f"{chat_title}\n")
        f.write("=" * 80 + "\n\n")

        # Обрабатываем каждое сообщение
        for i, msg in enumerate(messages, 1):
            msg_lines = parse_message(msg)
            if msg_lines:
                # Получаем ID сообщения
                msg_id = msg.get('id', '')

                # Записываем сообщение
                if 'service' not in msg.get('class', []):
                    f.write(f"\n{'─' * 80}\n")
                    f.write(f"Сообщение ID: {msg_id}\n")
                    f.write('─' * 80 + "\n")

                for line in msg_lines:
                    f.write(line + "\n")

                f.write("\n")

            # Показываем прогресс
            if i % 100 == 0:
                print(f"Обработано: {i}/{len(messages)}")

    print(f"\n✅ Готово! Файл сохранен: {output_path}")
    print(f"Размер: {output_path.stat().st_size / 1024:.2f} KB")


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование:")
        print(f"  python {sys.argv[0]} <путь_к_messages.html> [путь_для_выходного_файла.txt]")
        print("\nПример:")
        print(f"  python {sys.argv[0]} messages.html")
        print(f"  python {sys.argv[0]} messages.html output.txt")
        sys.exit(1)

    html_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    convert_html_to_txt(html_path, output_path)


if __name__ == '__main__':
    main()
