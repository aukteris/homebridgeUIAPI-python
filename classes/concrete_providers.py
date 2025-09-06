import os
import json
import random
import string
from typing import Dict, Any, Optional, List

from .auth_providers import AuthProvider, StorageProvider, UserSessionProvider
from . import hbApi


class HomebridgeAuthProvider(AuthProvider):
    """Concrete implementation for Homebridge UI API authentication."""
    
    def __init__(self, host: str, port: int = 8581, secure: bool = False):
        self.host = host
        self.port = port
        self.secure = secure
        self.hb_api = None
        self._current_token = None
        
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with Homebridge UI API.
        
        Args:
            credentials: Dict with 'username' and 'password' keys
            
        Returns:
            Authentication result dictionary
        """
        try:
            self.hb_api = hbApi.hbApi(self.host, self.port, self.secure)
            self.hb_api.authorize(credentials['username'], credentials['password'])
            
            if self.hb_api.authorization and self.hb_api.authorization['status_code'] == 201:
                # Store secure preference in the authorization data
                self.hb_api.authorization['secure'] = self.secure
                self._current_token = self.hb_api.authorization
                return self.hb_api.authorization
            else:
                raise Exception('Authorization failure')
                
        except Exception as e:
            return {
                'status_code': 401,
                'error': str(e),
                'body': {'error': 'Authentication failed', 'message': str(e)}
            }
    
    def get_token(self) -> Optional[Dict[str, Any]]:
        """Get the current authentication token."""
        return self._current_token
    
    def is_valid(self) -> bool:
        """Check if the current token is valid by making an auth check request."""
        if not self.hb_api or not self._current_token:
            return False
            
        try:
            auth_check = self.hb_api.apiRequest("/api/auth/check", "get")
            return auth_check['status_code'] == 200
        except:
            return False
    
    def refresh_token(self) -> bool:
        """
        Homebridge UI API doesn't support token refresh, 
        would need to re-authenticate with credentials.
        """
        return False
    
    def set_token(self, token_data: Dict[str, Any]) -> None:
        """Set the current token (used when loading from storage)."""
        self._current_token = token_data
        if not self.hb_api:
            self.hb_api = hbApi.hbApi(
                token_data.get('host', self.host),
                token_data.get('port', self.port),
                token_data.get('secure', self.secure)
            )
        self.hb_api.authorization = token_data


class FileStorageProvider(StorageProvider):
    """File-based storage provider for session data."""
    
    def __init__(self, base_dir: str = '.sessionStore'):
        self.base_dir = base_dir
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Ensure the storage directory exists."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def _get_session_file_path(self, session_id: str) -> str:
        """Get the file path for a session."""
        return os.path.join(self.base_dir, f"{session_id}.json")
    
    def save_session(self, session_id: str, auth_data: Dict[str, Any]) -> bool:
        """Save session data to a JSON file."""
        try:
            file_path = self._get_session_file_path(session_id)
            with open(file_path, 'w') as f:
                json.dump(auth_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from a JSON file."""
        try:
            file_path = self._get_session_file_path(session_id)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data file."""
        try:
            file_path = self._get_session_file_path(session_id)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def list_sessions(self) -> List[str]:
        """List all session IDs (filenames without .json extension)."""
        try:
            if not os.path.exists(self.base_dir):
                return []
            
            sessions = []
            for filename in os.listdir(self.base_dir):
                if filename.endswith('.json'):
                    sessions.append(filename[:-5])  # Remove .json extension
            return sessions
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session file exists."""
        file_path = self._get_session_file_path(session_id)
        return os.path.exists(file_path)


class FileUserSessionProvider(UserSessionProvider):
    """File-based provider for user-to-session mappings."""
    
    def __init__(self, base_dir: str = '.authStore'):
        self.base_dir = base_dir
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Ensure the storage directory exists."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def _get_user_file_path(self, username: str, host: str) -> str:
        """Get the file path for a user@host mapping."""
        return os.path.join(self.base_dir, f"{username}@{host}")
    
    def get_session_id(self, username: str, host: str) -> Optional[str]:
        """Get the session ID for a user@host combination."""
        try:
            file_path = self._get_user_file_path(username, host)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return f.read().strip()
            return None
        except Exception as e:
            print(f"Error getting session ID for {username}@{host}: {e}")
            return None
    
    def set_session_id(self, username: str, host: str, session_id: str) -> bool:
        """Set the session ID for a user@host combination."""
        try:
            file_path = self._get_user_file_path(username, host)
            with open(file_path, 'w') as f:
                f.write(session_id)
            return True
        except Exception as e:
            print(f"Error setting session ID for {username}@{host}: {e}")
            return False
    
    def remove_user_session(self, username: str, host: str) -> bool:
        """Remove the session mapping for a user@host combination."""
        try:
            file_path = self._get_user_file_path(username, host)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error removing session for {username}@{host}: {e}")
            return False


class MemoryStorageProvider(StorageProvider):
    """In-memory storage provider for session data (useful for testing)."""
    
    def __init__(self):
        self._sessions = {}
    
    def save_session(self, session_id: str, auth_data: Dict[str, Any]) -> bool:
        """Save session data in memory."""
        self._sessions[session_id] = auth_data.copy()
        return True
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from memory."""
        return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data from memory."""
        if session_id in self._sessions:
            del self._sessions[session_id]
        return True
    
    def list_sessions(self) -> List[str]:
        """List all session IDs in memory."""
        return list(self._sessions.keys())
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists in memory."""
        return session_id in self._sessions


class MemoryUserSessionProvider(UserSessionProvider):
    """In-memory provider for user-to-session mappings."""
    
    def __init__(self):
        self._user_sessions = {}
    
    def _get_user_key(self, username: str, host: str) -> str:
        """Get the key for a user@host combination."""
        return f"{username}@{host}"
    
    def get_session_id(self, username: str, host: str) -> Optional[str]:
        """Get the session ID for a user@host combination."""
        key = self._get_user_key(username, host)
        return self._user_sessions.get(key)
    
    def set_session_id(self, username: str, host: str, session_id: str) -> bool:
        """Set the session ID for a user@host combination."""
        key = self._get_user_key(username, host)
        self._user_sessions[key] = session_id
        return True
    
    def remove_user_session(self, username: str, host: str) -> bool:
        """Remove the session mapping for a user@host combination."""
        key = self._get_user_key(username, host)
        if key in self._user_sessions:
            del self._user_sessions[key]
        return True


def generate_session_id() -> str:
    """Generate a random session ID."""
    characters = string.digits + "-" + string.ascii_lowercase
    return ''.join(random.choice(characters) for i in range(20))
