from dishka import Provider, Scope, provide

from src.services.info_parser import InfoParser
from src.services.llm_service import LLMService
from src.services.pdf_processor import PDFProcessor
from src.services.rag import RAGEngine
from src.services.task_parser import TaskParser
from src.services.vkr_analyzer import VKRAnalyzer
from src.services.vkr_report import VKRReport
from src.services.pages_markup import MarkupPages


class ServicesProvider(Provider):
    info_parser = provide(InfoParser, scope=Scope.APP)
    llm_service = provide(LLMService, scope=Scope.APP)
    pdf_processor = provide(PDFProcessor, scope=Scope.APP)
    rag = provide(RAGEngine, scope=Scope.APP)
    task_parser = provide(TaskParser, scope=Scope.APP)
    vkr_analyzer = provide(VKRAnalyzer, scope=Scope.APP)
    vkr_report = provide(VKRReport, scope=Scope.APP)
    sign_detection = provide(MarkupPages, scope=Scope.APP)
