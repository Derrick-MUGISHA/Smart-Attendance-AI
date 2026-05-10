import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class FileManagerService:
    def __init__(self, base_dir: str = settings.UPLOAD_DIR):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_today_dir(self) -> Path:
        today = datetime.now().strftime("%Y-%m-%d")
        path = self.base_dir / today
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _calculate_hash(self, file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def save_upload(self, content: bytes, original_filename: str, sender_id: int) -> Dict:
        today_dir = self._get_today_dir()
        timestamp = datetime.now().strftime("%H-%M-%S")
        extension = Path(original_filename).suffix
        new_filename = f"attendance_{timestamp}{extension}"
        file_path = today_dir / new_filename

        # Handle name collisions (though unlikely with timestamp-seconds)
        counter = 1
        while file_path.exists():
            new_filename = f"attendance_{timestamp}_{counter}{extension}"
            file_path = today_dir / new_filename
            counter += 1

        with open(file_path, "wb") as f:
            f.write(content)

        file_hash = self._calculate_hash(file_path)

        metadata = {
            "original_filename": original_filename,
            "filename": new_filename,
            "path": str(file_path),
            "size": len(content),
            "sender_id": sender_id,
            "upload_time": datetime.now().isoformat(),
            "hash": file_hash,
            "status": "stored"
        }

        logger.info(f"File saved: {file_path}")
        return metadata

    def rename_file(self, current_path: str, new_name: str) -> str:
        old_path = Path(current_path)
        if not old_path.exists():
            raise FileNotFoundError(f"File not found: {current_path}")
        
        # Ensure an extension is preserved if not provided in new_name
        if not Path(new_name).suffix and old_path.suffix:
            new_name += old_path.suffix
            
        new_path = old_path.parent / new_name
        old_path.rename(new_path)
        return str(new_path)

    def delete_file(self, file_path: str, secure: bool = True) -> bool:
        path = Path(file_path)
        if path.exists():
            if secure:
                # In a production app, we might move to a 'trash' folder instead of unlinking
                trash_dir = self.base_dir / "trash"
                trash_dir.mkdir(exist_ok=True)
                shutil.move(str(path), str(trash_dir / path.name))
            else:
                path.unlink()
            return True
        return False

    def list_files(self, date_str: Optional[str] = None) -> List[Path]:
        target_dir = self.base_dir / date_str if date_str else self.base_dir
        if not target_dir.exists():
            return []
        return [p for p in target_dir.glob("**/*") if p.is_file()]

    def check_duplicate(self, file_hash: str) -> Optional[str]:
        # This would ideally check against a DB, but for now, we scan files if needed
        # or rely on the DB model unique constraint on hash
        pass

file_manager = FileManagerService()