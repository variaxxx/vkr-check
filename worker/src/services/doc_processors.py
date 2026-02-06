import io
import base64
import tempfile
import os
from typing import List, Dict

import pymupdf4llm
from pdf2image import convert_from_bytes
from docx2pdf import convert as docx_to_pdf

import re


class BaseProcessor:
    ANCHOR_SECTIONS = {"АННОТАЦИЯ", "ABSTRACT", "ВВЕДЕНИЕ", "ЗАКЛЮЧЕНИЕ", "СПИСОК ЛИТЕРАТУРЫ", "СОДЕРЖАНИЕ"}
    TITLE_NOISE = {"МОСКВА", "2025", "2024", "УНИВЕРСИТЕТ", "КАФЕДРА", "ДИПЛОМНАЯ РАБОТА"}

    @staticmethod
    def _final_clean(text: str) -> str:
        """Стерилизация заголовка: убираем звезды, решетки, лишние пробелы"""
        if not text: return ""

        clean = re.sub(r'[*_#`]', '', text)
        clean = " ".join(clean.split())

        return clean.strip()

    @staticmethod
    def _get_header_title(line: str) -> str:
        line = line.strip()
        if not line: return None

        raw_title = None
        md_match = re.match(r'^#+\s+(.*)', line)
        if md_match:
            raw_title = md_match.group(1)
        else:
            bold_match = re.match(r'^[*_]+(.+?)[*_]+$', line)
            if bold_match:
                raw_title = bold_match.group(1)

        if raw_title:
            clean_title = BaseProcessor._final_clean(raw_title)
            upper_title = clean_title.upper()

            # ФИЛЬТРАЦИЯ
            # Если это мусор с титульника
            if any(noise in upper_title for noise in BaseProcessor.TITLE_NOISE): return None
            # Если заголовок слишком длинный или короткий или это предложение (точка в конце)
            if len(clean_title) < 4 or len(clean_title) > 150 or clean_title.endswith('.'): return None
            # Если это просто жирный текст (маленькая буква в начале и нет цифр)
            if not clean_title[0].isdigit() and not clean_title[0].isupper(): return None

            return clean_title
        return None

    @staticmethod
    def _split_markdown_by_headers(md_text: str) -> List[Dict[str, str]]:
        lines = md_text.split('\n')
        chunks = []
        current_header = "Титульный лист"
        current_content = []

        def save_chunk(content, header):
            raw_text = "\n".join(content).strip()

            clean_text = re.sub(r'^\d+\s*$', '', raw_text, flags=re.MULTILINE)
            clean_text = re.sub(r'\n{3,}', '\n\n', clean_text).strip()
            
            if clean_text and len(clean_text) > 15:
                chunks.append({
                    "header": header,
                    "text": clean_text
                })

        for line in lines:
            new_header = BaseProcessor._get_header_title(line)
            if new_header:
                save_chunk(current_content, current_header)
                current_content = []
                current_header = new_header
            else:
                current_content.append(line)

        save_chunk(current_content, current_header)
        return chunks

class PDFProcessor(BaseProcessor):
    @staticmethod
    def get_pages_as_base64(pdf_file: io.BytesIO, first_page: int, last_page: int) -> List[str]:
        pdf_file.seek(0)
        images = convert_from_bytes(
            pdf_file.read(),
            first_page=first_page,
            last_page=last_page,
            dpi=200 
        )
        encoded = []
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            encoded.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
        return encoded

    @staticmethod
    def get_structured_text(pdf_file: io.BytesIO) -> List[Dict[str, str]]:
        # вот тут косяк может быть, pymupdf4llm вроде не читает байты
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_file.getvalue())
            tmp_path = tmp.name
        
        try:
            md_text = pymupdf4llm.to_markdown(tmp_path)
            return PDFProcessor._split_markdown_by_headers(md_text)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

import subprocess
import shutil
import tempfile
import os
import io
from typing import List, Dict

class DOCXProcessor(BaseProcessor):
    @staticmethod
    def _docx_to_pdf_bytes(docx_file: io.BytesIO) -> io.BytesIO:
        """Конвертация DOCX в PDF с использованием LibreOffice (Linux compatible)"""
        if not shutil.which('libreoffice') and not shutil.which('soffice'):
            raise EnvironmentError(
                "LibreOffice not found. Install it with: apt-get install libreoffice"
            )

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, "input.docx")
            with open(input_path, "wb") as f:
                f.write(docx_file.getvalue())

            try:
                subprocess.run([
                    'libreoffice', 
                    '--headless', 
                    '--convert-to', 'pdf', 
                    input_path, 
                    '--outdir', tmp_dir
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                subprocess.run([
                    'soffice', '--headless', '--convert-to', 'pdf', 
                    input_path, '--outdir', tmp_dir
                ], check=True)

            pdf_path = os.path.join(tmp_dir, "input.pdf")
            if not os.path.exists(pdf_path):
                raise FileNotFoundError("LibreOffice failed to generate PDF file.")
                
            with open(pdf_path, "rb") as f:
                return io.BytesIO(f.read())

    @staticmethod
    def get_pages_as_base64(docx_file: io.BytesIO, first_page: int, last_page: int) -> List[str]:
        pdf_data = DOCXProcessor._docx_to_pdf_bytes(docx_file)
        return PDFProcessor.get_pages_as_base64(pdf_data, first_page, last_page)

    @staticmethod
    def get_structured_text(docx_file: io.BytesIO) -> List[Dict[str, str]]:
        pdf_data = DOCXProcessor._docx_to_pdf_bytes(docx_file)
        return PDFProcessor.get_structured_text(pdf_data)


class DocumentProcessorService:
    def __init__(self, pdf_processor: PDFProcessor, docx_processor: DOCXProcessor):
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