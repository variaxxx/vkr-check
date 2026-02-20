import re
from typing import Tuple, List

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .llm_service import LLMService
from .rag import RAGEngine


class VKRConclusionChecker:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm = llm_service.get_llm()
        self.rag_engine = rag_engine

    def evaluate(
        self,
        vector_db: FAISS,
        task_points: List[str],
        is_collective: bool = False,
    ) -> Tuple[int, str]:
        """
        Проверяет заключение ВКР с учётом поставленных задач
        """

        docs = self.rag_engine.retrieve_relevant_chunks(
            vector_db,
            query="Заключение результаты практическая значимость внедрение развитие",
            categories=["conclusion"],
            k=10,
        )

        context = self.rag_engine.get_context_from_docs(docs)

        formatted_tasks = "\n".join(
            [f"{i+1}. {task}" for i, task in enumerate(task_points)]
        )

        collective_note = (
            "Для коллективных ВКР обязательно должно быть описано, какие результаты получены каждым автором самостоятельно."
            if is_collective
            else "Работа не является коллективной."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
Ты - эксперт по проверке заключений ВКР. 
Проверяй строго по методическим указаниям. 
Если пункт отсутствует - это нарушение. 
Не додумывай за автора. 
Отвечай строго по шаблону.
""",
                ),
                (
                    "user",
                    f"""
Текст заключения:
{{context}}

Поставленные задачи ВКР:
{formatted_tasks}

Методические требования к заключению: 
1. Содержит основные научные результаты и практические результаты, полученные при выполнении ВКР, соответствующие перечню поставленных задач 
2. Содержит практическую значимость полученных результатов 
3. Содержит направления работ по развитию и совершенствованию объекта разработки или исследования 
4. {collective_note}

Опционально могут быть приведены:
1. Результаты внедрения
2. Предложения по внедрению и тиражированию
3. Оценка эффективности внедрения (если упоминается)

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
        return self._parse_result(result)

    def _parse_result(self, text: str) -> Tuple[int, str]:
        score_match = re.search(r"Балл:\s*(\d+)", text)
        score = int(score_match.group(1)) if score_match else 0
        return score, text