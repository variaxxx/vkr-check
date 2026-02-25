import asyncio
import io
import uuid
from typing import Any, Dict, Union

from sqlalchemy.orm import Session

from src.common.enums import DocumentStatus
from src.core.di import run_in_di
from src.infra.db.models import Author, Document
from src.infra.minio import MinioService
from src.main import worker
from src.services.doc_processors import DocumentProcessorService
from src.services.headers_classifier import HeaderClassifier
from src.services.info_parser import InfoParser
from src.services.pages_markup import MarkupPages
from src.services.rag import RAGEngine
from src.services.task_parser import TaskParser
from src.services.vkr_analyzer import VKRAnalyzer
from src.services.vkr_annotation_checker import VKRAnnotationChecker
from src.services.vkr_application_check import ApplicationChecker
from src.services.vkr_conclusion_checker import VKRConclusionChecker
from src.services.vkr_evaluation_wrapper import check_structure, run_evaluation
from src.services.vkr_intro_checker import VKRIntroductionChecker
from src.services.vkr_literature_check import LiteratureChecker
from src.services.vkr_report import VKRReport

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
    sign_verify: MarkupPages = di.get(MarkupPages)
    header_classifier: HeaderClassifier = di.get(HeaderClassifier)
    intro_checker = di.get(VKRIntroductionChecker)
    conclusion_checker = di.get(VKRConclusionChecker)
    application_checker = di.get(ApplicationChecker)
    literature_checker = di.get(LiteratureChecker)
    annotation_checker = di.get(VKRAnnotationChecker)

    doc = db.get(Document, doc_id)
    if doc is None:
        print(f"[DEBUG] Doc {doc_id} not found")
        return

    doc.status = DocumentStatus.IN_PROCESSING
    db.commit()
    print(f"[DEBUG] Start processing doc: {doc_id}")

    try:
        bucket_name, object_name = doc.file_url.split("/", 1)
        obj_stat = minio.client.stat_object(bucket_name, object_name)
        doc_service.set_context(obj_stat.content_type)
        file_response = minio.client.get_object(bucket_name, object_name)
        file_buffer = io.BytesIO(file_response.read())
        print("[DEBUG] File loaded from Minio")

        raw_chunks = doc_service.get_structured_text(file_buffer)

        async def run_async_tasks():
            results = await asyncio.gather(
                task_parser.get_task_points(file_buffer),
                info_parser.get_fio(file_buffer),
                info_parser.get_theme(file_buffer),
                header_classifier.classify_headers(raw_chunks),
                sign_verify.markup_pdf(file_buffer),
            )

            status, pages_indexes = results[4]

            return (
                results[0],
                results[1],
                results[2],
                results[3],
                status,
                pages_indexes,
            )

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        (
            task_points,
            fio_list,
            theme,
            classified_chunks,
            status,
            pages_indexes,
        ) = loop.run_until_complete(run_async_tasks())

        signs_verification = {"signs_status_code": status}

        print(f"[DEBUG] Signs verification status code: {status}")
        print("[DEBUG] Model's answer: ", pages_indexes)

        vector_db = rag_engine.create_vector_db(classified_chunks)
        print(f"[DEBUG] Vector DB created. Chunks: {len(raw_chunks)}")
        eval_structure = check_structure(classified_chunks)
        print(f"[DEBUG] Structure check done: {eval_structure}")

        async def run_analysis():
            static_tasks = [
                run_evaluation(
                    "application",
                    eval_structure,
                    application_checker.evaluate,
                    chunks=classified_chunks,
                ),
                run_evaluation(
                    "literature",
                    eval_structure,
                    literature_checker.evaluate,
                    chunks=classified_chunks,
                ),
                run_evaluation(
                    "introduction",
                    eval_structure,
                    intro_checker.evaluate,
                    vector_db=vector_db,
                    total_doc_volume=len(raw_chunks),
                ),
                run_evaluation(
                    "conclusion",
                    eval_structure,
                    conclusion_checker.evaluate,
                    vector_db=vector_db,
                    task_points=task_points,
                    is_collective=len(fio_list) > 1,
                ),
                run_evaluation(
                    "annotation",
                    eval_structure,
                    annotation_checker.evaluate,
                    chunks=classified_chunks,
                ),
            ]

            point_tasks = [vkr_analyzer.evaluate_point(point, vector_db) for point in task_points]

            results = await asyncio.gather(*static_tasks, *point_tasks)

            evaluations = results[:5]

            point_results = results[5:]

            task_evaluations = []
            for point, result in zip(task_points, point_results):
                if isinstance(result, (tuple, list)) and len(result) == 2:
                    score, reason = result
                else:
                    score, reason = 0, f"Unexpected return format: {result}"

                task_evaluations.append(
                    {
                        "task_point": point,
                        "score": score,
                        "justification": reason,
                    }
                )

            print("[DEBUG] Task evaluation done")
            return evaluations, task_evaluations

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        evaluations, task_evaluations = loop.run_until_complete(run_analysis())

        info_data = {"students": fio_list, "theme": theme}
        report_dict: Dict[str, Any] = vkr_report.generate_report(
            info_data, task_evaluations, signs_verification, evaluations
        )
        print("[DEBUG] Report generated")

        # Сохранение результатов
        for student in fio_list:
            parts = student.split()
            group_parts = student.split("-")
            author = Author(
                last_name=parts[0] if len(parts) > 0 else "Unknown",
                first_name=parts[1] if len(parts) > 1 else "",
                middle_name=parts[2] if len(parts) > 2 else None,
                group=group_parts[-1] if len(parts) > 1 else None,
            )
            db.add(author)
            doc.authors.append(author)

        doc.score = report_dict["summary"].get("average_score", 0)
        doc.topic = theme if isinstance(theme, str) else (theme[0] if theme else "")

        if doc.score < 6:
            doc.status = DocumentStatus.REJECTED
        else:
            doc.status = DocumentStatus.APPROVED

        doc.result = report_dict
        db.commit()
        print(f"[DEBUG] Success: {doc_id} processed")

    except Exception as e:
        print(f"[ERROR] Doc {doc_id} failed: {e}")
        db.rollback()
        doc.status = DocumentStatus.FAILED
        db.commit()
