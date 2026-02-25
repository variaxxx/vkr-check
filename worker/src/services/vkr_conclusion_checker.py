import re
from typing import Tuple, List, Dict

from langchain_community.vectorstores import FAISS

from .llm_service import LLMService
from .rag import RAGEngine


class VKRConclusionChecker:
    def __init__(self, llm_service: LLMService, rag_engine: RAGEngine):
        self.llm_service = llm_service
        self.rag_engine = rag_engine

    async def evaluate(
        self,
        vector_db: FAISS,
        task_points: List[str],
        is_collective: bool = False,
    ) -> Tuple[int, str]:
        """
        Проверяет заключение ВКР с учётом поставленных задач (асинхронно)
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

        system_prompt = """
Ты - эксперт по проверке заключений ВКР. 
Проверяй строго по методическим указаниям. 
Если пункт отсутствует - это нарушение. 
Не додумывай за автора. 
Отвечай строго по шаблону.
"""

        user_text = """
Текст заключения:
{context}

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
"""

        prompt = self.llm_service.create_text_prompt(
            user_text=user_text, 
            system_prompt=system_prompt
        )

        result = await self.llm_service.llm_text_request(
            prompt=prompt,
            template_dict={"context": context, "formatted_tasks":formatted_tasks, "collective_note":collective_note},
            max_tokens=1024,
            temperature=0.1
        )

        return self._parse_result(result)

    def _parse_result(self, text: str) -> Tuple[int, str, Dict]:
        score_match = re.search(r"Балл:\s*(\d+)", text)
        score = int(score_match.group(1)) if score_match else 0
        return score, text, {}