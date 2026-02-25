import io
import os
import asyncio
from io import BytesIO
from typing import List, Tuple
import base64 

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
            "Определи, везде ли на этом изображении проставлены подписи рядом с фамилиями(Оценивай нестрого)? "
            "Ответь '1', если проставлены все подписи(блок без фамилии не считается за отсутствие подписи), "
            "либо '0', если не все подписи проставлены. "
            "Важно: Если стоит пустой блок и нет фамилии, то это '1', если стоит пустой блок и рядом есть фамилия, "
            "то это '0', если стоит фамилия без блока, то это '1'"
        )

        success_count = 0
        
        for idx in pages_indices:
            b64_image = pages[idx]
            
            messages = self.llm_service.create_vision_prompt(
                user_text=prompt_text,
                pages=[b64_image]
            )
            
            answer = await self.llm_service.llm_vision_request(messages)
            
            if "1" in answer:
                success_count += 1

        return count == success_count, pages_indices