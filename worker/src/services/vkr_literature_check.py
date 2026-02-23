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

    def evaluate(self, chunks: List[Dict]) -> Tuple[int, str, Dict[str, bool]]:
        """
        Проверяет правильность списка литературы
        """

        context: List = [i["text"] for i in chunks if i.get("category") == "biblio"]
        
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
{"".join(context)}

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
Балл: [0–10] (0 - список литературы полностью не соответствует требованиям, 10 — идеальное соответствие)
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

        links_status = bool(self._check_links(chunks))

        return self._parse_result(result, links_status)

    def _parse_result(self, result: str, links_status: bool) -> Tuple[int, str, Dict[str, bool]]:
        score_match = re.search(r"Балл: (\d+)", result)
        score = int(score_match.group(1)) if score_match else 0
        return score, result, {"if_links_exists": links_status}
