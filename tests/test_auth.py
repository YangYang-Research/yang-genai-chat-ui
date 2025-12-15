"""
Unit tests for helpers/auth.py
"""
import pytest
import jwt
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from datetime import datetime, timedelta


class TestJWTFunctions:
    """Test JWT-related functions."""
    
    @patch('helpers.auth.cookie_manager')
    @patch('helpers.auth.aws_secret_manager')
    def test_create_jwt_cookie(self, mock_secret_manager, mock_cookie_manager):
        """Test create_jwt_cookie function."""
        mock_secret_manager.get_secret.return_value = "test_secret_key"
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        helpers.auth.create_jwt_cookie("test_token")
        
        mock_cookie_manager.set.assert_called_once_with(
            cookie='yang-cookie',
            val='test_token',
            path="/",
            key="test_secret_key",
            secure=True,
        )
    
    @patch('helpers.auth.aws_secret_manager')
    def test_verify_jwt_token_valid(self, mock_secret_manager):
        """Test verify_jwt_token with valid token."""
        mock_secret_manager.get_secret.return_value = "test_secret_key"
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        # Create a valid token
        payload = {"username": "testuser", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(payload, 'test_secret_key', algorithm='HS256')
        
        result = helpers.auth.verify_jwt_token(token)
        
        assert result is not None
        assert result["username"] == "testuser"
    
    @patch('helpers.auth.aws_secret_manager')
    def test_verify_jwt_token_expired(self, mock_secret_manager):
        """Test verify_jwt_token with expired token."""
        mock_secret_manager.get_secret.return_value = "test_secret_key"
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        # Create an expired token
        payload = {"username": "testuser", "exp": datetime.utcnow() - timedelta(hours=1)}
        token = jwt.encode(payload, 'test_secret_key', algorithm='HS256')
        
        result = helpers.auth.verify_jwt_token(token)
        
        assert result is None
    
    @patch('helpers.auth.aws_secret_manager')
    def test_verify_jwt_token_invalid(self, mock_secret_manager):
        """Test verify_jwt_token with invalid token."""
        mock_secret_manager.get_secret.return_value = "test_secret_key"
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        result = helpers.auth.verify_jwt_token("invalid_token")
        
        assert result is None
    
    @patch('helpers.auth.cookie_manager')
    def test_clear_cookie(self, mock_cookie_manager):
        """Test clear_cookie function."""
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        helpers.auth.clear_cookie()
        
        mock_cookie_manager.delete.assert_called_once_with('yang-cookie')


class TestLoginFunctions:
    """Test login-related functions."""
    
    @patch('helpers.auth.st')
    @patch('helpers.auth.clear_cookie')
    def test_get_logout(self, mock_clear_cookie, mock_st):
        """Test get_logout function."""
        mock_st.session_state = {}
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        result = helpers.auth.get_logout()
        
        assert result is True
        assert mock_st.session_state["authentication_status"] is None
        mock_clear_cookie.assert_called_once()
    
    @patch('helpers.auth.cookie_manager')
    @patch('helpers.auth.verify_jwt_token')
    @patch('helpers.auth.st')
    def test_check_user_login_with_valid_cookie(self, mock_st, mock_verify, mock_cookie_manager):
        """Test check_user_login with valid cookie."""
        mock_st.session_state = {}
        mock_cookie_manager.get_all.return_value = {'yang-cookie': 'valid_token'}
        mock_verify.return_value = {"username": "testuser"}
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        result = helpers.auth.check_user_login("test-key")
        
        assert result is True
        assert mock_st.session_state["authentication_status"] is True
        mock_verify.assert_called_once_with('valid_token')
    
    @patch('helpers.auth.cookie_manager')
    @patch('helpers.auth.verify_jwt_token')
    @patch('helpers.auth.st')
    def test_check_user_login_without_cookie(self, mock_st, mock_verify, mock_cookie_manager):
        """Test check_user_login without cookie."""
        mock_st.session_state = {}
        mock_cookie_manager.get_all.return_value = {}
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        result = helpers.auth.check_user_login("test-key")
        
        assert result is False
        assert mock_st.session_state["authentication_status"] is False
        mock_verify.assert_not_called()
    
    @patch('helpers.auth.cookie_manager')
    @patch('helpers.auth.verify_jwt_token')
    @patch('helpers.auth.st')
    def test_check_user_login_with_invalid_token(self, mock_st, mock_verify, mock_cookie_manager):
        """Test check_user_login with invalid token."""
        mock_st.session_state = {}
        mock_cookie_manager.get_all.return_value = {'yang-cookie': 'invalid_token'}
        mock_verify.return_value = None
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        result = helpers.auth.check_user_login("test-key")
        
        assert result is False
        assert mock_st.session_state["authentication_status"] is False
        mock_verify.assert_called_once_with('invalid_token')
    
    @patch('helpers.auth.cookie_manager')
    @patch('helpers.auth.verify_jwt_token')
    @patch('helpers.auth.create_jwt_cookie')
    @patch('helpers.auth.st')
    def test_get_user_info_with_valid_cookie(self, mock_st, mock_create_cookie, mock_verify, mock_cookie_manager):
        """Test get_user_info with valid cookie."""
        mock_st.session_state = {}
        mock_cookie_manager.get_all.return_value = {'yang-cookie': 'valid_token'}
        mock_verify.return_value = {"username": "testuser"}
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        result = helpers.auth.get_user_info("test-key")
        
        assert result == {"username": "testuser"}
        mock_verify.assert_called_once_with('valid_token')
        mock_create_cookie.assert_not_called()
    
    @patch('helpers.auth.cookie_manager')
    @patch('helpers.auth.verify_jwt_token')
    @patch('helpers.auth.create_jwt_cookie')
    @patch('helpers.auth.st')
    def test_get_user_info_without_cookie(self, mock_st, mock_create_cookie, mock_verify, mock_cookie_manager):
        """Test get_user_info without cookie."""
        mock_st.session_state = {}
        mock_st.rerun = Mock()
        mock_cookie_manager.get_all.return_value = {}
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        # This should trigger rerun
        try:
            result = helpers.auth.get_user_info("test-key")
        except:
            pass  # rerun might raise an exception in test
        
        mock_st.rerun.assert_called_once()
    
    @patch('helpers.auth.cookie_manager')
    @patch('helpers.auth.verify_jwt_token')
    @patch('helpers.auth.create_jwt_cookie')
    @patch('helpers.auth.st')
    def test_get_user_info_with_invalid_token_fallback(self, mock_st, mock_create_cookie, mock_verify, mock_cookie_manager):
        """Test get_user_info with invalid token falls back to session."""
        mock_st.session_state = {"userinfo": {"username": "session_user"}}
        mock_cookie_manager.get_all.return_value = {'yang-cookie': 'invalid_token'}
        mock_verify.return_value = None
        
        # Import after patching
        import importlib
        import helpers.auth
        importlib.reload(helpers.auth)
        
        result = helpers.auth.get_user_info("test-key")
        
        assert result == {"username": "session_user"}
        mock_create_cookie.assert_called_once_with({"username": "session_user"})
