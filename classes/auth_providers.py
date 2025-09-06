from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class AuthProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform initial authentication with the given credentials.
        
        Args:
            credentials: Dictionary containing auth credentials (username, password, etc.)
            
        Returns:
            Dictionary containing authentication result with status and token data
        """
        pass
    
    @abstractmethod
    def get_token(self) -> Optional[Dict[str, Any]]:
        """
        Get the current authentication token.
        
        Returns:
            Current token data or None if not authenticated
        """
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """
        Check if the current token is valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def refresh_token(self) -> bool:
        """
        Refresh the current token if possible.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        pass


class StorageProvider(ABC):
    """Abstract base class for session storage providers."""
    
    @abstractmethod
    def save_session(self, session_id: str, auth_data: Dict[str, Any]) -> bool:
        """
        Save session data to storage.
        
        Args:
            session_id: Unique identifier for the session
            auth_data: Authentication data to store
            
        Returns:
            True if save was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data from storage.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Session data or None if not found
        """
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session data from storage.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_sessions(self) -> List[str]:
        """
        List all available session IDs.
        
        Returns:
            List of session IDs
        """
        pass
    
    @abstractmethod
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in storage.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if session exists, False otherwise
        """
        pass


class UserSessionProvider(ABC):
    """Abstract base class for managing user-to-session mappings."""
    
    @abstractmethod
    def get_session_id(self, username: str, host: str) -> Optional[str]:
        """
        Get the session ID for a specific user and host.
        
        Args:
            username: Username
            host: Host address
            
        Returns:
            Session ID or None if not found
        """
        pass
    
    @abstractmethod
    def set_session_id(self, username: str, host: str, session_id: str) -> bool:
        """
        Set the session ID for a specific user and host.
        
        Args:
            username: Username
            host: Host address
            session_id: Session ID to associate
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def remove_user_session(self, username: str, host: str) -> bool:
        """
        Remove the session mapping for a specific user and host.
        
        Args:
            username: Username
            host: Host address
            
        Returns:
            True if successful, False otherwise
        """
        pass
