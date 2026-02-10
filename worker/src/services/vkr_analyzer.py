import re
from typing import Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .llm_service import LLMService
from .rag import RAGEngine
from langchain_community.vectorstores import FAISS


class VKRAnalyzer:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        # тут есть проблема: модель иногда циклится и я не знаю как это фиксить
        self.llm_service = llm_service
        self.rag_engine = rag_engine

    def evaluate_point(self, task_point: str, vector_db: FAISS) -> Tuple[int, str]:
        """Оценивает пункт задания, понимая, где в дипломе искать информацию"""
        
        target_categories = None
        if any(word in task_point.lower() for word in ["литератур", "источник", "библиогр"]):
            target_categories = ["biblio", "main"]
        else:
            target_categories = ["intro", "main", "conclusion"]

        docs = self.rag_engine.retrieve_relevant_chunks(
            vector_db, 
            task_point, 
            categories=target_categories
        )
        context = self.rag_engine.get_context_from_docs(docs)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты эксперт, проверяющий соответствие ВКР (дипломную работу) выданному заданию. Оцени, раскрыт ли пункт в тексте. Отвечай максимально кратко и строго по шаблону. Не пиши вступлений."),
            ("user", """
Пункт задания: {task_point}
Контекст: {context}

Шаблон:
Балл: [число от 0 до 10]
Обоснование: [1-2 предложения]
""")
        ])

        llm = self.llm_service.get_llm()
        chain = prompt | llm.bind(max_tokens=512, temperature=0) | StrOutputParser()
        
        try:
            result = chain.invoke(
                {"task_point": task_point, "context": context},
            )
        except Exception as e:
            return 0, f"Ошибка тайм-аута или генерации: {e}"

        return self._parse_evaluation_result(result)

    def _parse_evaluation_result(self, result_text: str) -> Tuple[int, str]:
        score_match = re.search(r"Балл:\s*(\d+)", result_text)
        reason_match = re.search(r"Обоснование:\s*(.*)", result_text, re.DOTALL)
        score = int(score_match.group(1)) if score_match else 0
        reason = reason_match.group(1).strip() if reason_match else result_text
        return score, reason
