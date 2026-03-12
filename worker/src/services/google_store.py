import mimetypes
import os
from io import BytesIO
from pathlib import Path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from pypdf import PdfReader, PdfWriter, Transformation
from PIL import Image
import segno

from src.core.config import Settings


class GooglePdfStorage:
    """
    auth: создает инстанс для доступа к Google Drive api
    upload_pdf: загружает pdf в папку в Google Drive и получает публичную ссылку
    """

    def __init__(self, config: Settings):
        self.scopes = [scope.strip() for scope in config.SCOPES.split(",") if scope.strip()]
        self.service_account_file = self._resolve_service_account_path(config.SERVICE_ACCOUT_FILE)
        self.parent_folder_id = config.PARENT_FOLDER_ID
        self.oauth_client_file = self._resolve_service_account_path(config.OAUTH_CLIENT_FILE)
        self.token_file = self._resolve_service_account_path("token.json")

    def _resolve_service_account_path(self, raw_path: str) -> str:
        path = Path(raw_path)
        if path.is_file():
            return str(path)

        local_to_service_dir = Path(__file__).resolve().parent / raw_path
        if local_to_service_dir.is_file():
            return str(local_to_service_dir)

        return raw_path

    def auth(self):
        creds = None

        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, scopes=self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.oauth_client_file, self.scopes)
                creds = flow.run_local_server(port=0)

            with open(self.token_file, "w") as token:
                token.write(creds.to_json())

        return creds

    def _get_parent_folder_meta(self, service):
        return (
            service.files()
            .get(
                fileId=self.parent_folder_id,
                fields="id, name, mimeType, driveId",
                supportsAllDrives=True,
            )
            .execute()
        )

    def upload_pdf(self, pdf_bytes: BytesIO):
        """
        Загружает пдф по пути на гугл драйв и делает его публичным
        """
        # basename = os.path.basename(pdf_path)
        mime = "application/pdf"
        # guessed_mime, _ = mimetypes.guess_type(pdf_path)
        # mime = guessed_mime or mime
        creds = self.auth()
        service = build("drive", "v3", credentials=creds)

        file_metadata = {"name": f"vkr_report_{datetime.now().strftime("%Y-%m-%d")}", "parents": [self.parent_folder_id], "mimeType": mime}

        media = MediaFileUpload(pdf_bytes, mimetype=mime, resumable=True)

        created = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )

        file_permission = {"role": "reader", "type": "anyone"}

        service.permissions().create(
            body=file_permission,
            fileId=created.get("id"),
            supportsAllDrives=True,
        ).execute()
        web_link = created.get("webViewLink")

        print("File ID: {}".format(created.get("id")))
        print("webViewLink: {}".format(web_link))

        return web_link
    
    def generate_qr_code(self, data: str, pdf_bytes: BytesIO) -> BytesIO:
        """
        Генерит QR-code и вставляет его в pdf
        """
        qr = segno.make_qr(data)
        qr_png_buffer = BytesIO()
        qr.save(qr_png_buffer, kind="png", scale=10)
        qr_png_buffer.seek(0)

        qr_img = Image.open(qr_png_buffer).convert("RGB")
        qr_pdf_buffer = BytesIO()
        qr_img.save(qr_pdf_buffer, format="PDF")
        qr_pdf_buffer.seek(0)

        reader = PdfReader(pdf_bytes)
        writer = PdfWriter()

        first_page = reader.pages[0]
        qr_page = PdfReader(qr_pdf_buffer).pages[0]

        qr_size = 140
        qr_page.scale_to(qr_size, qr_size)
        first_page.merge_transformed_page(
            qr_page,
            Transformation().translate(tx=10, ty=10),
            over=True,
        )

        for page in reader.pages:
            writer.add_page(page)

        output_stream = BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        return output_stream
