import re
from typing import Tuple, Dict

from langchain_community.vectorstores import FAISS

from .llm_service import LLMService
from .rag import RAGEngine


class VKRIntroductionChecker:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm_service = llm_service
        self.rag_engine = rag_engine

    async def evaluate(self, vector_db: FAISS, total_doc_volume: int) -> Tuple[int, str]:
        """
        Проверяет введение на соответствие методическим указаниям (асинхронно)
        """

        docs = self.rag_engine.retrieve_relevant_chunks(
            vector_db,
            query="Введение цели задачи актуальность новизна результаты",
            categories=["intro"],
            k=10
        )

        context = self.rag_engine.get_context_from_docs(docs)

        system_prompt = """
Ты — строгий эксперт по проверке ВКР.
Проверяй введение ТОЛЬКО по методическим указаниям.
Каждое слово требований важно.
Если элемент отсутствует или выражен неявно - считай, что он НЕ выполнен.
Обязательно указывай расхождения.
Отвечай строго по шаблону.
"""
        user_text = """
Текст введения:
{context}

Методические требования к введению:
1. Содержит цели работы
2. Содержит задачи работы
3. Содержит актуальность
4. Обоснована актуальность
5. Содержит основные результаты анализа существующих технических решений
6. Содержит инструментальные средства, используемые при выполнении ВКР
7. Содержит программные средства, используемые при выполнении ВКР
8. Содержит результаты, полученные в ходе выполнения ВКР
9. Объем введения не превышает 10% от объема ВКР (объем ВКР: {total_doc_volume} условных единиц)

Шаблон ответа:
Балл: [0–10]
Нарушения:
- ...
- ...
Обоснование: [2–3 предложения]
"""

        prompt = self.llm_service.create_text_prompt(
            user_text=user_text, 
            system_prompt=system_prompt
        )

        result = await self.llm_service.llm_text_request(
            prompt=prompt,
            template_dict={"context": context, "total_doc_volume":total_doc_volume},
            max_tokens=1024,
            temperature=0.1
        )

        return self._parse_result(result)

    def _parse_result(self, text: str) -> Tuple[int, str, Dict]:
        score_match = re.search(r"Балл:\s*(\d+)", text)
        score = int(score_match.group(1)) if score_match else 0
        return score, text, {}