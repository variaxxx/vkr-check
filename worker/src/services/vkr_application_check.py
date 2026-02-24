import re
from typing import Tuple, Dict, List
import asyncio

from src.services.llm_service import LLMService

class ApplicationChecker:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def evaluate(self, chunks: List[Dict]) -> Tuple[int, str, Dict]:
        """
        Проверяет правильность приложения (асинхронно)
        """

        context_list = [i["title"] + "\n" + i["text"] for i in chunks if i.get("category") == "application"]
        context_text = "\n".join(context_list)

        system_prompt = """
Ты — строгий эксперт по проверке ВКР.
Проверяй приложение ТОЛЬКО по методическим указаниям.
Каждое слово требований важно.
Обязательно указывай расхождения.
Отвечай строго по шаблону.
"""

        user_content = """Текст приложений:
{context_text}

Методические требования к оформлению приложений:
1. Указано слово «Приложение» и тематический заголовок.
2. В приложении должны отсутствовать список литературы, комментарии и примечания.
3. Содержание соответствует справочному характеру (например: копии документов, таблицы, графики, акты, программный код).

Важно: 
1. если приложения нет, то выводи только следующий текст и ничего больше: Балл: 10, Отчет: Нет приложения, Нарушения: Нет приложения.
2. Пиши ответ в формате текста, нельзя писать в формате markdown

Шаблон ответа:

Балл: [0-10], (0 - приложение полностью не соответствует требованиям, 10 - приложение полностью соответствует требованиям)
Нарушения:
- ...
- ...
Обоснование: [2–3 предложения]
"""

        prompt_template = self.llm_service.create_text_prompt(
            user_text=user_content,
            system_prompt=system_prompt
        )

        result = await self.llm_service.llm_text_request(
            prompt=prompt_template,
            template_dict={"context_text":context_text},
            max_tokens=1024,
            temperature=0.1
        )

        return self._parse_result(result)

    def _parse_result(self, result: str) -> Tuple[int, str, Dict]:
        score_match = re.search(r"Балл: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {}
    