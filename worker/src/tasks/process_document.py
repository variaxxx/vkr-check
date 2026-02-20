import io
import json
import uuid
from typing import Any, Dict, List, Union

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
from src.services.vkr_application_check import ApplicationChecker
from src.services.vkr_conclusion_checker import VKRConclusionChecker
from src.services.vkr_evaluation_wrapper import check_structure, run_evaluation
from src.services.vkr_intro_checker import VKRIntroductionChecker
from src.services.vkr_literature_check import LiteratureChecker
from src.services.vkr_report import VKRReport
from src.services.vkr_annotation_checker import VKRAnnotationChecker

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
        return

    doc.status = DocumentStatus.IN_PROCESSING
    db.commit()

    try:
        bucket_name, object_name = doc.file_url.split("/", 1)
        obj_stat = minio.client.stat_object(bucket_name, object_name)

        doc_service.set_context(obj_stat.content_type)

        file_response = minio.client.get_object(bucket_name, object_name)
        file_buffer = io.BytesIO(file_response.read())

        status: bool = False
        txt: List[str] = []
        if doc_service.is_pdf():
            status, txt = sign_verify.markup_pdf(file_buffer)

        signs_verification = {"signs_status_code": status}

        task_points = task_parser.get_task_points(file_buffer)
        file_buffer.seek(0)

        fio_list = info_parser.get_fio(file_buffer)
        file_buffer.seek(0)

        theme = info_parser.get_theme(file_buffer)
        file_buffer.seek(0)

        raw_chunks = doc_service.get_structured_text(file_buffer)
        classified_chunks = header_classifier.classify_headers(raw_chunks)
        vector_db = rag_engine.create_vector_db(classified_chunks)

        task_points = task_parser.get_task_points(file_buffer)

        # Оценка ЗАДАНИЯ
        task_evaluations = []
        for point in task_points:
            score, reason = vkr_analyzer.evaluate_point(point, vector_db)
            task_evaluations.append(
                {"task_point": point, "score": score, "justification": reason}
            )

        # Проверка структуры
        eval_structure = check_structure(classified_chunks)

        # Оценка ПРИЛОЖЕНИЯ
        application_evaluations = run_evaluation(
            'application',
            eval_structure,
            application_checker.evaluate,
            vector_db=vector_db
        )

        # Оценка СПИСКА ЛИТЕРАТУРЫ
        literature_evaluations = run_evaluation(
            'literature',
            eval_structure,
            literature_checker.evaluate,
            vector_db=vector_db,
            raw_chunks=raw_chunks
        )

        # Оценка ВВЕДЕНИЯ
        intro_evaluations = run_evaluation(
            'introduction',
            eval_structure,
            intro_checker.evaluate,
            vector_db=vector_db,
            total_doc_volume=len(raw_chunks)
        )

        # Оценка ЗАКЛЮЧЕНИЯ
        conclusion_evaluations = run_evaluation(
            'conclusion',
            eval_structure,
            conclusion_checker.evaluate,
            vector_db=vector_db,
            task_points=task_points,
            is_collective=len(fio_list) > 1
        )

        #Оценка АННОТАЦИЙ
        annotation_evaluations = run_evaluation(
            'annotation',
            eval_structure,
            annotation_checker.evaluate,
            vector_db=vector_db
        )

        # ОТЧЕТ
        evaluations = [
            application_evaluations,
            literature_evaluations,
            intro_evaluations,
            conclusion_evaluations,
            annotation_evaluations
        ]

        info_data = {"students": fio_list, "theme": theme}
        report_dict: Dict[str, Any] = vkr_report.generate_report(
            info_data, task_evaluations, signs_verification, evaluations
        )

        report_json_tmp = json.dumps(report_dict, ensure_ascii=True)
        report_json = json.loads(report_json_tmp)

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
        doc.topic = (
            theme if isinstance(theme, str) else (theme[0] if theme else "")
        )
        doc.status = DocumentStatus.SUCCESS
        doc.result = report_json
        db.commit()

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        doc.status = DocumentStatus.FAILED
        db.commit()
