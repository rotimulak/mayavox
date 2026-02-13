#!/usr/bin/env python3
"""
Конвертер HTML экспорта Telegram с инъекцией транскрипций голосовых сообщений.
Создаёт messages+audio.txt с вставленным текстом из голосовых.
"""

import sys
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Ошибка: Необходимо установить библиотеку BeautifulSoup4")
    print("Установите её командой: pip install beautifulsoup4")
    sys.exit(1)


def load_transcriptions(transcriptions_dir):
    """Загружает все транскрипции, индексирует по имени файла"""
    transcriptions = {}

    for file_path in Path(transcriptions_dir).glob("audio_*.txt"):
        # Имя без .txt -> audio_5@07-04-2025_15-12-10
        key = file_path.stem
        text = extract_main_text(file_path)
        if text:
            transcriptions[key] = text
            print(f"  Загружена: {file_path.name}")

    return transcriptions


def extract_main_text(file_path):
    """Извлекает основной текст транскрипции (без временных меток)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Текст между первым и вторым блоком ====
    parts = content.split('=' * 80)
    if len(parts) >= 2:
        return parts[1].strip()

    return None


def parse_message(msg_div, transcriptions):
    """Извлекает информацию из одного сообщения"""
    result = []

    is_service = 'service' in msg_div.get('class', [])

    if is_service:
        body = msg_div.find('div', class_='body')
        if body:
            text = body.get_text(strip=True)
            result.append(f"[{text}]")
        return result

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

    # Ответ на сообщение
    reply_to = body.find('div', class_='reply_to')
    if reply_to:
        reply_text = reply_to.get_text(strip=True)
        result.append(f"↩️ {reply_text}")

    # Пересланное сообщение
    forwarded = body.find('div', class_='forwarded')
    if forwarded:
        result.append("--- Пересланное сообщение ---")
        fwd_from = forwarded.find('div', class_='from_name')
        if fwd_from:
            result.append(f"От: {fwd_from.get_text(strip=True)}")
        fwd_text = forwarded.find('div', class_='text')
        if fwd_text:
            text = process_text_element(fwd_text)
            result.append(f"Текст: {text}")

        # Голосовое в пересланном
        fwd_voice = forwarded.find('a', class_='media_voice_message')
        if fwd_voice:
            result.extend(process_voice_message(fwd_voice, transcriptions))

        result.append("--- Конец пересланного сообщения ---")

    # Основной текст
    text_elem = body.find('div', class_='text', recursive=False)
    if text_elem:
        text = process_text_element(text_elem)
        if text:
            result.append(f"Текст: {text}")

    # Медиафайлы
    media_wrap = body.find('div', class_='media_wrap')
    if media_wrap:
        result.extend(process_media(media_wrap, transcriptions))

    # Реакции
    reactions = body.find('span', class_='reactions')
    if reactions:
        reaction_list = []
        for reaction in reactions.find_all('span', class_='reaction'):
            emoji = reaction.find('span', class_='emoji')
            if emoji:
                emoji_text = emoji.get_text(strip=True)
                userpics = reaction.find('span', class_='userpics')
                count = len(userpics.find_all('div', class_='userpic')) if userpics else 1
                reaction_list.append(f"{emoji_text}×{count}")
        if reaction_list:
            result.append(f"Реакции: {', '.join(reaction_list)}")

    return result


def process_text_element(text_elem):
    """Обрабатывает текстовый элемент, сохраняя форматирование"""
    for br in text_elem.find_all('br'):
        br.replace_with('\n')
    text = text_elem.get_text()
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


def process_voice_message(voice_elem, transcriptions):
    """Обрабатывает голосовое сообщение с транскрипцией"""
    result = []

    href = voice_elem.get('href', '')
    # voice_messages/audio_5@07-04-2025_15-12-10.ogg -> audio_5@07-04-2025_15-12-10
    filename = Path(href).stem

    duration_elem = voice_elem.find('div', class_='status')
    duration = duration_elem.get_text(strip=True) if duration_elem else ''

    result.append(f"🎤 Голосовое сообщение ({duration})")

    # Вставляем транскрипцию
    if filename in transcriptions:
        result.append(transcriptions[filename])

    return result


def process_media(media_wrap, transcriptions):
    """Обрабатывает медиафайлы"""
    result = []

    # Голосовое сообщение
    voice = media_wrap.find('a', class_='media_voice_message')
    if voice:
        return process_voice_message(voice, transcriptions)

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

    # Аудио
    audio = media_wrap.find('a', class_='audio_file')
    if audio:
        href = audio.get('href', '')
        audio_title = media_wrap.find('div', class_='title')
        title = audio_title.get_text(strip=True) if audio_title else ''
        duration = media_wrap.find('div', class_='duration')
        dur = duration.get_text(strip=True) if duration else ''
        result.append(f"🎵 Аудио: {title} {dur} ({href})")

    # Файлы
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

    return result if result else ["📎 Медиафайл"]


def convert_with_transcriptions(html_path, transcriptions_dir, output_path):
    """Конвертирует HTML в текст с транскрипциями голосовых"""

    print(f"Загружаю транскрипции из: {transcriptions_dir}")
    transcriptions = load_transcriptions(transcriptions_dir)
    print(f"Найдено транскрипций: {len(transcriptions)}\n")

    print(f"Читаю HTML: {html_path}")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Заголовок чата
    header = soup.find('div', class_='page_header')
    chat_title = "Экспорт чата"
    if header:
        title_elem = header.find('div', class_='text')
        if title_elem:
            chat_title = title_elem.get_text(strip=True)

    messages = soup.find_all('div', class_='message')
    print(f"Найдено сообщений: {len(messages)}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"{chat_title}\n")
        f.write("=" * 80 + "\n\n")

        for i, msg in enumerate(messages, 1):
            msg_lines = parse_message(msg, transcriptions)
            if msg_lines:
                msg_id = msg.get('id', '')

                if 'service' not in msg.get('class', []):
                    f.write(f"\n{'─' * 80}\n")
                    f.write(f"Сообщение ID: {msg_id}\n")
                    f.write('─' * 80 + "\n")

                for line in msg_lines:
                    f.write(line + "\n")

                f.write("\n")

            if i % 100 == 0:
                print(f"Обработано: {i}/{len(messages)}")

    print(f"\n✅ Готово! Файл сохранен: {output_path}")
    print(f"Размер: {output_path.stat().st_size / 1024:.2f} KB")


def main():
    base_dir = Path(__file__).parent.parent

    # Пути по умолчанию
    html_path = base_dir / "ChatExport_2026-01-19" / "ChatExport_2026-01-19" / "messages.html"
    transcriptions_dir = base_dir / "data" / "transcriptions"
    output_path = base_dir / "data" / "messages+audio.txt"

    if len(sys.argv) >= 2:
        html_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        transcriptions_dir = Path(sys.argv[2])
    if len(sys.argv) >= 4:
        output_path = Path(sys.argv[3])

    convert_with_transcriptions(html_path, transcriptions_dir, output_path)


if __name__ == '__main__':
    main()
