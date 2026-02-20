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
                    "system",
                    """Проверь приложение на
соответствие следующим требованиям:
В приложение не включается список использованной литературы,
справочные комментарии и примечания, которые являются не приложениями
к основному тексту, а элементами справочно-сопроводительного аппарата работы,
помогающими пользоваться ее основным текстом.
Приложения оформляются как продолжение выпускной квалификационной работы на ее
последних страницах.

Шаблон ответа:
Статус: [0-1], где 0 - приложение не соответствует требованиям,
1 - приложение соответствует требованиям
Нарушения:
- ...
- ...
Обоснование: [2–3 предложения]
""",
                ),
                ("user", context),
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
        score_match = re.search(r"Статус: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {}
