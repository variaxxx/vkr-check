import supervision as sv
from ultralytics import YOLO
from typing import List, Tuple
from PIL.Image import Image
import sys
import os
from contextlib import contextmanager
from io import BytesIO
import io
import base64

from .doc_processors import DocumentProcessorService
from .llm_service import LLMService

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "yolov8s.pt")


def base64_to_image(base64_str: str) -> Image:
    image_bytes = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_bytes))
    return image

class MarkupPages:
    def __init__(self, llm_service: LLMService, doc_processor: DocumentProcessorService):
        self.llm_service = llm_service
        self.doc_processor = doc_processor
        self.verbose = False
        self.model = YOLO(MODEL_PATH, verbose=False)

    def sign_detect(self, image: Image, threshold: float = 0.3) -> bool:
        """
        Детектит,есть ли подписи на изображении.

        :param image: Объект PIL Image или путь к изображению
        :param threshold: Порог уверенности модели (0.0-1.0)
        :return: bool(Есть ли подпись на изображении)
        :raises ValueError: Если результаты не содержат детекций
        """
        if image is None:
            raise ValueError("Изображение не может быть None")

        if self.verbose:
            results = self.model(image, conf=threshold, verbose=True)
        else:
            results = self.model(image, conf=threshold, verbose=False)

        if not results or len(results) == 0:
            raise ValueError("Модель не вернула результаты")

        detections = sv.Detections.from_ultralytics(results[0])

        detections_list = detections.xyxy.tolist()
        detections_list = [((int(x1), int(y1)), (int(x2), int(y2))) for x1, y1, x2, y2 in detections_list]
        return len(detections_list) > 0

    def markup_pdf(self, pdf_bytes: io.BytesIO) -> bool:
        """
        Определяет везде ли есть подписи на изображении.
        return: bool
        """

        pages = self.doc_processor.get_pages_as_base64(pdf_bytes)
        pages_images = [base64_to_image(page) for page in pages]
        pages_indeces = [i for i, page in enumerate(pages_images) if self.sign_detect(page)]
        pages_markup = [pages[i] for i in pages_indeces]
        count = len(pages_indeces)
        if count == 0:
            return False
        c: int = 0
        for b64 in pages_markup:
            content = [
                {
                    "type": "text", "text": "Определи, везде ли на этом изображении проставлены подписи? Ответь '1', "
                "если проставлены все подписи, либо '0', если не все подписи проставлены. "
                "Важно: Каждая подпись должна соотвествовать фамилии, если пустой блок без фамилии, то это НЕ считается отсутствием подписи."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                }
            ]
            answer = self.llm_service.invoke_vision(content)
            if answer == '1':
                c += 1

        return count == c
