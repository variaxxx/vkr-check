import io
from typing import List

from .llm_service import LLMService
from .pdf_processor import PDFProcessor


class InfoParser:
    """Класс для извлечения задания из PDF с помощью Vision"""

    def __init__(self, llm_service: LLMService, pdf_processor: PDFProcessor):
        self.llm_service = llm_service
        self.pdf_processor = pdf_processor

    def get_fio(self, pdf_file: io.BytesIO) -> List[str]:
        """Извлекает пункты задания из PDF"""

        pages = self.pdf_processor.get_pages_as_base64(pdf_file, 1, 1)
        content = [
            {
                "type": "text",
                "text": "Найди на этой странице ФИО студентов выполнивших дипломную работу. Верни только полное имя в формате: Фамилия Имя Отчество - группа. Не используй инициалы.",  # noqa: E501
            }
        ]

        for b64 in pages:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                }
            )

        raw_text = self.llm_service.invoke_vision(content)

        return [p.strip() for p in raw_text.split("\n") if len(p.strip()) > 10]

    def get_theme(self, pdf_file: io.BytesIO) -> List[str]:
        """Извлекает пункты задания из PDF"""

        pages = self.pdf_processor.get_pages_as_base64(pdf_file, 2, 2)
        content = [
            {
                "type": "text",
                "text": "Найди на этой странице тему дипломной работы. Выведи полностью текст темы без изменений.",  # noqa: E501
            }
        ]

        for b64 in pages:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                }
            )

        raw_text = self.llm_service.invoke_vision(content)

        return raw_text

    def get_info(self, pdf_file: io.BytesIO) -> dict:
        res = {
            "students": self.get_fio(pdf_file),
            "theme": self.get_theme(pdf_file),
        }

        return res
