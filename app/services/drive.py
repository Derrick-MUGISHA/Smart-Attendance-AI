from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import os

SCOPES = ['https://www.googleapis.com/auth/drive']

class DriveService:
    def __init__(self, credentials_path: str):
        if not os.path.exists(credentials_path):
            # Fallback for environment variable if a path doesn't exist (useful for production)
            import json
            import base64
            creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            if creds_json:
                info = json.loads(base64.b64decode(creds_json))
                creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
            else:
                raise FileNotFoundError(f"Credentials file not found at {credentials_path}")
        else:
            creds = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )
        self.service = build('drive', 'v3', credentials=creds)

    def get_or_create_folder(self, name: str, parent_id: str = None) -> str:
        """Return folder ID, creating it if it doesn't exist."""
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = self.service.files().list(q=query, fields='files(id)').execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
            
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else []
        }
        folder = self.service.files().create(body=metadata, fields='id').execute()
        return folder['id']

    def upload_file(self, local_path: str, filename: str, folder_id: str,
                    mime_type: str = 'image/jpeg') -> str:
        """Upload the file to the Drive folder, return file ID."""
        metadata = {'name': filename, 'parents': [folder_id]}
        media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
        file = self.service.files().create(
            body=metadata, media_body=media, fields='id'
        ).execute()
        return file['id']

    def upload_bytes(self, content: bytes, filename: str, folder_id: str,
                     mime_type: str = 'application/pdf') -> str:
        """Upload in-memory bytes to Drive, return file ID."""
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as f:
            f.write(content)
            tmp_path = f.name
        try:
            file_id = self.upload_file(tmp_path, filename, folder_id, mime_type)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        return file_id

    def get_shareable_link(self, file_id: str) -> str:
        """Make file readable by anyone with the link and return the URL."""
        self.service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()
        return f"https://drive.google.com/file/d/{file_id}/view"
