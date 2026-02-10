from dishka import Provider, Scope, provide

from src.services.doc_processors import (
    DocumentProcessorService,
    DOCXProcessor,
    PDFProcessor,
)
from src.services.headers_classifier import HeaderClassifier
from src.services.info_parser import InfoParser
from src.services.llm_service import LLMService
from src.services.pages_markup import MarkupPages
from src.services.rag import RAGEngine
from src.services.task_parser import TaskParser
from src.services.vkr_analyzer import VKRAnalyzer
from src.services.vkr_conclusion_checker import VKRConclusionChecker
from src.services.vkr_intro_checker import VKRIntroductionChecker
from src.services.vkr_report import VKRReport


class ServicesProvider(Provider):
    llm_service = provide(LLMService, scope=Scope.APP)
    rag = provide(RAGEngine, scope=Scope.APP)
    vkr_report = provide(VKRReport, scope=Scope.APP)

    pdf_processor = provide(PDFProcessor, scope=Scope.APP)
    docx_processor = provide(DOCXProcessor, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def doc_processor_service(
        self, pdf: PDFProcessor, docx: DOCXProcessor
    ) -> DocumentProcessorService:
        return DocumentProcessorService(pdf, docx)

    task_parser = provide(TaskParser, scope=Scope.APP)
    info_parser = provide(InfoParser, scope=Scope.APP)
    header_classifier = provide(HeaderClassifier, scope=Scope.APP)

    vkr_analyzer = provide(VKRAnalyzer, scope=Scope.APP)
    intro_checker = provide(VKRIntroductionChecker, scope=Scope.APP)
    conclusion_checker = provide(VKRConclusionChecker, scope=Scope.APP)
    sign_detection = provide(MarkupPages, scope=Scope.APP)
