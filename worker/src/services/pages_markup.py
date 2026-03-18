import base64
import io
import os
import re
from io import BytesIO
from typing import List, Tuple

import supervision as sv
from PIL import Image as PILImage
from ultralytics import YOLO

from .doc_processors import DocumentProcessorService
from .llm_service import LLMService

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "yolov8s.pt")


def base64_to_image(base64_str: str) -> PILImage.Image:
    image_bytes = base64.b64decode(base64_str)
    image: PILImage.Image = PILImage.open(BytesIO(image_bytes))
    return image


class MarkupPages:
    def __init__(
        self, llm_service: LLMService, doc_processor: DocumentProcessorService
    ):
        self.llm_service = llm_service
        self.doc_processor = doc_processor
        self.verbose = False
        self.model = YOLO(MODEL_PATH, verbose=False)

    def sign_detect(
        self, image: PILImage.Image, threshold: float = 0.3
    ) -> bool:
        """
        Детектит, есть ли подписи на изображении.
        """
        if image is None:
            raise ValueError("Изображение не может быть None")

        results = self.model(image, conf=threshold, verbose=self.verbose)

        if not results or len(results) == 0:
            raise ValueError("Модель не вернула результаты")

        detections = sv.Detections.from_ultralytics(results[0])
        return len(detections.xyxy) > 0

    async def markup_pdf(self, pdf_bytes: io.BytesIO) -> Tuple[bool, List[int]]:
        """
        Определяет везде ли есть подписи на изображении.
        Теперь работает асинхронно.
        """

        pages = self.doc_processor.get_pages_as_base64(pdf_bytes, 1, 25)

        pages_images = [base64_to_image(page) for page in pages]

        pages_indices = [
            i for i, page in enumerate(pages_images) if self.sign_detect(page)
        ]

        count = len(pages_indices)
        if count == 0:
            return False, []

        prompt_text = (
            {
    "Твоя задача — определить, стоят ли подписи у всех фамилий на изображении.\n\n"
    "Отвечай 0, если нет хотя бы одной подписи. 1 - если есть все подписи\n\n"
    "Работай максимально осторожно: если есть сомнение, что подпись присутствует — считай, что она есть.\n\n"
    "Определения:\n"
    "- \"Фамилия\" — текст с ФИО или фамилией человека.\n"
    "- \"Подпись\" — любой рукописный текст, росчерк, линия с заполнением или надпись рядом с фамилией.\n"
    "- Если фамилия написана синим цветом — это уже считается подписью.\n\n"
    "Правила:\n"
    "1. Для каждой фамилии проверь, есть ли рядом подпись.\n"
    "2. Подпись считается присутствующей, если рядом есть:\n"
    "   - рукописный текст,\n"
    "   - росчерк,\n"
    "   - линия, которая выглядит заполненной,\n"
    "   - или фамилия написана синим цветом.\n"
    "3. Если рядом с фамилией пустая линия/пустой блок без подписи → это отсутствие подписи.\n"
    "4. Пустые блоки без фамилии рядом — игнорируй.\n"
    "5. Если у фамилии нет отдельного блока для подписи — игнорируй (это не ошибка).\n"
    "6. Если не уверен, пустой блок или нет — считай, что подпись есть (важно для повышения recall).\n\n"
    "Формат ответа (строго):\n"
    "[ОТВЕТ]: 1 или 0\n"
    "[ПОЯСНЕНИЕ]: перечисли фамилии без подписи (если таких нет — напиши \"все подписи присутствуют\")"
                }
        )

        success_count = 0
        answer_pattern = re.compile(r"\[ОТВЕТ\]\s*:\s*['\"]?([01])['\"]?", re.IGNORECASE)

        for idx in pages_indices:
            b64_image = pages[idx]

            messages = self.llm_service.create_vision_prompt(
                user_text=prompt_text,
                pages=[b64_image]
            )

            answer = await self.llm_service.llm_vision_request(messages)
            print("[DEBUG] Ответ модели по подписям: ", answer)
            print("[]Конец ответа")
            match = answer_pattern.search(answer)
            parsed_answer = match.group(1) if match else None
            if parsed_answer == "1":
                success_count += 1

        return count == success_count, pages_indices
