from dishka import Provider, Scope, provide

from src.modules.report.service import ReportService


class ReportProvider(Provider):
    report_service = provide(ReportService, scope=Scope.REQUEST)
