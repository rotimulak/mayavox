"""
Модуль загрузки контекста из markdown файлов.

Загружает все файлы анализа из директории result/ в единую строку.
"""

import sys
from pathlib import Path


def load_all_context(result_dir='result'):
    """
    Загрузить все markdown файлы из директории result/ в единую строку.

    Args:
        result_dir: Путь к директории с файлами контекста

    Returns:
        str: Объединенное содержимое всех файлов

    Raises:
        FileNotFoundError: Если какой-либо файл не найден
        Exception: При ошибках чтения файлов
    """
    # Список файлов в правильном порядке
    context_files = [
        '01-methodology.md',
        '02-chat_participants.md',
        '03-projects.md',
        '04-vision_evolution.md',
        '05-positions_by_participant.md',
        '06-positions_evolution.md',
        '07-positions_matrix.md'
    ]

    result_path = Path(result_dir)

    if not result_path.exists():
        raise FileNotFoundError(f"Директория контекста не найдена: {result_path}")

    context_parts = []

    for filename in context_files:
        filepath = result_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Файл контекста не найден: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Добавляем заголовок с именем файла для навигации
                context_parts.append(f"# Файл: {filename}\n\n{content}\n\n{'=' * 80}\n\n")
        except Exception as e:
            raise Exception(f"Ошибка чтения файла {filepath}: {e}")

    full_context = ''.join(context_parts)

    return full_context


def get_context_stats(context):
    """
    Получить статистику по загруженному контексту.

    Args:
        context: Строка с контекстом

    Returns:
        dict: Статистика (символы, слова, строки)
    """
    return {
        'chars': len(context),
        'words': len(context.split()),
        'lines': len(context.split('\n'))
    }


if __name__ == '__main__':
    """Тест загрузки контекста"""
    try:
        print("[INFO] Загрузка контекста из result/...")
        context = load_all_context()
        stats = get_context_stats(context)

        print(f"[OK] Контекст успешно загружен!")
        print(f"  Символов: {stats['chars']:,}")
        print(f"  Слов: {stats['words']:,}")
        print(f"  Строк: {stats['lines']:,}")
        print(f"\nПервые 500 символов:")
        print("-" * 80)
        print(context[:500])
        print("-" * 80)

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
