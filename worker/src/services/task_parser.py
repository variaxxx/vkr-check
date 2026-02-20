import io
from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .doc_processors import DocumentProcessorService
from .llm_service import LLMService


class TaskParser:
    """Класс для извлечения задания из PDF с помощью Vision"""

    def __init__(self, llm_service: LLMService, doc_processor: DocumentProcessorService):
        self.llm_service = llm_service
        self.doc_processor = doc_processor

    def get_task_points(self, pdf_bytes: io.BytesIO) -> List[str]:
        """Извлекает пункты задания из PDF"""

        pages = self.doc_processor.get_pages_as_base64(pdf_bytes, 2, 4)
        content = [
            {
                "type": "text",
                "text": "Найди на этих сканах раздел 'Задание' и выпиши пункты требований и содержания.",  # noqa: E501
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

        refine_prompt = ChatPromptTemplate.from_template("""
        Извлеки из текста пункты задания.
        Правила: убери заголовки ('Тема', 'Задание'), убери нумерацию, оставь только текст каждого пункта. Убери пункты связанные с датами или сроками для сдачи.
        Текст: {text}
        """)  # noqa: E501

        chain = refine_prompt | self.llm_service.get_llm() | StrOutputParser()
        result = chain.invoke({"text": raw_text})

        return [p.strip() for p in result.split("\n") if len(p.strip()) > 10]
