import re
from typing import Dict, List, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.services.llm_service import LLMService


class LiteratureChecker:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service.get_llm()

    def _check_links(self, classified_chunks: List[Dict]) -> bool:
        """Топорная логика на наличие ссылок в списке литературы"""
        counter: int = 0
        for _, chunk in enumerate(classified_chunks):
            text = chunk.get("text", "")
            refs = re.findall(r"\[(\d+)\]", text)
            counter += len(refs)
        return counter > 0

    def evaluate(
        self, chunks: List[Dict]
    ) -> Tuple[int, str, Dict[str, bool]]:
        """
        Проверяет правильность списка литературы
        """

        context: List = [i["text"] for i in chunks if i.get("category") == "biblio"]
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
Статус: [0-10], где 0 - список литературы полностью не соответствует требованиям, 1 - список литературы соответствует требованиям
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
            | self.llm.bind(max_tokens=600, temperature=0)
            | StrOutputParser()
        )

        result = chain.invoke({"context": context})

        links_status = bool(self._check_links(chunks))

        return self._parse_result(result, links_status)

    def _parse_result(
        self, result: str, links_status: bool
    ) -> Tuple[int, str, Dict[str, bool]]:
        score_match = re.search(r"Статус: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {"if_links_exists": links_status}
