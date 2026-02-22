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
                    "system",
                    """Проверь приложение на
соответствие следующим требованиям:\
В приложение не включается список использованной литературы,
справочные комментарии и примечания, которые являются не приложениями
к основному тексту, а элементами справочно-сопроводительного аппарата работы,
помогающими пользоваться ее основным текстом.
Приложения оформляются как продолжение выпускной квалификационной работы на ее
последних страницах.

Важно: 
1. если приложения нет, то выводи только следующий текст и ничего больше: Статус: 10, Отчет: Нет приложения, Нарушения: Нет приложения.
2. Пиши ответ в формате текста, нельзя писать в формате markdown

Шаблон ответа:
Статус: [0-10], где 0 - приложение полностью не соответствует требованиям,
10 - приложение соответствует требованиям
Нарушения:
- ...
- ...
Обоснование: [2–3 предложения]
""",
                ),
                ("user", "".join(context)),
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
        score_match = re.search(r"Статус: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {}
