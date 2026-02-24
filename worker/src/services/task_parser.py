import io
from typing import List
from .doc_processors import DocumentProcessorService
from .llm_service import LLMService

class TaskParser:
    """Класс для извлечения задания из PDF с помощью Vision (асинхронная версия)"""

    def __init__(self, llm_service: LLMService, doc_processor: DocumentProcessorService):
        self.llm_service = llm_service
        self.doc_processor = doc_processor

    async def get_task_points(self, pdf_bytes: io.BytesIO) -> List[str]:
        """Извлекает пункты задания из PDF асинхронно"""

        pages = self.doc_processor.get_pages_as_base64(pdf_bytes, 2, 4)
        
        vision_prompt_text = (
            "Найди на этих сканах раздел 'Задание' и выпиши пункты требований и содержания. "
            "Если встретятся одинаковые или дублирующие друг друга пункты, верни только один из них."
        )
        messages = self.llm_service.create_vision_prompt(
            user_text=vision_prompt_text,
            pages=pages
        )

        raw_text = await self.llm_service.llm_vision_request(messages)
        
        if not raw_text:
            return []

        refine_system = "Ты — помощник по структурированию текста."
        refine_user = (
            f"Извлеки из текста пункты задания.\n"
            f"Правила: убери заголовки ('Тема', 'Задание'), убери нумерацию, "
            f"оставь только текст каждого пункта. Убери пункты связанные с датами или сроками для сдачи.\n"
            f"Текст: {raw_text}"
        )
        
        refine_prompt = self.llm_service.create_text_prompt(
            user_text=refine_user,
            system_prompt=refine_system
        )

        refined_text = await self.llm_service.llm_text_request(refine_prompt)

        return [
            p.strip() 
            for p in refined_text.split("\n") 
            if len(p.strip()) > 10
        ]