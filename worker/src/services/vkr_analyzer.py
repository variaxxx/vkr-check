import re
from typing import Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .llm_service import LLMService
from .rag import RAGEngine


class VKRAnalyzer:
    """Анализатор ВКР"""

    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm_service = llm_service
        self.rag_engine = rag_engine

    def evaluate_point(self, task_point: str, vector_db) -> Tuple[int, str]:
        """Оценивает один пункт задания"""
        docs = self.rag_engine.retrieve_relevant_chunks(vector_db, task_point)
        context = self.rag_engine.get_context_from_docs(docs)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Ты эксперт, проверяющий соответствие ВКР (дипломную работу) выданному заданию. Оцени, раскрыт ли пункт в тексте.",  # noqa: E501
                ),
                (
                    "user",
                    """
Пункт задания: {task_point}

Выдержки из текста работы:
{context}

Отвечай строго по шаблону:
Балл: [число от 0 до 10]
Обоснование: [почему такая оценка]
""",
                ),
            ]
        )

        chain = prompt | self.llm_service.get_llm() | StrOutputParser()
        result = chain.invoke({"task_point": task_point, "context": context})

        return self._parse_evaluation_result(result)

    def _parse_evaluation_result(self, result_text: str) -> Tuple[int, str]:
        """Парсит результат оценки из текста"""
        score_match = re.search(r"Балл:\s*(\d+)", result_text)
        reason_match = re.search(r"Обоснование:\s*(.*)", result_text, re.DOTALL)

        score = int(score_match.group(1)) if score_match else 0
        reason = reason_match.group(1).strip() if reason_match else result_text

        return score, reason
