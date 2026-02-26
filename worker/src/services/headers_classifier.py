import asyncio
import json
import re
from typing import Dict, List

from .llm_service import LLMService


class HeaderClassifier:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.batch_size = 10

    async def classify_headers(self, extracted_chunks: List[Dict[str, str]]) -> List[Dict]:
        """Классифицирует заголовки ПАРАЛЛЕЛЬНО и фильтрует мусор."""

        all_headers = [chunk["header"] for chunk in extracted_chunks]

        batches = [all_headers[i:i + self.batch_size] for i in range(0, len(all_headers), self.batch_size)]

        tasks = [self._process_batch(batch) for batch in batches]

        results = await asyncio.gather(*tasks)

        all_mappings = []
        for batch_mapping in results:
            if batch_mapping:
                all_mappings.extend(batch_mapping)

        return self._build_final_structure(extracted_chunks, all_mappings)

    async def _process_batch(self, batch_headers: List[str]) -> List[Dict]:
        """Обработка одной группы заголовков."""
        system_prompt = "Ты — эксперт-аналитик. Отвечаешь строго в формате JSON списка без пояснений."

        user_text = """
Проанализируй заголовки документа и верни ТОЛЬКО JSON список.
Категории:
- 'annotation_ru': Аннотация на русском
- 'annotation_en': Abstract / Annotation на английском
- 'intro': Введение, акутальность, цели, задачи
- 'main': Главы, параграфы, основная часть
- 'conclusion': Заключение, выводы, результаты
- 'biblio': Список литературы, список использованной литературы
- 'application': Приложение к документу
- 'garbage': Технический мусор (ФИО, город, год, стр. №, кафедры)

Правила:
1. Исправь регистр (ВВЕДЕНИЕ -> Введение).
2. Формат: [{{"original": "...", "category": "...", "refined": "..."}}]

Список:
""" + json.dumps(batch_headers, ensure_ascii=False)

        prompt_template = self.llm_service.create_text_prompt(
            user_text=user_text,
            system_prompt=system_prompt,
        )

        try:
            response_content = await self.llm_service.llm_text_request(
                prompt_template,
                max_tokens=1024,
                temperature=0.1
            )

            clean_json = re.sub(r"```json|```", "", response_content).strip()

            data = json.loads(clean_json)
            return data if isinstance(data, list) else []

        except Exception as e:
            print(f"Ошибка при обработке батча LLM: {e}")
            return [{"original": h, "category": "other", "refined": h} for h in batch_headers]

    def _build_final_structure(self, chunks: List[Dict], mapping: List[Dict]) -> List[Dict]:
        """Сборка финального документа, исключая 'garbage'."""
        meta_map = {item["original"]: item for item in mapping if isinstance(item, dict) and "original" in item}
        structured_data = []

        for chunk in chunks:
            header_text = chunk["header"]
            meta = meta_map.get(header_text)

            if meta and meta.get("category") == "garbage":
                continue

            structured_data.append({
                "category": meta.get("category", "other") if meta else "other",
                "title": meta.get("refined", header_text) if meta else header_text,
                "text": chunk["text"],
            })

        return structured_data
