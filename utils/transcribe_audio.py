#!/usr/bin/env python3
"""
Транскрибация аудиофайлов с использованием OpenAI Whisper.
Поддерживает форматы: .ogg, .m4a, .mp3, .wav и другие аудио форматы.
"""

import sys
import os
from pathlib import Path
import argparse

try:
    import whisper
except ImportError:
    print("Ошибка: Необходимо установить библиотеку openai-whisper")
    print("Установите её командой: pip install openai-whisper")
    print("\nДополнительно может потребоваться ffmpeg:")
    print("  Windows: winget install ffmpeg")
    print("  или скачайте с https://ffmpeg.org/download.html")
    sys.exit(1)


# Поддерживаемые аудио форматы
AUDIO_EXTENSIONS = {'.ogg', '.m4a', '.mp3', '.wav', '.flac', '.aac', '.wma', '.opus'}

# Доступные модели Whisper
AVAILABLE_MODELS = ['tiny', 'base', 'small', 'medium', 'large']


def transcribe_file(audio_path, model, output_dir, language='ru', verbose=True):
    """
    Транскрибирует один аудиофайл

    Args:
        audio_path: путь к аудиофайлу
        model: загруженная модель Whisper
        output_dir: директория для сохранения результатов
        language: язык аудио (по умолчанию 'ru')
        verbose: выводить ли детальную информацию

    Returns:
        tuple: (success: bool, output_path: Path)
    """
    audio_path = Path(audio_path)

    if not audio_path.exists():
        print(f"[ERROR] Файл не найден: {audio_path}")
        return False, None

    # Формируем имя выходного файла
    output_filename = audio_path.stem + '.txt'
    output_path = Path(output_dir) / output_filename

    # Проверяем, не обработан ли файл уже
    if output_path.exists():
        print(f"[SKIP] Пропускаем (уже существует): {output_filename}")
        return True, output_path

    try:
        print(f"[...] Обрабатываю: {audio_path.name}")

        # Транскрибируем
        result = model.transcribe(
            str(audio_path),
            language=language,
            verbose=verbose,
            fp16=False  # Отключаем FP16 для совместимости с CPU
        )

        # Сохраняем результат
        with open(output_path, 'w', encoding='utf-8') as f:
            # Записываем метаданные
            f.write(f"# Транскрипция: {audio_path.name}\n")
            f.write(f"# Язык: {result.get('language', language)}\n")
            f.write(f"# Модель: {model.__class__.__name__}\n")
            f.write("=" * 80 + "\n\n")

            # Основной текст
            f.write(result['text'].strip())
            f.write("\n\n")

            # Детальная информация по сегментам (с временными метками)
            if 'segments' in result and result['segments']:
                f.write("\n" + "=" * 80 + "\n")
                f.write("# Детальная транскрипция с временными метками\n")
                f.write("=" * 80 + "\n\n")

                for segment in result['segments']:
                    start = segment['start']
                    end = segment['end']
                    text = segment['text'].strip()

                    # Форматируем время как MM:SS
                    start_time = f"{int(start // 60):02d}:{int(start % 60):02d}"
                    end_time = f"{int(end // 60):02d}:{int(end % 60):02d}"

                    f.write(f"[{start_time} -> {end_time}] {text}\n")

        print(f"[OK] Сохранено: {output_path}")
        return True, output_path

    except Exception as e:
        print(f"[ERROR] Ошибка при обработке {audio_path.name}: {e}")
        return False, None


def process_directory(input_dir, model, output_dir, language='ru', verbose=False):
    """
    Обрабатывает все аудиофайлы в директории

    Args:
        input_dir: директория с аудиофайлами
        model: загруженная модель Whisper
        output_dir: директория для сохранения результатов
        language: язык аудио
        verbose: выводить ли детальную информацию от Whisper
    """
    input_dir = Path(input_dir)

    # Находим все аудиофайлы
    audio_files = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(input_dir.glob(f'*{ext}'))

    audio_files.sort()

    if not audio_files:
        print(f"[ERROR] Аудиофайлы не найдены в {input_dir}")
        return

    print(f"\nНайдено файлов: {len(audio_files)}\n")

    # Обрабатываем каждый файл
    successful = 0
    failed = 0

    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] ", end='')
        success, _ = transcribe_file(audio_file, model, output_dir, language, verbose=verbose)

        if success:
            successful += 1
        else:
            failed += 1

    # Итоговая статистика
    print(f"\n{'=' * 80}")
    print(f"[OK] Успешно обработано: {successful}")
    if failed > 0:
        print(f"[ERROR] Ошибок: {failed}")
    print(f"Результаты сохранены в: {output_dir}")
    print(f"{'=' * 80}\n")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Транскрибация аудиофайлов с использованием OpenAI Whisper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Обработать все файлы в папке (рекомендуется)
  python utils/transcribe_audio.py "ChatExport_2026-01-19/ChatExport_2026-01-19/voice_messages"

  # Обработать один файл
  python utils/transcribe_audio.py "path/to/audio.ogg"

  # Использовать другую модель
  python utils/transcribe_audio.py "path/to/folder" --model large

  # Для английского языка
  python utils/transcribe_audio.py "path/to/audio.m4a" --language en

Модели (от быстрой к точной):
  tiny, base, small, medium (по умолчанию), large
        """
    )

    parser.add_argument(
        'input_path',
        help='Путь к аудиофайлу или папке с аудиофайлами'
    )

    parser.add_argument(
        '-m', '--model',
        default='medium',
        choices=AVAILABLE_MODELS,
        help='Модель Whisper (по умолчанию: medium)'
    )

    parser.add_argument(
        '-l', '--language',
        default='ru',
        help='Язык аудио (по умолчанию: ru)'
    )

    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Папка для сохранения результатов (по умолчанию: та же папка, что и аудио)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Показывать детальный вывод от Whisper'
    )

    args = parser.parse_args()

    input_path = Path(args.input_path)

    # Определяем output_dir: по умолчанию та же папка, что и аудио
    if args.output:
        output_dir = Path(args.output)
    elif input_path.is_dir():
        output_dir = input_path
    else:
        output_dir = input_path.parent

    # Создаём выходную директорию
    output_dir.mkdir(parents=True, exist_ok=True)

    # Загружаем модель
    print(f"Загружаю модель Whisper '{args.model}'...")
    print("   (При первом запуске модель будет скачана, это может занять время)")

    try:
        model = whisper.load_model(args.model)
        print(f"[OK] Модель '{args.model}' загружена\n")
    except Exception as e:
        print(f"[ERROR] Ошибка загрузки модели: {e}")
        sys.exit(1)

    # Определяем, что обрабатывать
    if input_path.is_file():
        # Обрабатываем один файл
        if input_path.suffix.lower() not in AUDIO_EXTENSIONS:
            print(f"[ERROR] Неподдерживаемый формат файла: {input_path.suffix}")
            print(f"   Поддерживаются: {', '.join(sorted(AUDIO_EXTENSIONS))}")
            sys.exit(1)

        transcribe_file(input_path, model, output_dir, args.language, verbose=args.verbose)

    elif input_path.is_dir():
        # Обрабатываем всю папку
        process_directory(input_path, model, output_dir, args.language, verbose=args.verbose)

    else:
        print(f"[ERROR] Путь не найден: {input_path}")
        sys.exit(1)


if __name__ == '__main__':
    main()
