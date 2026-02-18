import base64
import io
import os
import re
import shutil
import subprocess
import tempfile
from typing import Dict, List

import pymupdf4llm
from pdf2image import convert_from_bytes


class BaseProcessor:
    ANCHOR_SECTIONS = {
        "АННОТАЦИЯ",
        "ABSTRACT",
        "ВВЕДЕНИЕ",
        "ЗАКЛЮЧЕНИЕ",
        "СПИСОК ЛИТЕРАТУРЫ",
        "СОДЕРЖАНИЕ",
        'ПРИЛОЖЕНИЕ'
    }
    TITLE_NOISE = {
        "МОСКВА",
        "2025",
        "2024",
        "УНИВЕРСИТЕТ",
        "КАФЕДРА",
        "ДИПЛОМНАЯ РАБОТА",
    }

    @staticmethod
    def _final_clean(text: str) -> str:
        """Стерилизация заголовка: убираем звезды, решетки, лишние пробелы"""
        if not text:
            return ""

        clean = re.sub(r"[*_#`]", "", text)
        clean = " ".join(clean.split())

        return clean.strip()

    @staticmethod
    def _get_header_title(line: str) -> str:
        line = line.strip()
        if not line:
            return None

        raw_title = None
        
        # 1. Сначала проверяем, есть ли Markdown заголовок (#)
        md_match = re.match(r"^#+\s+(.*)", line)
        if md_match:
            raw_title = md_match.group(1)
        # 2. Если решетки нет, проверяем, не вся ли строка жирная
        else:
            bold_match = re.match(r"^[*_]+(.+?)[*_]+$", line)
            if bold_match:
                raw_title = bold_match.group(1)

        if raw_title:
            # ОЧИСТКА: Убираем оставшиеся звезды/решетки внутри (например, из # **ЗАГОЛОВОК**)
            clean_title = BaseProcessor._final_clean(raw_title)
            upper_title = clean_title.upper()

            # ФИЛЬТРАЦИЯ
            if any(noise in upper_title for noise in BaseProcessor.TITLE_NOISE):
                return None
            
            # Проверка длины и точки (точка в конце часто признак обычного предложения)
            if (
                len(clean_title) < 3 # Сократил до 3, чтобы "П-1" или подобные влезали
                or len(clean_title) > 200 # Чуть расширил лимит
                or clean_title.endswith(".")
            ):
                return None
                
            # Валидация: начинается с заглавной или цифры
            if not clean_title[0].isdigit() and not clean_title[0].isupper():
                return None

            return clean_title
        return None

    @staticmethod
    def _split_markdown_by_headers(md_text: str) -> List[Dict[str, str]]:
        lines = md_text.split("\n")
        chunks = []
        
        current_header = "Титульный лист"
        current_content = []

        def get_clean_text(content_list):
            raw_text = "\n".join(content_list).strip()
            # Удаляем номера страниц (одинокие цифры на строке)
            clean_text = re.sub(r"^\d+\s*$", "", raw_text, flags=re.MULTILINE)
            # Схлопываем лишние переносы
            return re.sub(r"\n{3,}", "\n\n", clean_text).strip()

        for line in lines:
            new_header = BaseProcessor._get_header_title(line)
            
            if new_header:
                text_before = get_clean_text(current_content)
                
                # ЛОГИКА СКЛЕЙКИ:
                # Если под текущим заголовком пусто И это не титульник — клеим к заголовку
                if not text_before and current_header != "Титульный лист":
                    current_header = f"{current_header} {new_header}"
                else:
                    # Если текст был, сохраняем старый чанк и начинаем новый
                    if text_before or current_header != "Титульный лист":
                        chunks.append({"header": current_header, "text": text_before})
                    
                    current_header = new_header
                    current_content = []
            else:
                current_content.append(line)

        # Сохраняем последний кусок
        last_text = get_clean_text(current_content)
        if last_text or current_header != "Титульный лист":
            chunks.append({"header": current_header, "text": last_text})

        return chunks


class PDFProcessor(BaseProcessor):
    @staticmethod
    def get_pages_as_base64(
        pdf_file: io.BytesIO, first_page: int, last_page: int
    ) -> List[str]:
        pdf_file.seek(0)
        images = convert_from_bytes(
            pdf_file.read(), first_page=first_page, last_page=last_page, dpi=130
        )
        encoded = []
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            encoded.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
        return encoded

    @staticmethod
    def get_structured_text(pdf_file: io.BytesIO) -> List[Dict[str, str]]:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_file.getvalue())
            tmp_path = tmp.name

        try:
            md_text = pymupdf4llm.to_markdown(tmp_path)
            return PDFProcessor._split_markdown_by_headers(md_text)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class DOCXProcessor(BaseProcessor):
    @staticmethod
    def _docx_to_pdf_bytes(docx_file: io.BytesIO) -> io.BytesIO:
        """Конвертация DOCX в PDF с использованием LibreOffice (Linux compatible)"""
        if not shutil.which("libreoffice") and not shutil.which("soffice"):
            raise EnvironmentError(
                "LibreOffice not found. Install it with: apt-get install libreoffice"
            )

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, "input.docx")
            with open(input_path, "wb") as f:
                f.write(docx_file.getvalue())

            try:
                subprocess.run(
                    [
                        "libreoffice",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        input_path,
                        "--outdir",
                        tmp_dir,
                    ],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                subprocess.run(
                    [
                        "soffice",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        input_path,
                        "--outdir",
                        tmp_dir,
                    ],
                    check=True,
                )

            pdf_path = os.path.join(tmp_dir, "input.pdf")
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(
                    "LibreOffice failed to generate PDF file."
                )

            with open(pdf_path, "rb") as f:
                return io.BytesIO(f.read())

    @staticmethod
    def get_pages_as_base64(
        docx_file: io.BytesIO, first_page: int, last_page: int
    ) -> List[str]:
        pdf_data = DOCXProcessor._docx_to_pdf_bytes(docx_file)
        return PDFProcessor.get_pages_as_base64(pdf_data, first_page, last_page)

    @staticmethod
    def get_structured_text(docx_file: io.BytesIO) -> List[Dict[str, str]]:
        pdf_data = DOCXProcessor._docx_to_pdf_bytes(docx_file)
        return PDFProcessor.get_structured_text(pdf_data)


class DocumentProcessorService:
    def __init__(
        self, pdf_processor: PDFProcessor, docx_processor: DOCXProcessor
    ):
        self.pdf_processor = pdf_processor
        self.docx_processor = docx_processor
        self._current_content_type = "application/pdf"

    def set_context(self, content_type: str):
        """Устанавливает контекст типа файла для текущей задачи"""
        self._current_content_type = content_type

    def _get_p(self):
        if self._current_content_type == "application/pdf":
            return self.pdf_processor
        return self.docx_processor

    def get_pages_as_base64(self, file_bytes, start, end):
        return self._get_p().get_pages_as_base64(file_bytes, start, end)

    def get_structured_text(self, file_bytes):
        return self._get_p().get_structured_text(file_bytes)

    def is_pdf(self) -> bool:
        return self._current_content_type == "application/pdf"
