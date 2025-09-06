"""
Unit tests for the auth and storage providers.
"""

import unittest
import tempfile
import shutil
import os
import json
from unittest.mock import Mock, patch

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.concrete_providers import (
    HomebridgeAuthProvider,
    FileStorageProvider,
    FileUserSessionProvider,
    MemoryStorageProvider,
    MemoryUserSessionProvider,
    generate_session_id
)


class TestHomebridgeAuthProvider(unittest.TestCase):
    """Test the Homebridge authentication provider."""
    
    def setUp(self):
        self.auth_provider = HomebridgeAuthProvider("localhost", 8581, False)
    
    def test_init(self):
        """Test provider initialization."""
        self.assertEqual(self.auth_provider.host, "localhost")
        self.assertEqual(self.auth_provider.port, 8581)
        self.assertEqual(self.auth_provider.secure, False)
        self.assertIsNone(self.auth_provider.hb_api)
        self.assertIsNone(self.auth_provider._current_token)
    
    def test_get_token_when_none(self):
        """Test getting token when none is set."""
        self.assertIsNone(self.auth_provider.get_token())
    
    def test_is_valid_when_no_token(self):
        """Test token validation when no token is set."""
        self.assertFalse(self.auth_provider.is_valid())
    
    def test_refresh_token(self):
        """Test token refresh (should return False for Homebridge)."""
        self.assertFalse(self.auth_provider.refresh_token())
    
    def test_set_token(self):
        """Test setting a token."""
        token_data = {
            'access_token': 'test_token',
            'status_code': 201,
            'host': 'localhost',
            'port': 8581,
            'secure': False
        }
        
        self.auth_provider.set_token(token_data)
        self.assertEqual(self.auth_provider.get_token(), token_data)


class TestFileStorageProvider(unittest.TestCase):
    """Test the file-based storage provider."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage_provider = FileStorageProvider(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_init_creates_directory(self):
        """Test that initialization creates the storage directory."""
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_save_and_load_session(self):
        """Test saving and loading session data."""
        session_id = "test_session_123"
        auth_data = {
            'access_token': 'test_token',
            'status_code': 201,
            'host': 'localhost'
        }
        
        # Save session
        result = self.storage_provider.save_session(session_id, auth_data)
        self.assertTrue(result)
        
        # Load session
        loaded_data = self.storage_provider.load_session(session_id)
        self.assertEqual(loaded_data, auth_data)
    
    def test_session_exists(self):
        """Test checking if a session exists."""
        session_id = "test_session_456"
        auth_data = {'test': 'data'}
        
        # Should not exist initially
        self.assertFalse(self.storage_provider.session_exists(session_id))
        
        # Save and check again
        self.storage_provider.save_session(session_id, auth_data)
        self.assertTrue(self.storage_provider.session_exists(session_id))
    
    def test_delete_session(self):
        """Test deleting session data."""
        session_id = "test_session_789"
        auth_data = {'test': 'data'}
        
        # Save session
        self.storage_provider.save_session(session_id, auth_data)
        self.assertTrue(self.storage_provider.session_exists(session_id))
        
        # Delete session
        result = self.storage_provider.delete_session(session_id)
        self.assertTrue(result)
        self.assertFalse(self.storage_provider.session_exists(session_id))
    
    def test_list_sessions(self):
        """Test listing all sessions."""
        session_ids = ["session_1", "session_2", "session_3"]
        auth_data = {'test': 'data'}
        
        # Save multiple sessions
        for session_id in session_ids:
            self.storage_provider.save_session(session_id, auth_data)
        
        # List sessions
        listed_sessions = self.storage_provider.list_sessions()
        self.assertEqual(set(listed_sessions), set(session_ids))
    
    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist."""
        result = self.storage_provider.load_session("nonexistent_session")
        self.assertIsNone(result)


class TestFileUserSessionProvider(unittest.TestCase):
    """Test the file-based user session provider."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.user_provider = FileUserSessionProvider(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_init_creates_directory(self):
        """Test that initialization creates the storage directory."""
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_set_and_get_session_id(self):
        """Test setting and getting session ID for a user."""
        username = "testuser"
        host = "localhost"
        session_id = "test_session_123"
        
        # Set session ID
        result = self.user_provider.set_session_id(username, host, session_id)
        self.assertTrue(result)
        
        # Get session ID
        retrieved_id = self.user_provider.get_session_id(username, host)
        self.assertEqual(retrieved_id, session_id)
    
    def test_get_nonexistent_session_id(self):
        """Test getting session ID for a user that doesn't exist."""
        result = self.user_provider.get_session_id("nonexistent", "localhost")
        self.assertIsNone(result)
    
    def test_remove_user_session(self):
        """Test removing a user session mapping."""
        username = "testuser"
        host = "localhost"
        session_id = "test_session_456"
        
        # Set session ID
        self.user_provider.set_session_id(username, host, session_id)
        self.assertEqual(self.user_provider.get_session_id(username, host), session_id)
        
        # Remove session
        result = self.user_provider.remove_user_session(username, host)
        self.assertTrue(result)
        self.assertIsNone(self.user_provider.get_session_id(username, host))


class TestMemoryStorageProvider(unittest.TestCase):
    """Test the in-memory storage provider."""
    
    def setUp(self):
        self.storage_provider = MemoryStorageProvider()
    
    def test_save_and_load_session(self):
        """Test saving and loading session data in memory."""
        session_id = "memory_session_123"
        auth_data = {
            'access_token': 'test_token',
            'status_code': 201,
            'host': 'localhost'
        }
        
        # Save session
        result = self.storage_provider.save_session(session_id, auth_data)
        self.assertTrue(result)
        
        # Load session
        loaded_data = self.storage_provider.load_session(session_id)
        self.assertEqual(loaded_data, auth_data)
    
    def test_session_exists(self):
        """Test checking if a session exists in memory."""
        session_id = "memory_session_456"
        auth_data = {'test': 'data'}
        
        # Should not exist initially
        self.assertFalse(self.storage_provider.session_exists(session_id))
        
        # Save and check again
        self.storage_provider.save_session(session_id, auth_data)
        self.assertTrue(self.storage_provider.session_exists(session_id))
    
    def test_delete_session(self):
        """Test deleting session data from memory."""
        session_id = "memory_session_789"
        auth_data = {'test': 'data'}
        
        # Save session
        self.storage_provider.save_session(session_id, auth_data)
        self.assertTrue(self.storage_provider.session_exists(session_id))
        
        # Delete session
        result = self.storage_provider.delete_session(session_id)
        self.assertTrue(result)
        self.assertFalse(self.storage_provider.session_exists(session_id))
    
    def test_list_sessions(self):
        """Test listing all sessions in memory."""
        session_ids = ["mem_session_1", "mem_session_2", "mem_session_3"]
        auth_data = {'test': 'data'}
        
        # Save multiple sessions
        for session_id in session_ids:
            self.storage_provider.save_session(session_id, auth_data)
        
        # List sessions
        listed_sessions = self.storage_provider.list_sessions()
        self.assertEqual(set(listed_sessions), set(session_ids))
    
    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist in memory."""
        result = self.storage_provider.load_session("nonexistent_session")
        self.assertIsNone(result)


class TestMemoryUserSessionProvider(unittest.TestCase):
    """Test the in-memory user session provider."""
    
    def setUp(self):
        self.user_provider = MemoryUserSessionProvider()
    
    def test_set_and_get_session_id(self):
        """Test setting and getting session ID for a user in memory."""
        username = "testuser"
        host = "localhost"
        session_id = "memory_session_123"
        
        # Set session ID
        result = self.user_provider.set_session_id(username, host, session_id)
        self.assertTrue(result)
        
        # Get session ID
        retrieved_id = self.user_provider.get_session_id(username, host)
        self.assertEqual(retrieved_id, session_id)
    
    def test_get_nonexistent_session_id(self):
        """Test getting session ID for a user that doesn't exist in memory."""
        result = self.user_provider.get_session_id("nonexistent", "localhost")
        self.assertIsNone(result)
    
    def test_remove_user_session(self):
        """Test removing a user session mapping from memory."""
        username = "testuser"
        host = "localhost"
        session_id = "memory_session_456"
        
        # Set session ID
        self.user_provider.set_session_id(username, host, session_id)
        self.assertEqual(self.user_provider.get_session_id(username, host), session_id)
        
        # Remove session
        result = self.user_provider.remove_user_session(username, host)
        self.assertTrue(result)
        self.assertIsNone(self.user_provider.get_session_id(username, host))


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_generate_session_id(self):
        """Test session ID generation."""
        session_id = generate_session_id()
        
        # Should be 20 characters long
        self.assertEqual(len(session_id), 20)
        
        # Should only contain allowed characters
        allowed_chars = set("0123456789-abcdefghijklmnopqrstuvwxyz")
        session_chars = set(session_id)
        self.assertTrue(session_chars.issubset(allowed_chars))
        
        # Should generate unique IDs
        session_id_2 = generate_session_id()
        self.assertNotEqual(session_id, session_id_2)


if __name__ == '__main__':
    unittest.main()
