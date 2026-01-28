import io
import base64
from pdf2image import convert_from_path
from typing import List
import pypdf

class PDFProcessor:
    """Класс для обработки PDF файлов"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Извлекает весь текст из PDF файла"""
        reader = pypdf.PdfReader(pdf_path)
        return "\n".join([page.extract_text() for page in reader.pages])

    @staticmethod
    def get_page_text(pdf_path: str, page_num: int) -> str:
        """Извлекает текст конкретной страницы (1-based index)"""
        reader = pypdf.PdfReader(pdf_path)
        if 1 <= page_num <= len(reader.pages):
            return reader.pages[page_num - 1].extract_text()
        return ""

    @staticmethod
    def get_total_pages(pdf_path: str) -> int:
        """Возвращает общее количество страниц в PDF"""
        reader = pypdf.PdfReader(pdf_path)
        return len(reader.pages)
    
    @staticmethod
    def get_pages_as_base64(pdf_path: str, first_page: int, last_page: int) -> List[str]:
        """Конвертирует страницы PDF в base64 изображения"""
        images = convert_from_path(pdf_path, first_page=first_page, last_page=last_page, dpi=300)
        encoded = []
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            encoded.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
        return encoded