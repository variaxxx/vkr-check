import re
from typing import Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.services.llm_service import LLMService
from src.services.rag import RAGEngine


class ApplicationChecker:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm = llm_service.get_llm()
        self.rag_engine = rag_engine

    def evaluate(self, vector_db: FAISS) -> Tuple[int, str]:
        """
        Проверяет правильность приложения
        """

        docs = self.rag_engine.retrieve_relevant_chunks(
            vector_db=vector_db,
            query="приложение application",
            k=20,
            categories=["application"],
        )

        if not docs:
            return False, "Не найдено приложение"

        context = self.rag_engine.get_context_from_docs(docs)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", """
Ты — строгий эксперт по проверке ВКР.
Проверяй приложение ТОЛЬКО по методическим указаниям.
Каждое слово требований важно.
Если элемент отсутствует или выражен неявно - считай, что он НЕ выполнен.
Обязательно указывай расхождения.
Отвечай строго по шаблону.
"""
                ),

                    ("user", 
f"""Текст приложений:
{{context}}

Методические требования к оформлению приложений:
1. Указано слово «Приложение» и тематический заголовок.
2. Приложения пронумерованы (цифры, русские или латинские буквы), если их больше одного.
3. В приложении отсутствуют список литературы, справочные комментарии и примечания.
4. Содержание соответствует справочному характеру (копии документов, таблицы, графики, акты).

Шаблон ответа:
Балл: [0–10]
Нарушения:
- ...
- ...
Обоснование: [2–3 предложения]
""",
                ),
            ]
        )

        chain = (
            prompt
            | self.llm.bind(max_tokens=1024, temperature=0)
            | StrOutputParser()
        )

        result = chain.invoke({"context": context})

        return self._parse_result(result)

    def _parse_result(self, result: str) -> Tuple[int, str]:
        score_match = re.search(r"Балл: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {}
