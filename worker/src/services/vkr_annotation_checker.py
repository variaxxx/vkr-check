import re
import asyncio
from typing import Tuple, List, Dict

from .llm_service import LLMService
from .rag import RAGEngine


class VKRAnnotationChecker:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm_service = llm_service
        self.rag_engine = rag_engine

    async def evaluate(self, chunks: List[Dict]) -> Tuple[int, str]:
        """
        Проверяет аннотации ВКР по методичке, используя методы LLMService.
        """

        context_ru = "".join([i["text"] for i in chunks if i.get("category") == "annotation_ru"])
        context_en = "".join([i["text"] for i in chunks if i.get("category") == "annotation_en"])

        len_ru = len(context_ru)
        len_en = len(context_en)
        
        violations = []
        if len_ru > 2000:
            violations.append(f"Превышен объем RU: {len_ru} зн.")
        if len_en > 2000:
            violations.append(f"Превышен объем EN: {len_en} зн.")
        
        volume_violation_str = "; ".join(violations) if violations else "нет"

        system_msg = (
            "Ты - эксперт по проверке аннотаций ВКР. "
            "Проверяй строго по методическим указаниям. "
            "Если элемент отсутствует - это нарушение. "
            "Не додумывай. Отвечай строго по шаблону."
        )

        user_msg = """
Текст аннотации на русском:
{context_ru}

Текст аннотации на английском:
{context_en}

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
   г) количество использованных источников
4. Объем аннотации не должен превышать 2000 знаков

Дополнительная информация:
- Количество знаков в тексте на русском: {len_ru}
- Количество знаков в тексте на английском: {len_en}
- Нарушение объема: {volume_violation_str}

Шаблон ответа:
Балл: [0–10]
Нарушения:
- ...
- ...
Обоснование: [2–3 предложения]
"""

        prompt_template = self.llm_service.create_text_prompt(
            user_text=user_msg, 
            system_prompt=system_msg
        )

        result = await self.llm_service.llm_text_request(
            prompt=prompt_template,
            template_dict={
                "context_ru":context_ru,
                "context_en":context_en,
                "len_ru":len_ru,
                "len_en":len_en,
                "volume_violation_str":volume_violation_str
            }, 
            max_tokens=1024,
            temperature=0.1
        )

        if volume_violation_str != "нет" and "Нарушение объема" not in result:
            result += f"\n- Нарушение объема: {volume_violation_str}"

        return self._parse_result(result)

    def _parse_result(self, text: str) -> Tuple[int, str, Dict]:
        score_match = re.search(r"Балл:\s*(\d+)", text)
        score = int(score_match.group(1)) if score_match else 0
        return score, text, {}