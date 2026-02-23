import re
from typing import Tuple, Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.services.llm_service import LLMService


class ApplicationChecker:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service.get_llm()

    def evaluate(self,  chunks: List[Dict]) -> Tuple[int, str, Dict]:
        """
        Проверяет правильность приложения
        """


        ## тут из классифицированных чанков.
        context: List = [i["text"] for i in chunks if i.get("category") == "application"]

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
{"".join(context)}

Методические требования к оформлению приложений:
1. Указано слово «Приложение» и тематический заголовок.
2. Приложения пронумерованы (цифры, русские или латинские буквы), если их больше одного.
3. В приложении отсутствуют список литературы, справочные комментарии и примечания.
4. Содержание соответствует справочному характеру (копии документов, таблицы, графики, акты).

Важно: 
1. если приложения нет, то выводи только следующий текст и ничего больше: Балл: 10, Отчет: Нет приложения, Нарушения: Нет приложения.
2. Пиши ответ в формате текста, нельзя писать в формате markdown

Шаблон ответа:

Балл: [0-10], (0 - приложение полностью не соответствует требованиям, 10 - приложение полностью соответствует требованиям)
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

    def _parse_result(self, result: str) -> Tuple[int, str, Dict]:
        score_match = re.search(r"Балл: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {}
