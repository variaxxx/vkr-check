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
                    "Определи, заполнены ли подписи у всех фамилий на изображении.",

"Правила проверки:",
	"1.	Рассматривай только случаи, где рядом с фамилией есть блок с подписью.",
	"2.	Для каждой фамилии рядом должен быть блок с подписью (непустой).",
	"3.	Каждую фамилию оценивай отдельно. Если фамилия встречается несколько раз, то каждое её появление должно иметь непустую подпись в своём блоке. Если хотя бы у одного появления подписи нет → итог 0.(если идут несколько фамилий подряд, то для каждой из них должен быть блок с подписью рядом)",
	"4.	Пустой блок без фамилии рядом — игнорируй (не влияет).",
	"5.	Пустой блок рядом с фамилией — это отсутствие подписи → итог 0.",
	"6.	Фамилия без блока рядом — не считается отсутствием подписи (не влияет).",
    "7. Подпись должна занимать значимую часть блока рядом с фамилией, а не быть маленькой пометкой в углу.Иначе - '0'",
    "8. Блоком является область, которая подчеркнута линией",
    "9. Если подряд идут одинаковые фамилии, то обязательно проверь для каждой ",
                    "Обязательно: Ответь обычным текстом в формате:",
                    "[ОТВЕТ]: '1' или '0'",
                    "[ПОЯСНЕНИЕ]: Текст с пояснением, почему ты так решил"
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
