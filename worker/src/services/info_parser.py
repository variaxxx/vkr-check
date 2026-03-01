import asyncio
import io
import re
from typing import List

from .doc_processors import DocumentProcessorService
from .llm_service import LLMService


class InfoParser:
    """Класс для извлечения задания из PDF с помощью Vision (Async version)"""

    def __init__(
        self, llm_service: LLMService, doc_processor: DocumentProcessorService
    ):
        self.llm_service = llm_service
        self.doc_processor = doc_processor

    async def get_fio(self, pdf_file: io.BytesIO) -> List[str]:
        """Извлекает ФИО студентов из PDF"""

        pages = self.doc_processor.get_pages_as_base64(pdf_file, 1, 1)

        system_prompt = """Ты - эксперт по точному анализу дипломных работ. 
            Критически важные инструкции:
            1. Извлекай только ФИО студентов, выполнивших дипломную работу, другие ФИО не возвращай, ФИО руководителей возвращать НЕ нужно
            2. Извлекай ТОЛЬКО полные ФИО (Фамилия Имя Отчество полностью), игнорируй сокращенные формы ("Иванов И.И.")
            3. Если одно и то же имя встречается в полной и сокращенной форме - бери только полную
            4. Возвращай только уникальные записи, без повторений
            5. Строгий формат: Фамилия Имя Отчество - группа
            6. В случае отсутствия указания группы формат: Фамилия Имя Отчество - группа не указана
            7. Никаких пояснений"""

        user_text = "Найди на титульном листе только полные ФИО студентов, которые выполнили дипломную работу, другие ФИО возвращать не нужно. Верни только уникальные записи в формате: Фамилия Имя Отчество - группа. Каждое ФИО с новой строки."

        messages = self.llm_service.create_vision_prompt(
            user_text=user_text, pages=pages, system_prompt=system_prompt
        )
        raw_text = await self.llm_service.llm_vision_request(
            messages, max_tokens=512, temperature=0.1
        )

        raw_list = [
            p.strip() for p in raw_text.split("\n") if len(p.strip()) > 10
        ]

        return self.deduplicate_students(raw_list)

    async def get_theme(self, pdf_file: io.BytesIO) -> str:
        """Извлекает тему дипломной работы из PDF"""

        pages = self.doc_processor.get_pages_as_base64(pdf_file, 1, 3)

        system_prompt = """Ты - эксперт по точному анализу дипломных работ. В приоритете ищи тему рядом с заголовком 'Тема работы'.
            Возвращай только тему дипломной работы, без пояснений и комментариев, без заголовков по типу 'Тема работы'."""

        user_text = "Найди на этих страницах тему дипломной работы. Выведи полностью текст темы без изменений."

        messages = self.llm_service.create_vision_prompt(
            user_text=user_text, pages=pages, system_prompt=system_prompt
        )

        response = await self.llm_service.llm_vision_request(
            messages, max_tokens=512, temperature=0.1
        )

        return response.strip()

    async def get_info(self, pdf_file: io.BytesIO) -> dict:
        """Извлекает всю информацию из PDF асинхронно"""

        students_task = asyncio.create_task(self.get_fio(pdf_file))
        theme_task = asyncio.create_task(self.get_theme(pdf_file))

        students, theme = await asyncio.gather(students_task, theme_task)

        return {
            "students": students,
            "theme": theme,
        }

    def deduplicate_students(self, students: List[str]) -> List[str]:
        if not students:
            return []

        filtered_list = []
        for s in students:
            if s.count(".") >= 2:
                continue
            if len(re.findall(r"\b[А-ЯЁA-Z]\b", s)) >= 2:
                continue

            if "-" in s:
                fio_part, group_part = s.split("-", 1)
                fio_part = fio_part.strip()
                group_part = group_part.strip()

                group_part = re.sub(
                    r"[Г6Б]ИВ\s?", "БИВ", group_part, flags=re.IGNORECASE
                )

                if not re.search(r"БИВ\d+", group_part, flags=re.IGNORECASE):
                    digits = re.findall(r"\d+", group_part)
                    if digits:
                        group_part = f"БИВ{digits[0]}"
                    else:
                        group_part = "группа не указана"

                s = f"{fio_part} - {group_part}"

            if len(s) > 5:
                filtered_list.append(s)

        unique_students = []
        sorted_candidates = sorted(
            list(set(filtered_list)), key=len, reverse=True
        )

        for current in sorted_candidates:
            curr_fio_part = current.split("-")[0].strip()
            curr_words = set(curr_fio_part.lower().split())

            is_duplicate = False
            for existing in unique_students:
                exist_fio_part = existing.split("-")[0].strip()
                exist_words = set(exist_fio_part.lower().split())

                if curr_words.issubset(exist_words) or exist_words.issubset(
                    curr_words
                ):
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_students.append(current)

        return unique_students
