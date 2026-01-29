import base64
import io
from typing import List

import pypdf
from pdf2image import convert_from_bytes


class PDFProcessor:
    def extract_text_from_pdf(pdf_file: io.BytesIO) -> str:
        """Извлекает весь текст из PDF файла"""
        pdf_file.seek(0)
        reader = pypdf.PdfReader(pdf_file)
        return "\n".join([page.extract_text() for page in reader.pages])

    def get_page_text(pdf_file: io.BytesIO, page_num: int) -> str:
        """Извлекает текст конкретной страницы (1-based index)"""
        pdf_file.seek(0)
        reader = pypdf.PdfReader(pdf_file)

        if 1 <= page_num <= len(reader.pages):
            return reader.pages[page_num - 1].extract_text()
        return ""

    def get_total_pages(pdf_file: io.BytesIO) -> int:
        """Возвращает общее количество страниц в PDF"""
        pdf_file.seek(0)
        reader = pypdf.PdfReader(pdf_file)
        return len(reader.pages)

    def get_pages_as_base64(
        pdf_bytes: io.BytesIO, first_page: int, last_page: int
    ) -> List[str]:
        """Конвертирует страницы PDF в base64 изображения"""
        pdf_bytes.seek(0)
        images = convert_from_bytes(
            pdf_bytes.read(),
            first_page=first_page,
            last_page=last_page,
            dpi=300,
        )

        encoded = []
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            encoded.append(base64.b64encode(buf.getvalue()).decode("utf-8"))

        return encoded
