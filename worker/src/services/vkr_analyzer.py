import re
from typing import Tuple

from langchain_community.vectorstores import FAISS

from .llm_service import LLMService
from .rag import RAGEngine


class VKRAnalyzer:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm_service = llm_service
        self.rag_engine = rag_engine

    async def evaluate_point(self, task_point: str, vector_db: FAISS) -> Tuple[int, str]:
        """Асинхронно оценивает пункт задания на основе извлеченного контекста"""

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

        system_prompt = """Ты эксперт, проверяющий соответствие ВКР (дипломную работу) выданному заданию.
Оцени, раскрыт ли пункт в тексте (0 - пункт вообще не упоминается в тексте, 10 - пункт полностью раскрыт в тексте). 
Отвечай строго по шаблону.
Не пиши вступлений."""

        user_text = """
Пункт задания: {task_point}
Контекст: {context}

Шаблон:
Балл: [число от 0 до 10]
Обоснование: [1-2 предложения]
"""

        prompt_template = self.llm_service.create_text_prompt(
            user_text=user_text,
            system_prompt=system_prompt
        )

        result = await self.llm_service.llm_text_request(
            prompt=prompt_template,
            template_dict={"task_point": task_point, "context": context},
            max_tokens=512,
            temperature=0
        )
        print(result)
        if not result:
            return 0, "Ошибка генерации: пустой ответ от модели"

        return self._parse_evaluation_result(result)

    def _parse_evaluation_result(self, result_text: str) -> Tuple[int, str]:
        score_match = re.search(r"Балл:\s*(\d+)", result_text)
        if not score_match:
            score_match = re.search(r"(?:Балл:\s*)?^(\d+)", result_text, re.MULTILINE)
        reason_match = re.search(r"Обоснование:\s*(.*)", result_text, re.DOTALL)

        score = int(score_match.group(1)) if score_match else 0
        reason = reason_match.group(1).strip() if reason_match else result_text
        return score, reason
