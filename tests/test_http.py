"""
Unit tests for helpers/http.py
"""
import pytest
import requests
from unittest.mock import Mock, MagicMock, patch, call
from helpers.http import MakeRequest
from helpers.utils import FileMetadata, FileProcessStatus


class TestMakeRequest:
    """Test MakeRequest class."""
    
    @patch('helpers.http.AWSSecretManager')
    @patch('helpers.http.AppConfig')
    @patch('helpers.http.APIConfig')
    @patch('helpers.http.AWSConfig')
    def test_init(self, mock_aws_config, mock_api_config, mock_app_config, mock_secret_manager):
        """Test MakeRequest initialization."""
        make_request = MakeRequest()
        
        assert make_request.app_conf is not None
        assert make_request.api_conf is not None
        assert make_request.aws_secret_manager is not None
    
    @patch('helpers.http.requests.post')
    @patch('helpers.http.st.session_state', {"chat_session_id": "test-session-id"})
    def test_stream_chat_completions_success(self, mock_post):
        """Test stream_chat_completions with successful response."""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_post.return_value.__enter__.return_value = mock_response
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.chat_agent_completions_endpoint = "/chat/completions"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            # Mock history
            mock_history = Mock()
            mock_history.messages = []
            
            # Test
            chunks = list(make_request.stream_chat_completions(
                agent_name="test_agent",
                chat_model="test_model",
                history=mock_history,
                prompt="test prompt",
                attachments=[]
            ))
            
            assert len(chunks) == 3
            assert chunks[0] == "chunk1"
            assert chunks[1] == "chunk2"
            assert chunks[2] == "chunk3"
    
    @patch('helpers.http.requests.post')
    @patch('helpers.http.st.session_state', {"chat_session_id": "test-session-id"})
    def test_stream_chat_completions_with_image_attachment(self, mock_post):
        """Test stream_chat_completions with image attachment."""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [b"response"]
        mock_post.return_value.__enter__.return_value = mock_response
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.chat_agent_completions_endpoint = "/chat/completions"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            # Mock history
            mock_history = Mock()
            mock_history.messages = []
            
            # Create image attachment
            attachment = FileMetadata(
                name="test.png",
                type="image/png",
                size=1024,
                bytes=b"image_data",
                base64="base64_encoded_image",
                status=FileProcessStatus.COMPLETED
            )
            
            # Test
            chunks = list(make_request.stream_chat_completions(
                agent_name="test_agent",
                chat_model="test_model",
                history=mock_history,
                prompt="test prompt",
                attachments=[attachment]
            ))
            
            # Verify the request was made with correct payload
            call_args = mock_post.call_args
            assert call_args is not None
            payload = call_args[1]['json']
            assert 'messages' in payload
            # Check that image attachment is included
            messages = payload['messages']
            assert len(messages) > 0
    
    @patch('helpers.http.requests.post')
    @patch('helpers.http.st.session_state', {"chat_session_id": "test-session-id"})
    def test_stream_chat_completions_error(self, mock_post):
        """Test stream_chat_completions with request error."""
        # Mock response to raise exception
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.chat_agent_completions_endpoint = "/chat/completions"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            # Mock history
            mock_history = Mock()
            mock_history.messages = []
            
            # Test
            chunks = list(make_request.stream_chat_completions(
                agent_name="test_agent",
                chat_model="test_model",
                history=mock_history,
                prompt="test prompt",
                attachments=[]
            ))
            
            assert len(chunks) == 1
            assert "[Error]" in chunks[0]
    
    @patch('helpers.http.requests.get')
    def test_get_success(self, mock_get):
        """Test get method with successful response."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result, status_code = make_request.get("/test/endpoint")
            
            assert result == {"data": "test"}
            assert status_code == 200
            mock_get.assert_called_once()
    
    @patch('helpers.http.requests.get')
    def test_get_with_params(self, mock_get):
        """Test get method with parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result, status_code = make_request.get("/test/endpoint", param="test_param")
            
            assert result == {"data": "test"}
            assert status_code == 200
            # Verify params were passed
            call_args = mock_get.call_args
            assert call_args[1]['params'] == "test_param"
    
    @patch('helpers.http.requests.get')
    def test_get_error(self, mock_get):
        """Test get method with request error."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result = make_request.get("/test/endpoint")
            
            assert result is None
    
    @patch('helpers.http.requests.post')
    def test_post_success(self, mock_post):
        """Test post method with successful response."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result, status_code = make_request.post("/test/endpoint", {"key": "value"})
            
            assert result == {"result": "success"}
            assert status_code == 201
            mock_post.assert_called_once()
    
    @patch('helpers.http.requests.post')
    def test_post_error(self, mock_post):
        """Test post method with request error."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result = make_request.post("/test/endpoint", {"key": "value"})
            
            assert result is None
    
    @patch('helpers.http.requests.put')
    def test_put_success(self, mock_put):
        """Test put method with successful response."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "updated"}
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result, status_code = make_request.put("/test/endpoint", {"key": "value"})
            
            assert result == {"result": "updated"}
            assert status_code == 200
            mock_put.assert_called_once()
    
    @patch('helpers.http.requests.put')
    def test_put_error(self, mock_put):
        """Test put method with request error."""
        mock_put.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result = make_request.put("/test/endpoint", {"key": "value"})
            
            assert result is None
    
    @patch('helpers.http.requests.delete')
    def test_delete_success(self, mock_delete):
        """Test delete method with successful response."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "deleted"}
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result, status_code = make_request.delete("/test/endpoint")
            
            assert result == {"result": "deleted"}
            assert status_code == 200
            mock_delete.assert_called_once()
    
    @patch('helpers.http.requests.delete')
    def test_delete_error(self, mock_delete):
        """Test delete method with request error."""
        mock_delete.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Mock configs
        with patch('helpers.http.MakeRequest.__init__', lambda self: None):
            make_request = MakeRequest()
            make_request.api_conf = Mock()
            make_request.api_conf.api_service = "http://test-api.com"
            make_request.api_conf.api_auth_key_name = "test_auth_key"
            make_request.api_conf.api_timeout_seconds = 300
            make_request.aws_secret_manager = Mock()
            make_request.aws_secret_manager.get_secret.return_value = "test_auth_token"
            
            result = make_request.delete("/test/endpoint")
            
            assert result is None
