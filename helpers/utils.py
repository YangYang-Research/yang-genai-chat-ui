import re
import uuid
import base64
from enum import Enum
from typing import Optional
from helpers.loog import logger
from dataclasses import dataclass
from helpers.config import FileConfig

class FileProcessStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class FileMetadata:
    name: str
    type: str
    size: int
    bytes: bytes
    base64: Optional[str] = None
    content: Optional[str] = None
    status: FileProcessStatus = FileProcessStatus.PENDING
    error: Optional[str] = None

    @property
    def size_kb(self) -> float:
        """Return size in kilobytes."""
        return self.size / 1024
    
    @property
    def is_image(self) -> bool:
        """Check if the file is an image based on its MIME type."""
        return self.type.startswith("image/")
    
    @property
    def is_document(self) -> bool:
        """Check if the file is a document based on its MIME type."""
        document_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]
        return self.type in document_types
    
    @property
    def is_text(self) -> bool:
        """Check if the file is a text file based on its MIME type."""
        return self.type.startswith("text/")

class Utils:
    def __init__(self):
        self.file_conf = FileConfig()
    
    def process_multiple_files(self, files) -> list[FileMetadata]:
        """Process multiple uploaded files and return their metadata."""
        processed_files = []
        for file in files:
            processed_file = self.process_single_file(file)
            processed_files.append(processed_file)
        return processed_files
    
    def process_single_file(self, file) -> FileMetadata:
        """Process a single uploaded file and return its metadata."""
        try:
            file_content = file.read()
            if len(file_content) > self.file_conf.max_upload_size_mb * 1024 * 1024:
                return FileMetadata(
                    name=file.name,
                    type=file.type,
                    size=len(file_content),
                    bytes=b'',
                    base64=None,
                    status=FileProcessStatus.FAILED,
                    error="File size exceeds the maximum limit."
                )
            
            attachment = FileMetadata(
                name=file.name,
                type=file.type,
                size=len(file_content),
                bytes=file_content,
                status=FileProcessStatus.PROCESSING,
                error=None
            )
            
            if self.is_allow_image_file(file):
                attachment.base64 = base64.b64encode(file_content).decode('utf-8')
            elif self.is_allow_document_file(file):
                attachment.base64 = base64.b64encode(file_content).decode('utf-8')
            elif self.is_allow_text_file(file):
                attachment.content = file_content.decode('utf-8')
            else:
                return FileMetadata(
                    name=file.name,
                    type=file.type,
                    size=len(file_content),
                    bytes=b'',
                    status=FileProcessStatus.FAILED,
                    error="Unsupported file type."
                )
            
            attachment.status = FileProcessStatus.COMPLETED
            
            return attachment
        
        except Exception as e:
            logger.error(f"[FE-FILE_PROCESSING] Error processing file : {e}")
            return FileMetadata(
                name=file.name,
                type=file.type,
                size=0,
                content=b'',
                base64=None,
                status=FileProcessStatus.FAILED,
                error=str(e)
            )
        
    def is_allow_image_file(self, file) -> bool:
        return (file.type in ["image/png", "image/jpg", "image/jpeg"] and file.name.split('.')[-1].lower() in self.file_conf.allowed_file_types)
    
    def is_allow_document_file(self, file) -> bool:
        return (file.type in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ] and file.name.split('.')[-1].lower() in self.file_conf.allowed_file_types)
    
    def is_allow_text_file(self, file) -> bool:
        return (file.type.startswith("text/") and file.name.split('.')[-1].lower() in self.file_conf.allowed_file_types)
    
    def get_file_format(value: str) -> str:
        """
        Map between file extensions and MIME types, both directions.
        - Input a filename or extension (e.g., "file.pdf" or "pdf") → returns MIME type
        - Input a MIME type (e.g., "application/pdf") → returns short format ("pdf")
        """

        value = value.strip().lower()

        mime_map = {
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xls": "application/vnd.ms-excel",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "csv": "text/csv",
            "pdf": "application/pdf",
            "txt": "text/plain",
            "md": "text/markdown",
            "html": "text/html",
            "htm": "text/html",
        }

        # 🔁 Reverse map for quick lookup
        ext_map = {v: k for k, v in mime_map.items()}

        # Case 1: If it's a MIME type, return short format
        if value in ext_map:
            return ext_map[value]

        # Case 2: If it's a filename or extension, return MIME type
        if "." in value:
            value = value.split(".")[-1]  # handle "file.pdf" case

        return mime_map.get(value, "application/octet-stream")
    
    def format_filename(filename: str) -> str:
        """
        Sanitize and format a document file name.
        Allowed:
        - Alphanumeric (A–Z, a–z, 0–9)
        - Whitespace
        - Hyphens (-)
        - Parentheses ((, ))
        - Square brackets ([, ])
        Rules:
        - Remove disallowed characters
        - Collapse multiple spaces into one
        - Trim leading/trailing spaces
        """
        # Step 1: Remove disallowed characters
        sanitized = re.sub(r"[^A-Za-z0-9\-\[\]\(\)\s]", "", filename)

        # Step 2: Replace multiple spaces with a single space
        sanitized = re.sub(r"\s{2,}", " ", sanitized)

        # Step 3: Trim whitespace at start/end
        sanitized = sanitized.strip()

        return sanitized
    
    def generate_session_uuid(self) -> str:
        """Generate a unique identifier string."""
        return str(uuid.uuid4())