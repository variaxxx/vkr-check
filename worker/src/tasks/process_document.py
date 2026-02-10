import io
import uuid
import json
from typing import Union

from sqlalchemy.orm import Session

from src.common.enums import DocumentStatus
from src.core.di import run_in_di
from src.infra.db.models import Author, Document
from src.infra.minio import MinioService
from src.main import worker
from src.services.info_parser import InfoParser
from src.services.doc_processors import DocumentProcessorService 
from src.services.rag import RAGEngine
from src.services.task_parser import TaskParser
from src.services.vkr_analyzer import VKRAnalyzer
from src.services.vkr_report import VKRReport
from src.services.pages_markup import MarkupPages
from src.services.headers_classifier import HeaderClassifier

ALLOWED_FILE_TYPES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/pdf",
]

@worker.task(
    name="ml.process_document",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
@run_in_di
def process_document(di, self, doc_id: Union[uuid.UUID, str]):
    doc_id = uuid.UUID(doc_id) if isinstance(doc_id, str) else doc_id

    db: Session = di.get(Session)
    minio: MinioService = di.get(MinioService)
    task_parser: TaskParser = di.get(TaskParser)
    info_parser: InfoParser = di.get(InfoParser)
    doc_service: DocumentProcessorService = di.get(DocumentProcessorService)
    rag_engine: RAGEngine = di.get(RAGEngine)
    vkr_analyzer: VKRAnalyzer = di.get(VKRAnalyzer)
    vkr_report: VKRReport = di.get(VKRReport)
    # sign_verify: MarkupPages = di.get(MarkupPages)
    header_classifier: HeaderClassifier = di.get(HeaderClassifier)

    doc = db.get(Document, doc_id)
    if doc is None:
        return

    doc.status = DocumentStatus.IN_PROCESSING
    db.commit()

    try:
        bucket_name, object_name = doc.file_url.split("/", 1)
        obj_stat = minio.client.stat_object(bucket_name, object_name)
        
        doc_service.set_context(obj_stat.content_type)

        file_response = minio.client.get_object(bucket_name, object_name)
        file_buffer = io.BytesIO(file_response.read())

        # if doc_service.is_pdf():
        #     if not sign_verify.markup_pdf(file_buffer):
        #         raise Exception("Верификация подписей не прошла")

        task_points = task_parser.get_task_points(file_buffer)
        file_buffer.seek(0)
        fio_list = info_parser.get_fio(file_buffer)
        file_buffer.seek(0)
        theme = info_parser.get_theme(file_buffer)
        file_buffer.seek(0)

        raw_chunks = doc_service.get_structured_text(file_buffer)
        classified_chunks = header_classifier.classify_headers(raw_chunks)
        vector_db = rag_engine.create_vector_db(classified_chunks)

        evaluations = []
        for point in task_points:
            score, reason = vkr_analyzer.evaluate_point(point, vector_db)
            evaluations.append(
                {"task_point": point, "score": score, "justification": reason}
            )

        info_data = {"students": fio_list, "theme": theme}
        report_json = vkr_report.generate_report(info_data, evaluations)
        report_dict = json.loads(report_json)

        for student in fio_list:
            parts = student.split()
            author = Author(
                last_name=parts[0] if len(parts) > 0 else "Unknown",
                first_name=parts[1] if len(parts) > 1 else "",
                middle_name=parts[2] if len(parts) > 2 else "",
            )
            db.add(author)
            doc.authors.append(author)

        doc.score = report_dict["summary"].get("average_score", 0)
        doc.topic = theme if isinstance(theme, str) else (theme[0] if theme else "")
        doc.status = DocumentStatus.SUCCESS
        doc.result = report_json
        db.commit()

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        doc.status = DocumentStatus.FAILED
        db.commit()