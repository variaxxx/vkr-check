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
            k=10,
            categories=["biblio"],
        )
        
        if not docs:
            return False, False, "Не найдено списка литературы"

        context = self.rag_engine.get_context_from_docs(docs)
        prompt = ChatPromptTemplate.from_messages(
            [
    (
        "system", """
Ты — строгий эксперт-нормоконтролер ВКР. Твоя задача: проверить список литературы на соответствие жестким правилам оформления.
Проверяй текст ТОЛЬКО по приведенным методическим указаниям. Каждая точка, пробел и сокращение имеют значение.
Если из-за обрезки текста элемент (например, дата обращения или номер страницы) отсутствует — фиксируй это как потенциальное нарушение или неполноту данных.
Отвечай строго по шаблону. Пиши только текст, без маркауна и специальных символов.
"""
    ),
    (
        "user", 
f"""Текст списка литературы:
{{context}}

Методические требования к оформлению литературы:
1. Нумерация: Арабские цифры БЕЗ точки в конце (например, 1 ). Абзацный отступ.
2. Пунктуация и инициалы: Между инициалами пробелы ЗАПРЕЩЕНЫ (правильно: Иванов И.И.). Кавычки в названиях книг и издательств ЗАПРЕЩЕНЫ.
3. Город и Издательство: М. и СПб. пишутся сокращенно, остальные города — полностью. После города ставится двоеточие. Слово «год» или «г.» после цифр НЕ ставится.
4. Разделители и структура:
   - Для статей: Автор. Название // Журнал. Год. №. С. 00-00. (Обязательны две косые черты).
   - Для книг (под ред.): Название / Под ред. Фамилия И.О.
   - Для конференций: Название доклада // Название мероприятия: Тема.
5. Интернет-ресурсы: Наличие URL: [ссылка] и даты обращения в формате (дата обращения: дд.мм.гггг) в скобках.

Шаблон ответа:
Балл: [0–10] (10 — идеальное соответствие)
Нарушения:
- [наиболее частые нарушения пунктов ]
- ...
Обоснование: [2–3 предложения по общей картине качества оформления и критичности ошибок].
""",
        ),
    ])

        chain = (
            prompt
            | self.llm.bind(max_tokens=2048, temperature=0.1)
            | StrOutputParser()
        )

        result = chain.invoke({"context": context})

        links_status = bool(self._check_links(raw_chunks))

        return self._parse_result(result, links_status)

    def _parse_result(
        self, result: str, links_status: bool
    ) -> Tuple[int, bool, str]:
        score_match = re.search(r"Балл: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {"if_links_exists": links_status}
