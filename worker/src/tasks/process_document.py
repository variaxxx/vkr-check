import io
import uuid
from typing import Union

from sqlalchemy.orm import Session

from src.common.enums import DocumentStatus
from src.core.di import run_in_di
from src.infra.db.models import Author, Document
from src.infra.minio import MinioService
from src.main import worker
from src.services.info_parser import InfoParser
from src.services.pdf_processor import PDFProcessor
from src.services.rag import RAGEngine
from src.services.task_parser import TaskParser
from src.services.vkr_analyzer import VKRAnalyzer
from src.services.vkr_report import VKRReport
from src.services.pages_markup import MarkupPages


@worker.task(
    name="ml.process_document",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={
        "max_retries": 3,
        "countdown": 10,
    },
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
@run_in_di
def process_document(di, self, doc_id: Union[uuid.UUID, str]):
    doc_id = uuid.UUID(doc_id) if isinstance(doc_id, str) else doc_id

    # DEPS
    db: Session = di.get(Session)
    minio: MinioService = di.get(MinioService)
    task_parser: TaskParser = di.get(TaskParser)
    info_parser: InfoParser = di.get(InfoParser)
    pdf_processor: PDFProcessor = di.get(PDFProcessor)
    rag_engine: RAGEngine = di.get(RAGEngine)
    vkr_analyzer: VKRAnalyzer = di.get(VKRAnalyzer)
    vkr_report: VKRReport = di.get(VKRReport)
    sign_verify: MarkupPages = di.get(MarkupPages)

    doc = db.get(Document, doc_id)

    if doc is None:
        return

    doc.status = DocumentStatus.IN_PROCESSING
    db.commit()

    try:

        bucket_name = doc.file_url.split("/")[0]
        object_name = doc.file_url[len(bucket_name) + 1 :]

        file_response = minio.client.get_object(
            bucket_name=bucket_name, object_name=object_name
        )
        file_buffer = io.BytesIO(file_response.read())
        #блок вериифкации подписи
        sign_verify_status = sign_verify.markup_pdf(file_buffer)
        if not sign_verify_status:
            raise Exception("Верификация подписей не прошла")

        task_points = task_parser.get_task_points(file_buffer)
        info = info_parser.get_info(file_buffer)

        full_text = pdf_processor.extract_text_from_pdf(file_buffer)
        vector_db = rag_engine.create_vector_db(full_text)

        evaluations = []

        for point in task_points:
            print(point)
            score, reason = vkr_analyzer.evaluate_point(point, vector_db)

            evaluations.append(
                {"task_point": point, "score": score, "justification": reason}
            )

        report = vkr_report.generate_report(info, evaluations)

        for student in info.students:
            author = Author(
                last_name=student.split()[0],
                first_name=student.split()[1],
                middle_name=student.split()[2],
            )
            db.add(author)
            doc.authors.append(author)

        doc.score = report.summary.average_score


        doc.status = DocumentStatus.SUCCESS
        doc.topic = info.theme
        db.commit()
    except Exception:
        doc.status = DocumentStatus.FAILED
        db.commit()
