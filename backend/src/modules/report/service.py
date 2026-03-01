from datetime import datetime
from io import BytesIO
from uuid import UUID

import openpyxl
import openpyxl.styles
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from minio import S3Error
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.enums.document_status import DocumentStatus
from src.common.schemas.token_user_info import TokenUserInfo
from src.infra.minio.service import MinioService
from src.modules.documents.repositories import DocumentRepository


class ReportService:
    def __init__(
        self,
        db: AsyncSession,
        doc_repo: DocumentRepository,
        minio: MinioService,
    ):
        self.db = db
        self.doc_repo = doc_repo
        self.minio = minio

    async def get_for_all(
        self,
        user: TokenUserInfo,
        start: datetime,
        end: datetime,
    ):
        STATUSES_MAP = {
            DocumentStatus.APPROVED: "Зачёт",
            DocumentStatus.REJECTED: "Незачёт",
        }

        headers = ["ФИО студента", "Группа", "Тема работы", "Статус", "Оценка"]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Отчёт"

        header_font = openpyxl.styles.Font(bold=True, color="FFFFFF")
        header_fill = openpyxl.styles.PatternFill("solid", fgColor="155dfc")
        header_alignment = openpyxl.styles.Alignment(
            horizontal="center", vertical="center"
        )

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

        docs = await self.doc_repo.get_all_processed(
            user_id=user.id, from_date=start, to_date=end
        )
        row_idx = 2
        for doc in docs:
            for student in doc.authors:
                ws.cell(
                    row=row_idx,
                    column=1,
                    value=f"{student.last_name} {student.first_name} {student.middle_name or ''}",
                )
                ws.cell(
                    row=row_idx,
                    column=2,
                    value=(student.group or "Группа не распознана"),
                )
                ws.cell(row=row_idx, column=3, value=doc.topic)
                ws.cell(
                    row=row_idx,
                    column=4,
                    value=STATUSES_MAP.get(doc.status, "Ошибка"),
                )
                ws.cell(row=row_idx, column=5, value=doc.score)

                # выравнивание
                for col_idx in range(1, 6):
                    ws.cell(
                        row=row_idx, column=col_idx
                    ).alignment = openpyxl.styles.Alignment(
                        horizontal="left", vertical="top", wrap_text=True
                    )

                row_idx += 1

        column_widths = [30, 15, 40, 15, 10]
        for i, width in enumerate(column_widths, start=1):
            ws.column_dimensions[
                openpyxl.utils.get_column_letter(i)
            ].width = width

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="report.xlsx"'
            },
        )

    async def get_for_doc(
        self,
        user: TokenUserInfo,
        doc_id: UUID,
    ) -> StreamingResponse:
        try:
            document = await self.doc_repo.get_by_id(id=doc_id)

            if document is None or str(document.user_id) != user.id:
                raise HTTPException(404, "Document not found")

            if document.report_url is None:
                raise HTTPException(400, "Document is not processed")

            bucket_name = document.report_url.split("/")[0]
            object_name = document.report_url[len(bucket_name) + 1 :]

            response = self.minio.client.get_object(
                bucket_name=bucket_name, object_name=object_name
            )

            headers = {}
            if hasattr(response, "headers"):
                content_type = response.headers.get("content-type")
                if content_type:
                    headers["Content-Type"] = content_type

            return StreamingResponse(
                response.stream(amt=1024 * 1024),
                media_type=headers.get(
                    "Content-Type", "application/octet-stream"
                ),
                headers={
                    "Content-Disposition": f'attachment; filename="{document.original_name}"'
                },
            )
        except S3Error:
            raise HTTPException(404, "File not found")
