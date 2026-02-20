import re
from typing import Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .llm_service import LLMService
from .rag import RAGEngine


class VKRAnnotationChecker:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm = llm_service.get_llm()
        self.rag_engine = rag_engine

    def evaluate(
        self,
        vector_db: FAISS,
    ) -> Tuple[int, str]:
        """
        Проверяет аннотации ВКР по методичке
        """

        docs = self.rag_engine.retrieve_relevant_chunks(
            vector_db,
            query="Аннотация abstract объект цель результаты рекомендации объем таблиц источников",
            categories=["annotation"],
            k=10,
        )

        context = self.rag_engine.get_context_from_docs(docs)

        char_count = len(context)

        volume_violation = ""
        if char_count > 2000:
            volume_violation = (
                f"Превышен допустимый объем аннотации: {char_count} знаков (максимум 2000)."
            )

        has_english = bool(re.search(r"[A-Za-z]{4,}", context))

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
Ты - эксперт по проверке аннотаций ВКР.
Проверяй строго по методическим указаниям.
Если элемент отсутствует - это нарушение.
Не додумывай.
Отвечай строго по шаблону.
""",
                ),
                (
                    "user",
                    f"""
Текст аннотации:
{{context}}

Методические требования:
1. Аннотация должна быть представлена на русском и английском языках
2. Должны быть указаны:
   a) объект разработки
   б) цель работы
   в) краткое описание полученных результатов
   г) рекомендации по использованию результатов и направления дальнейших разработок
3. Должны быть указаны сведения:
   a) объем работы
   б) количество иллюстраций
   в) количество таблиц
   в) количество использованных источников
4. Объем аннотации не должен превышать 2000 знаков

Дополнительная информация:
- Количество знаков в тексте: {char_count}
- Наличие английского текста: {"да" if has_english else "нет"}
- Нарушение объема: {volume_violation if volume_violation else "нет"}

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
            | self.llm.bind(max_tokens=600, temperature=0)
            | StrOutputParser()
        )

        result = chain.invoke({"context": context})

        if volume_violation and volume_violation not in result:
            result += f"\n- {volume_violation}"

        return self._parse_result(result)

    def _parse_result(self, text: str) -> Tuple[int, str]:
        score_match = re.search(r"Балл:\s*(\d+)", text)
        score = int(score_match.group(1)) if score_match else 0
        return score, text