import json, re
from typing import List, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from .llm_service import LLMService

class HeaderClassifier:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service.get_llm()

    def classify_headers(self, extracted_chunks: List[Dict[str, str]]) -> List[Dict]:
        """Классифицирует заголовки и фильтрует мусор."""
        headers_to_process = [chunk['header'] for chunk in extracted_chunks]
        
        prompt = f"""
        Проанализируй заголовки документа и верни ТОЛЬКО JSON список.
        Категории:
        - 'annotation_ru': Аннотация на русском
        - 'annotation_en': Abstract / Annotation на английском
        - 'intro': Введение
        - 'main': Главы, параграфы, основная часть
        - 'conclusion': Заключение, выводы
        - 'biblio': Список литературы
        - 'garbage': Технический мусор (ФИО, город, год, стр. №, кафедры)

        Правила: 
        1. Исправь регистр (ВВЕДЕНИЕ -> Введение). 
        2. Формат: [{{"original": "...", "category": "...", "refined": "..."}}]
        
        Список:
        {json.dumps(headers_to_process, ensure_ascii=False)}
        """

        messages = [
            SystemMessage(content="Ты — эксперт-аналитик. Отвечаешь строго в формате JSON без пояснений."),
            HumanMessage(content=prompt)
        ]

        try:
            response = self.llm.invoke(messages)
            clean_json = re.sub(r'```json|```', '', response.content).strip()
            mapping = json.loads(clean_json)
            return self._build_final_structure(extracted_chunks, mapping)
        except Exception as e:
            print(f"Ошибка LLM: {e}")
            return [{"category": "other", "title": c['header'], "text": c['text']} for c in extracted_chunks]

    def _build_final_structure(self, chunks: List[Dict], mapping: List[Dict]) -> List[Dict]:
        """Сборка финального документа без мусора."""
        meta_map = {item['original']: item for item in mapping}
        structured_data = []

        for chunk in chunks:
            meta = meta_map.get(chunk['header'])
            
            if not meta or meta.get('category') == 'garbage':
                continue
                
            structured_data.append({
                "category": meta['category'],
                "title": meta.get('refined', chunk['header']),
                "text": chunk['text']
            })
            
        return structured_data