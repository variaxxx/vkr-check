from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pdf_processor import PDFProcessor
from llm_service import LLMService
from typing import List

class TaskParser:
    """Класс для извлечения задания из PDF с помощью Vision"""
    
    def __init__(self, llm_service: LLMService, pdf_processor: PDFProcessor):
        self.llm_service = llm_service
        self.pdf_processor = pdf_processor
    
    def get_task_points(self, pdf_path: str) -> List[str]:
        """Извлекает пункты задания из PDF"""

        pages = self.pdf_processor.get_pages_as_base64(pdf_path, 2, 4)
        content = [{"type": "text", "text": "Найди на этих сканах раздел 'Задание' и выпиши пункты требований и содержания."}]
        
        for b64 in pages:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

        raw_text = self.llm_service.invoke_vision(content)

        refine_prompt = ChatPromptTemplate.from_template("""
        Извлеки из текста пункты задания. 
        Правила: убери заголовки ('Тема', 'Задание'), убери нумерацию, оставь только текст каждого пункта. Убери пункты связанные с датами или сроками для сдачи.
        Текст: {text}
        """)
        
        chain = refine_prompt | self.llm_service.get_llm() | StrOutputParser()
        result = chain.invoke({"text": raw_text})
        
        return [p.strip() for p in result.split('\n') if len(p.strip()) > 10]