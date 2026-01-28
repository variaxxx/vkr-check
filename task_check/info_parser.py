from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pdf_processor import PDFProcessor
from llm_service import LLMService
from typing import List

class InfoParser:
    """Класс для извлечения задания из PDF с помощью Vision"""
    
    def __init__(self, llm_service: LLMService, pdf_processor: PDFProcessor):
        self.llm_service = llm_service
        self.pdf_processor = pdf_processor
    
    def get_fio(self, pdf_path: str) -> List[str]:
        """Извлекает пункты задания из PDF"""

        pages = self.pdf_processor.get_pages_as_base64(pdf_path, 1, 1)
        content = [{"type": "text", "text": "Найди на этой странице ФИО студентов выполнивших дипломную работу. Верни только полное имя в формате: Фамлия Имя Отчество - группа. Не используй инициалы."}]
        
        for b64 in pages:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        
        raw_text = self.llm_service.invoke_vision(content)
        
        return [p.strip() for p in raw_text.split('\n') if len(p.strip()) > 10]    
    
    def get_theme(self, pdf_path: str) -> List[str]:
        """Извлекает пункты задания из PDF"""

        pages = self.pdf_processor.get_pages_as_base64(pdf_path, 2, 2)
        content = [{"type": "text", "text": "Найди на этой странице тему дипломной работы. Выведи полностью текст темы без изменений."}]
        
        for b64 in pages:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        
        raw_text = self.llm_service.invoke_vision(content)
        
        return raw_text
    
    def get_info(self, pdf_path: str) -> dict:
        res = {
            "students": self.get_fio(pdf_path),
            "theme": self.get_theme(pdf_path)
        }
        
        return res
    
