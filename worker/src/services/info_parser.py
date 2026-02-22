import io
import time
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .llm_service import LLMService
from .doc_processors import DocumentProcessorService


class InfoParser:
    """Класс для извлечения задания из PDF с помощью Vision"""

    def __init__(self, llm_service: LLMService, doc_processor: DocumentProcessorService):
        self.llm_service = llm_service
        self.doc_processor = doc_processor
        
    def get_fio(self, pdf_file: io.BytesIO) -> List[str]:
        """Извлекает ФИО студентов из PDF"""
        
        pages = self.doc_processor.get_pages_as_base64(pdf_file, 1, 1)
        timestamp = time.time()

        messages = [
            SystemMessage(content="""Ты - эксперт по точному анализу дипломных работ. 
            Критически важные инструкции:
            1. Извлекай только ФИО студентов, выполнивших дипломную работу, никакие ФИО больше не возвращай, ФИО руководителей возвращать НЕ нужно
            2. Извлекай ТОЛЬКО полные ФИО (Фамилия Имя Отчество полностью), игнорируй сокращенные формы (типа "Иванов И.И.")
            3. Если одно и то же имя встречается в полной и сокращенной форме - бери только полную
            4. Возвращай только уникальные записи, без повторений
            5. Строгий формат: Фамилия Имя Отчество - группа
            6. В случае отсутствия указания группы формат: Фамилия Имя Отчество - группа не указана
            7. Никаких пояснений, только список"""),
            
            HumanMessage(content=[
                {
                    "type": "text", 
                    "text": f"Найди на титульном листе только полные ФИО студентов, которые выполнили дипломную работу, другие ФИО возвращать не нужно. \
                    Верни только уникальные записи в формате: Фамилия Имя Отчество - группа. Каждое ФИО с новой строки. Время запроса: {timestamp}"
                }
            ])
        ]
        
        for b64 in pages:
            messages[1].content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })
        
        llm = self.llm_service.get_llm()
        raw_text = llm.invoke(messages, max_tokens=2048)
        timestamp = time.time()

        refine_prompt = ChatPromptTemplate.from_template("""Время запроса: {timestamp}
        Проверь список ФИО на совпадения, если в списке есть совпадающие ФИО, записанные в разных формат, например в полной и краткой, выбери только их полные формы.
        К этим полным формам добавь информацию о группе, которая написана через '-', и выведи в формате: Фамилия Имя Отчество - группа.
        Информацию о каждом человеке выводи с новой строки, ничего больше не выводи.
        Список ФИО: {text}
        """)  # noqa: E501

        chain = refine_prompt | self.llm_service.get_llm() | StrOutputParser()
        response = chain.invoke({"text": raw_text, "timestamp" : timestamp})

        return [p.strip() for p in response.split("\n") if len(p.strip()) > 10]        

    def get_theme(self, pdf_file: io.BytesIO) -> str:
        """Извлекает тему дипломной работы из PDF"""
        
        pages = self.doc_processor.get_pages_as_base64(pdf_file, 1, 3)
        timestamp = time.time()

        messages = [
            SystemMessage(content="""Ты - эксперт по точному анализу дипломных работ. В приоритете ищи тему рядом с заголовком 'Тема работы'.
            Возвращай только тему дипломной работы, без пояснений и комментариев, без заголовков по типу 'Тема работы'."""),
            
            HumanMessage(content=[
                {
                    "type": "text",
                    "text": f"Найди на этих страницах тему дипломной работы. Выведи полностью текст темы без изменений. Время запроса: {timestamp}"
                }
            ])
        ]
        
        for b64 in pages:
            messages[1].content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })
                
        llm = self.llm_service.get_llm()
        response = llm.invoke(messages, max_tokens=2048)   

        return response.content.strip()

    def get_info(self, pdf_file: io.BytesIO) -> dict:
        """Извлекает всю информацию из PDF"""
        
        res = {
            "students": self.get_fio(pdf_file),
            "theme": self.get_theme(pdf_file),
        }
        
        return res