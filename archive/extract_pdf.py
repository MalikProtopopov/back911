#!/usr/bin/env python3
"""Скрипт для извлечения текста из PDF"""
import sys

try:
    from pypdf import PdfReader
except ImportError:
    print("Устанавливаю pypdf...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf", "--quiet"])
    from pypdf import PdfReader


def extract_pdf_text(pdf_path):
    """Извлекает весь текст из PDF"""
    reader = PdfReader(pdf_path)
    text = ""
    for page_num, page in enumerate(reader.pages, 1):
        page_text = page.extract_text()
        text += f"\n--- Страница {page_num} ---\n"
        text += page_text
        text += "\n"
    return text


if __name__ == "__main__":
    pdf_file = "e81303a9-7db4-4813-933c-e8833bd79b13_Сайт_для_911.pdf"
    print(f"Извлечение текста из {pdf_file}...")
    text = extract_pdf_text(pdf_file)

    # Сохраняем в файл
    output_file = "pdf_extracted_text.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Текст сохранен в {output_file}")
    print(f"Всего страниц: {len(PdfReader(pdf_file).pages)}")
    print(f"Длина текста: {len(text)} символов")
    print("\nПервые 2000 символов:")
    print(text[:2000])
