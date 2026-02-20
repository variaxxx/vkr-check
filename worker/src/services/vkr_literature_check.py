import re
from typing import Dict, List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.services.llm_service import LLMService
from src.services.rag import RAGEngine


class LiteratureChecker:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm = llm_service.get_llm()
        self.rag_engine = rag_engine

    def _check_links(self, raw_chunks: List[Dict[str, str]]) -> bool:
        """Топорная логика на наличие ссылок в списке литературы"""
        counter: int = 0
        # print(raw_chunks)
        for _, chunk in enumerate(raw_chunks):
            text = chunk.get("text", "")
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
            counter += len(links)
        return counter > 0

    def evaluate(
        self, vector_db: FAISS, raw_chunks: List[Dict[str, str]]
    ) -> Tuple[int, bool, str]:
        """
        Проверяет правильность списка литературы
        """
        # print(raw_chunks[-5:])
        docs = self.rag_engine.retrieve_relevant_chunks(
            vector_db=vector_db,
            query="Список литературы литература ссылки источники",
            k=3,
            categories=["biblio"],
        )

        if not docs:
            return False, False, "Не найдено списка литературы"

        context = self.rag_engine.get_context_from_docs(docs)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Проверь список литературы,
соотвествующий следующим требованиям:
1.	Проверка порядка источников\
2.	Проверка формата библиографических записей

    - книги
    - статьи
    - конференции
    - интернет-источники

3.	Проверка наличия URL и даты обращения для онлайн-источников

Шаблон ответа:
Статус: [0-1], где 0 - список литературы не соответствует требованиям, 1 - список литературы соответствует требованиям
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
            | self.llm.bind(max_tokens=600, temperature=0)
            | StrOutputParser()
        )

        result = chain.invoke({"context": context})

        links_status = bool(self._check_links(raw_chunks))

        return self._parse_result(result, links_status)

    def _parse_result(
        self, result: str, links_status: bool
    ) -> Tuple[int, bool, str]:
        score_match = re.search(r"Статус: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {"if_links_exists": links_status}
