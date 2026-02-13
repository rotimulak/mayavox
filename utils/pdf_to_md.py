#!/usr/bin/env python3
"""
Конвертер PDF файлов в Markdown формат.
Использует PyMuPDF (fitz) для извлечения текста.
"""

import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Ошибка: Необходимо установить библиотеку PyMuPDF")
    print("Установите её командой: pip install pymupdf")
    sys.exit(1)


def extract_text_from_pdf(pdf_path):
    """
    Извлекает текст из PDF файла постранично.

    Args:
        pdf_path: путь к PDF файлу

    Returns:
        список кортежей (номер_страницы, текст)
    """
    pages = []

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, 1):
            text = page.get_text("text")
            if text.strip():
                pages.append((page_num, text))

    return pages


def format_as_markdown(pages, title):
    """
    Форматирует извлечённый текст как Markdown.

    Args:
        pages: список кортежей (номер_страницы, текст)
        title: заголовок документа

    Returns:
        строка в формате Markdown
    """
    lines = []

    # Заголовок документа
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"*Страниц: {len(pages)}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Содержимое страниц
    for page_num, text in pages:
        lines.append(f"## Страница {page_num}")
        lines.append("")

        # Обрабатываем текст: убираем лишние пустые строки
        text_lines = text.split('\n')
        cleaned_lines = []
        prev_empty = False

        for line in text_lines:
            line = line.rstrip()
            is_empty = not line

            if is_empty:
                if not prev_empty:
                    cleaned_lines.append("")
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False

        lines.extend(cleaned_lines)
        lines.append("")
        lines.append("---")
        lines.append("")

    return '\n'.join(lines)


def convert_pdf_to_md(pdf_path, output_path=None):
    """
    Конвертирует PDF файл в Markdown формат.

    Args:
        pdf_path: путь к PDF файлу
        output_path: путь для сохранения MD (по умолчанию - то же имя с расширением .md)
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"Ошибка: Файл {pdf_path} не найден")
        sys.exit(1)

    # Определяем путь для выходного файла (в той же папке что и PDF)
    if output_path is None:
        output_path = pdf_path.with_suffix('.md')
    else:
        output_path = Path(output_path)

    print(f"Читаю файл: {pdf_path}")

    # Извлекаем текст
    pages = extract_text_from_pdf(pdf_path)

    if not pages:
        print("Ошибка: Не удалось извлечь текст из PDF")
        print("Возможно, PDF содержит только изображения (требуется OCR)")
        sys.exit(1)

    print(f"Извлечено страниц: {len(pages)}")
    print("Конвертирую в Markdown...")

    # Форматируем как Markdown
    title = pdf_path.stem  # имя файла без расширения
    markdown_content = format_as_markdown(pages, title)

    # Сохраняем результат
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"\n✅ Готово! Файл сохранен: {output_path}")
    print(f"Размер: {output_path.stat().st_size / 1024:.2f} KB")


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Конвертер PDF в Markdown")
        print("")
        print("Использование:")
        print(f"  python {sys.argv[0]} <путь_к_файлу.pdf> [путь_для_выходного_файла.md]")
        print("")
        print("Примеры:")
        print(f"  python {sys.argv[0]} document.pdf")
        print(f"  python {sys.argv[0]} document.pdf output.md")
        print("")
        print("По умолчанию MD файл сохраняется в ту же папку, что и исходный PDF.")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    convert_pdf_to_md(pdf_path, output_path)


if __name__ == '__main__':
    main()
