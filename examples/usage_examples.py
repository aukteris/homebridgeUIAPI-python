"""
Usage examples for the refactored cliExecutor with abstracted auth and storage providers.

These examples demonstrate how to use the cliExecutor in different scenarios
and with different storage backends.
"""

import sys
import os
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import the classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.cliExecutorRefactored import (
    cliExecutor, 
    create_default_executor, 
    create_memory_executor, 
    create_custom_executor
)
from classes.concrete_providers import (
    HomebridgeAuthProvider,
    FileStorageProvider,
    FileUserSessionProvider,
    MemoryStorageProvider,
    MemoryUserSessionProvider
)


def example_1_backward_compatible():
    """
    Example 1: Backward compatible usage (same as original)
    
    This creates a cliExecutor that works exactly like the original,
    using file-based storage in .authStore and .sessionStore directories.
    """
    print("=== Example 1: Backward Compatible Usage ===")
    
    # Create executor with default file-based providers
    executor = create_default_executor()
    
    # Or equivalently:
    # executor = cliExecutor()
    
    print("Created executor with default file-based storage")
    print("Auth store directory: .authStore")
    print("Session store directory: .sessionStore")
    print()


def example_2_custom_directories():
    """
    Example 2: Custom storage directories
    
    Use file-based storage but in custom directories for better organization
    in your project.
    """
    print("=== Example 2: Custom Storage Directories ===")
    
    # Create executor with custom storage directories
    executor = cliExecutor(
        storage_provider=FileStorageProvider(base_dir="./my_app/sessions"),
        user_session_provider=FileUserSessionProvider(base_dir="./my_app/users")
    )
    
    print("Created executor with custom directories:")
    print("Sessions: ./my_app/sessions")
    print("User mappings: ./my_app/users")
    print()


def example_3_memory_storage():
    """
    Example 3: In-memory storage for testing
    
    Use in-memory storage for unit tests or temporary sessions
    that don't need persistence.
    """
    print("=== Example 3: In-Memory Storage for Testing ===")
    
    # Create executor with in-memory providers
    executor = create_memory_executor()
    
    # Or equivalently:
    # executor = cliExecutor(
    #     storage_provider=MemoryStorageProvider(),
    #     user_session_provider=MemoryUserSessionProvider()
    # )
    
    print("Created executor with in-memory storage")
    print("Perfect for unit tests and temporary sessions")
    print()


def example_4_mixed_providers():
    """
    Example 4: Mixed providers
    
    Use different providers for different aspects - for example,
    file-based user sessions but memory-based session storage.
    """
    print("=== Example 4: Mixed Providers ===")
    
    executor = cliExecutor(
        storage_provider=MemoryStorageProvider(),  # Sessions in memory
        user_session_provider=FileUserSessionProvider(base_dir="./persistent_users")  # Users on disk
    )
    
    print("Created executor with mixed providers:")
    print("Sessions: In-memory (temporary)")
    print("User mappings: File-based (persistent)")
    print()


def example_5_programmatic_usage():
    """
    Example 5: Programmatic usage without command line args
    
    Shows how to use the executor programmatically in your own applications.
    """
    print("=== Example 5: Programmatic Usage ===")
    
    # Create executor
    executor = create_memory_executor()  # Using memory for this example
    
    # Create a mock args object for authorization
    class MockArgs:
        def __init__(self):
            self.action = "authorize"
            self.configFile = None
            self.host = "192.168.1.100"
            self.port = 8581
            self.username = "admin"
            self.password = "admin"
            self.secure = False
    
    # Note: This is just showing the structure - you'd need a real Homebridge instance
    print("Example of programmatic usage:")
    print("1. Create executor with desired providers")
    print("2. Create configuration object")
    print("3. Call executor methods directly")
    print("4. Handle results in your application logic")
    print()


def example_6_custom_auth_provider():
    """
    Example 6: Custom authentication provider
    
    Shows how you could implement a custom auth provider for a different API
    or authentication mechanism.
    """
    print("=== Example 6: Custom Authentication Provider ===")
    
    from classes.auth_providers import AuthProvider
    
    class CustomAuthProvider(AuthProvider):
        """Example custom auth provider for a different API."""
        
        def __init__(self, api_endpoint: str):
            self.api_endpoint = api_endpoint
            self._token = None
        
        def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
            # Your custom authentication logic here
            print(f"Authenticating with {self.api_endpoint}")
            # Return mock success for example
            self._token = {"access_token": "mock_token", "status_code": 201}
            return self._token
        
        def get_token(self):
            return self._token
        
        def is_valid(self) -> bool:
            # Your token validation logic
            return self._token is not None
        
        def refresh_token(self) -> bool:
            # Your token refresh logic
            return False
    
    # Use custom auth provider
    custom_auth = CustomAuthProvider("https://my-api.example.com")
    executor = create_custom_executor(auth_provider=custom_auth)
    
    print("Created executor with custom authentication provider")
    print("This allows integration with different APIs and auth mechanisms")
    print()


def example_7_database_storage():
    """
    Example 7: Database storage provider (conceptual)
    
    Shows how you could implement a database-backed storage provider.
    """
    print("=== Example 7: Database Storage Provider (Conceptual) ===")
    
    from classes.auth_providers import StorageProvider
    
    class DatabaseStorageProvider(StorageProvider):
        """Example database storage provider."""
        
        def __init__(self, connection_string: str):
            self.connection_string = connection_string
            # Initialize database connection here
            print(f"Would connect to database: {connection_string}")
        
        def save_session(self, session_id: str, auth_data: Dict[str, Any]) -> bool:
            # Save to database
            print(f"Would save session {session_id} to database")
            return True
        
        def load_session(self, session_id: str):
            # Load from database
            print(f"Would load session {session_id} from database")
            return None
        
        def delete_session(self, session_id: str) -> bool:
            # Delete from database
            print(f"Would delete session {session_id} from database")
            return True
        
        def list_sessions(self):
            # List from database
            return []
        
        def session_exists(self, session_id: str) -> bool:
            # Check database
            return False
    
    # Use database storage
    db_storage = DatabaseStorageProvider("postgresql://user:pass@localhost/mydb")
    executor = create_custom_executor(storage_provider=db_storage)
    
    print("Created executor with database storage provider")
    print("This enables enterprise-grade session management")
    print()


def example_8_configuration_based():
    """
    Example 8: Configuration-based setup
    
    Shows how to configure the executor based on configuration files
    or environment variables.
    """
    print("=== Example 8: Configuration-Based Setup ===")
    
    # Example configuration
    config = {
        "storage_type": "file",
        "storage_config": {
            "session_dir": "./app_sessions",
            "user_dir": "./app_users"
        }
    }
    
    def create_executor_from_config(config: Dict[str, Any]) -> cliExecutor:
        """Factory function to create executor from configuration."""
        
        if config["storage_type"] == "file":
            storage_config = config["storage_config"]
            return cliExecutor(
                storage_provider=FileStorageProvider(storage_config["session_dir"]),
                user_session_provider=FileUserSessionProvider(storage_config["user_dir"])
            )
        elif config["storage_type"] == "memory":
            return create_memory_executor()
        else:
            return create_default_executor()
    
    executor = create_executor_from_config(config)
    
    print("Created executor from configuration:")
    print(f"Storage type: {config['storage_type']}")
    print(f"Configuration: {config['storage_config']}")
    print()


if __name__ == "__main__":
    """Run all examples to demonstrate the different usage patterns."""
    
    print("Homebridge CLI Executor - Usage Examples")
    print("=" * 50)
    print()
    
    example_1_backward_compatible()
    example_2_custom_directories()
    example_3_memory_storage()
    example_4_mixed_providers()
    example_5_programmatic_usage()
    example_6_custom_auth_provider()
    example_7_database_storage()
    example_8_configuration_based()
    
    print("All examples completed!")
    print()
    print("Key Benefits of the Refactored Architecture:")
    print("- Separation of concerns between auth and execution logic")
    print("- Pluggable storage backends for different project needs")
    print("- Easy testing with in-memory providers")
    print("- Backward compatibility with existing code")
    print("- Extensible for future authentication mechanisms")
