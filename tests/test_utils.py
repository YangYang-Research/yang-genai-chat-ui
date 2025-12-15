"""
Unit tests for helpers/utils.py
"""
import pytest
import base64
from unittest.mock import Mock, patch, MagicMock
from helpers.utils import Utils, FileMetadata, FileProcessStatus


class TestFileMetadata:
    """Test FileMetadata dataclass."""
    
    def test_file_metadata_creation(self):
        """Test creating FileMetadata instance."""
        metadata = FileMetadata(
            name="test.txt",
            type="text/plain",
            size=1024,
            bytes=b"content"
        )
        assert metadata.name == "test.txt"
        assert metadata.type == "text/plain"
        assert metadata.size == 1024
        assert metadata.bytes == b"content"
        assert metadata.status == FileProcessStatus.PENDING
    
    def test_size_kb_property(self):
        """Test size_kb property calculation."""
        metadata = FileMetadata(
            name="test.txt",
            type="text/plain",
            size=2048,
            bytes=b"content"
        )
        assert metadata.size_kb == 2.0
    
    def test_is_image_property(self):
        """Test is_image property."""
        image_metadata = FileMetadata(
            name="test.png",
            type="image/png",
            size=1024,
            bytes=b"content"
        )
        assert image_metadata.is_image is True
        
        text_metadata = FileMetadata(
            name="test.txt",
            type="text/plain",
            size=1024,
            bytes=b"content"
        )
        assert text_metadata.is_image is False
    
    def test_is_document_property(self):
        """Test is_document property."""
        pdf_metadata = FileMetadata(
            name="test.pdf",
            type="application/pdf",
            size=1024,
            bytes=b"content"
        )
        assert pdf_metadata.is_document is True
        
        docx_metadata = FileMetadata(
            name="test.docx",
            type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size=1024,
            bytes=b"content"
        )
        assert docx_metadata.is_document is True
        
        text_metadata = FileMetadata(
            name="test.txt",
            type="text/plain",
            size=1024,
            bytes=b"content"
        )
        assert text_metadata.is_document is False
    
    def test_is_text_property(self):
        """Test is_text property."""
        text_metadata = FileMetadata(
            name="test.txt",
            type="text/plain",
            size=1024,
            bytes=b"content"
        )
        assert text_metadata.is_text is True
        
        image_metadata = FileMetadata(
            name="test.png",
            type="image/png",
            size=1024,
            bytes=b"content"
        )
        assert image_metadata.is_text is False


class TestUtils:
    """Test Utils class."""
    
    @patch('helpers.utils.FileConfig')
    def test_process_single_file_text(self, mock_file_config, mock_file):
        """Test processing a single text file."""
        mock_file_config.return_value.allowed_file_types = ["txt", "html", "md"]
        mock_file_config.return_value.max_upload_size_mb = 10
        
        utils = Utils()
        result = utils.process_single_file(mock_file)
        
        assert result.name == "test_file.txt"
        assert result.type == "text/plain"
        assert result.status == FileProcessStatus.COMPLETED
        assert result.content == "test content"
        assert result.error is None
    
    @patch('helpers.utils.FileConfig')
    def test_process_single_file_image(self, mock_file_config, mock_image_file):
        """Test processing a single image file."""
        mock_file_config.return_value.allowed_file_types = ["png", "jpg", "jpeg"]
        mock_file_config.return_value.max_upload_size_mb = 10
        
        utils = Utils()
        result = utils.process_single_file(mock_image_file)
        
        assert result.name == "test_image.png"
        assert result.type == "image/png"
        assert result.status == FileProcessStatus.COMPLETED
        assert result.base64 == base64.b64encode(b"fake image content").decode('utf-8')
        assert result.error is None
    
    @patch('helpers.utils.FileConfig')
    def test_process_single_file_document(self, mock_file_config, mock_document_file):
        """Test processing a single document file."""
        mock_file_config.return_value.allowed_file_types = ["pdf", "docx", "doc"]
        mock_file_config.return_value.max_upload_size_mb = 10
        
        utils = Utils()
        result = utils.process_single_file(mock_document_file)
        
        assert result.name == "test_document.pdf"
        assert result.type == "application/pdf"
        assert result.status == FileProcessStatus.COMPLETED
        assert result.base64 == base64.b64encode(b"fake pdf content").decode('utf-8')
        assert result.error is None
    
    @patch('helpers.utils.FileConfig')
    def test_process_single_file_size_exceeded(self, mock_file_config, mock_large_file):
        """Test processing a file that exceeds size limit."""
        mock_file_config.return_value.allowed_file_types = ["pdf"]
        mock_file_config.return_value.max_upload_size_mb = 10
        
        utils = Utils()
        result = utils.process_single_file(mock_large_file)
        
        assert result.status == FileProcessStatus.FAILED
        assert result.error == "File size exceeds the maximum limit."
        assert result.bytes == b''
    
    @patch('helpers.utils.FileConfig')
    def test_process_single_file_unsupported_type(self, mock_file_config):
        """Test processing an unsupported file type."""
        mock_file_config.return_value.allowed_file_types = ["txt", "pdf"]
        mock_file_config.return_value.max_upload_size_mb = 10
        
        file = Mock()
        file.name = "test.exe"
        file.type = "application/x-msdownload"
        file.read.return_value = b"executable content"
        
        utils = Utils()
        result = utils.process_single_file(file)
        
        assert result.status == FileProcessStatus.FAILED
        assert result.error == "Unsupported file type."
    
    @patch('helpers.utils.FileConfig')
    def test_process_single_file_exception(self, mock_file_config):
        """Test processing a file that raises an exception."""
        mock_file_config.return_value.allowed_file_types = ["txt"]
        mock_file_config.return_value.max_upload_size_mb = 10
        
        file = Mock()
        file.name = "test.txt"
        file.type = "text/plain"
        file.read.side_effect = Exception("Read error")
        
        utils = Utils()
        result = utils.process_single_file(file)
        
        assert result.status == FileProcessStatus.FAILED
        assert "Read error" in result.error
    
    @patch('helpers.utils.FileConfig')
    def test_process_multiple_files(self, mock_file_config, mock_file, mock_image_file):
        """Test processing multiple files."""
        mock_file_config.return_value.allowed_file_types = ["txt", "png"]
        mock_file_config.return_value.max_upload_size_mb = 10
        
        utils = Utils()
        files = [mock_file, mock_image_file]
        results = utils.process_multiple_files(files)
        
        assert len(results) == 2
        assert results[0].name == "test_file.txt"
        assert results[1].name == "test_image.png"
        assert all(r.status == FileProcessStatus.COMPLETED for r in results)
    
    @patch('helpers.utils.FileConfig')
    def test_is_allow_image_file(self, mock_file_config):
        """Test is_allow_image_file method."""
        mock_file_config.return_value.allowed_file_types = ["png", "jpg", "jpeg"]
        
        file = Mock()
        file.name = "test.png"
        file.type = "image/png"
        
        utils = Utils()
        assert utils.is_allow_image_file(file) is True
        
        file.name = "test.jpg"
        file.type = "image/jpg"
        assert utils.is_allow_image_file(file) is True
        
        file.name = "test.gif"
        file.type = "image/gif"
        assert utils.is_allow_image_file(file) is False
    
    @patch('helpers.utils.FileConfig')
    def test_is_allow_document_file(self, mock_file_config):
        """Test is_allow_document_file method."""
        mock_file_config.return_value.allowed_file_types = ["pdf", "docx", "doc"]
        
        file = Mock()
        file.name = "test.pdf"
        file.type = "application/pdf"
        
        utils = Utils()
        assert utils.is_allow_document_file(file) is True
        
        file.name = "test.docx"
        file.type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert utils.is_allow_document_file(file) is True
        
        file.name = "test.txt"
        file.type = "text/plain"
        assert utils.is_allow_document_file(file) is False
    
    @patch('helpers.utils.FileConfig')
    def test_is_allow_text_file(self, mock_file_config):
        """Test is_allow_text_file method."""
        mock_file_config.return_value.allowed_file_types = ["txt", "md", "html"]
        
        file = Mock()
        file.name = "test.txt"
        file.type = "text/plain"
        
        utils = Utils()
        assert utils.is_allow_text_file(file) is True
        
        file.name = "test.md"
        file.type = "text/markdown"
        assert utils.is_allow_text_file(file) is True
        
        file.name = "test.pdf"
        file.type = "application/pdf"
        assert utils.is_allow_text_file(file) is False
    
    def test_get_file_format_extension_to_mime(self):
        """Test get_file_format with file extension."""
        assert Utils.get_file_format("pdf") == "application/pdf"
        assert Utils.get_file_format("docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert Utils.get_file_format("txt") == "text/plain"
        assert Utils.get_file_format("csv") == "text/csv"
        assert Utils.get_file_format("unknown") == "application/octet-stream"
    
    def test_get_file_format_filename_to_mime(self):
        """Test get_file_format with filename."""
        assert Utils.get_file_format("document.pdf") == "application/pdf"
        assert Utils.get_file_format("file.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert Utils.get_file_format("test.txt") == "text/plain"
    
    def test_get_file_format_mime_to_extension(self):
        """Test get_file_format with MIME type."""
        assert Utils.get_file_format("application/pdf") == "pdf"
        assert Utils.get_file_format("text/plain") == "txt"
        assert Utils.get_file_format("text/csv") == "csv"
        assert Utils.get_file_format("application/vnd.openxmlformats-officedocument.wordprocessingml.document") == "docx"
    
    def test_format_filename_valid(self):
        """Test format_filename with valid characters."""
        assert Utils.format_filename("test file.pdf") == "test file.pdf"
        assert Utils.format_filename("test-file.pdf") == "test-file.pdf"
        assert Utils.format_filename("test (1).pdf") == "test (1).pdf"
        assert Utils.format_filename("test [1].pdf") == "test [1].pdf"
        assert Utils.format_filename("test123.pdf") == "test123.pdf"
    
    def test_format_filename_remove_invalid(self):
        """Test format_filename removes invalid characters."""
        assert Utils.format_filename("test@file.pdf") == "testfile.pdf"
        assert Utils.format_filename("test#file.pdf") == "testfile.pdf"
        assert Utils.format_filename("test$file.pdf") == "testfile.pdf"
        assert Utils.format_filename("test&file.pdf") == "testfile.pdf"
    
    def test_format_filename_collapse_spaces(self):
        """Test format_filename collapses multiple spaces."""
        assert Utils.format_filename("test    file.pdf") == "test file.pdf"
        assert Utils.format_filename("test  file  name.pdf") == "test file name.pdf"
    
    def test_format_filename_trim_whitespace(self):
        """Test format_filename trims leading/trailing whitespace."""
        assert Utils.format_filename("  test file.pdf  ") == "test file.pdf"
        assert Utils.format_filename(" test file.pdf ") == "test file.pdf"
    
    def test_generate_session_uuid(self):
        """Test generate_session_uuid returns a valid UUID string."""
        utils = Utils()
        uuid_str = utils.generate_session_uuid()
        
        assert isinstance(uuid_str, str)
        assert len(uuid_str) == 36  # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        assert uuid_str.count('-') == 4
