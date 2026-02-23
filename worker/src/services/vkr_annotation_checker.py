import re
from typing import Tuple, List, Dict

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .llm_service import LLMService
from .rag import RAGEngine


class VKRAnnotationChecker:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm = llm_service.get_llm()
        self.rag_engine = rag_engine

    def evaluate(self, chunks: List[Dict])  -> Tuple[int, str]:
        """
        Проверяет аннотации ВКР по методичке
        """


        context_ru: List = [i["text"] for i in chunks if i.get("category") == "annotation_ru"]
        context_en: List = [i["text"] for i in chunks if i.get("category") == "annotation_en"]

        for context in [context_ru, context_en]:
            char_count = len(context)

            volume_violation = ""
            if char_count > 2000:
                volume_violation = (
                    f"Превышен допустимый объем аннотации: {char_count} знаков (максимум 2000)."
                )
        
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
Текст аннотации на русском:
{{context_ru}}
Текст аннотации на английском:
{{context_en}}

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
- Количество знаков в тексте на русском: {char_count}
- Количество знаков в тексте на английском: {char_count}
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
            | self.llm.bind(max_tokens=1024, temperature=0)
            | StrOutputParser()
        )

        result = chain.invoke({"context_ru": context_ru, "context_en": context_en})

        if volume_violation and volume_violation not in result:
            result += f"\n- {volume_violation}"

        return self._parse_result(result)

    def _parse_result(self, text: str) -> Tuple[int, str]:
        score_match = re.search(r"Балл:\s*(\d+)", text)
        score = int(score_match.group(1)) if score_match else 0
        return score, text, {}