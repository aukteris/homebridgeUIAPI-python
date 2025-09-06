# Homebridge CLI Executor - Refactored Architecture

This document describes the refactored architecture of the Homebridge CLI Executor that abstracts authentication and storage logic for better reusability across different Python projects.

## Overview

The original `cliExecutor` class had tightly coupled authentication and storage logic, making it difficult to reuse in different projects with varying storage requirements. The refactored architecture uses the **Strategy Pattern** to separate concerns and provide pluggable authentication and storage providers.

## Key Benefits

- **Separation of Concerns**: Authentication logic is separated from execution logic
- **Flexibility**: Choose different storage mechanisms (file, memory, database, etc.)
- **Testability**: Easy to mock providers for unit testing
- **Backward Compatibility**: Existing code continues to work unchanged
- **Extensibility**: Easy to add new authentication and storage methods

## Architecture Components

### 1. Abstract Base Classes (`classes/auth_providers.py`)

- **`AuthProvider`**: Defines the contract for authentication
- **`StorageProvider`**: Defines the contract for session storage
- **`UserSessionProvider`**: Defines the contract for user-to-session mappings

### 2. Concrete Implementations (`classes/concrete_providers.py`)

- **`HomebridgeAuthProvider`**: Handles Homebridge UI API authentication
- **`FileStorageProvider`**: File-based session storage
- **`FileUserSessionProvider`**: File-based user session mappings
- **`MemoryStorageProvider`**: In-memory session storage (for testing)
- **`MemoryUserSessionProvider`**: In-memory user session mappings

### 3. Refactored Executor (`classes/cliExecutorRefactored.py`)

- **`cliExecutor`**: Main executor class with dependency injection
- Factory functions for easy instantiation

### 4. Backward Compatibility (`classes/cliHelperBackwardCompatible.py`)

- Drop-in replacement for the original `cliHelper.py`
- Maintains exact same API while using new architecture internally

## Usage Examples

### Basic Usage (Backward Compatible)

```python
from classes.cliHelperBackwardCompatible import cliExecutor

# Works exactly like the original
executor = cliExecutor()
```

### Custom Storage Directories

```python
from classes.cliExecutorRefactored import cliExecutor
from classes.concrete_providers import FileStorageProvider, FileUserSessionProvider

executor = cliExecutor(
    storage_provider=FileStorageProvider("./my_app/sessions"),
    user_session_provider=FileUserSessionProvider("./my_app/users")
)
```

### In-Memory Storage (Testing)

```python
from classes.cliExecutorRefactored import create_memory_executor

executor = create_memory_executor()
```

### Custom Authentication Provider

```python
from classes.auth_providers import AuthProvider
from classes.cliExecutorRefactored import create_custom_executor

class MyCustomAuthProvider(AuthProvider):
    def authenticate(self, credentials):
        # Your custom auth logic
        pass
    
    def get_token(self):
        # Return current token
        pass
    
    def is_valid(self):
        # Check token validity
        pass
    
    def refresh_token(self):
        # Refresh token if needed
        pass

custom_auth = MyCustomAuthProvider()
executor = create_custom_executor(auth_provider=custom_auth)
```

### Configuration-Based Setup

```python
def create_executor_from_config(config):
    if config["storage_type"] == "file":
        return cliExecutor(
            storage_provider=FileStorageProvider(config["session_dir"]),
            user_session_provider=FileUserSessionProvider(config["user_dir"])
        )
    elif config["storage_type"] == "memory":
        return create_memory_executor()
    else:
        return create_default_executor()

config = {
    "storage_type": "file",
    "session_dir": "./app_sessions",
    "user_dir": "./app_users"
}

executor = create_executor_from_config(config)
```

## Migration Guide

### For Existing Projects

1. **No Changes Required**: Replace `from classes.cliHelper import cliExecutor` with `from classes.cliHelperBackwardCompatible import cliExecutor`

2. **Gradual Migration**: Start using the new architecture for new features while keeping existing code unchanged

### For New Projects

1. **Use Refactored Version**: Import from `classes.cliExecutorRefactored`
2. **Choose Appropriate Providers**: Select storage providers that fit your project needs
3. **Leverage Factory Functions**: Use `create_default_executor()`, `create_memory_executor()`, etc.

## File Structure

```
classes/
├── auth_providers.py              # Abstract base classes
├── concrete_providers.py          # Concrete implementations
├── cliExecutorRefactored.py       # Refactored executor with DI
├── cliHelperBackwardCompatible.py # Backward compatibility layer
├── cliHelper.py                   # Original implementation (preserved)
└── hbApi.py                       # Homebridge API client

examples/
└── usage_examples.py              # Comprehensive usage examples

tests/
└── test_auth_providers.py         # Unit tests for providers
```

## Provider Interface Reference

### AuthProvider

```python
class AuthProvider(ABC):
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Perform authentication with given credentials"""
        pass
    
    @abstractmethod
    def get_token(self) -> Optional[Dict[str, Any]]:
        """Get current authentication token"""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Check if current token is valid"""
        pass
    
    @abstractmethod
    def refresh_token(self) -> bool:
        """Refresh the current token"""
        pass
```

### StorageProvider

```python
class StorageProvider(ABC):
    @abstractmethod
    def save_session(self, session_id: str, auth_data: Dict[str, Any]) -> bool:
        """Save session data"""
        pass
    
    @abstractmethod
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data"""
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        pass
    
    @abstractmethod
    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        pass
    
    @abstractmethod
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        pass
```

### UserSessionProvider

```python
class UserSessionProvider(ABC):
    @abstractmethod
    def get_session_id(self, username: str, host: str) -> Optional[str]:
        """Get session ID for user@host"""
        pass
    
    @abstractmethod
    def set_session_id(self, username: str, host: str, session_id: str) -> bool:
        """Set session ID for user@host"""
        pass
    
    @abstractmethod
    def remove_user_session(self, username: str, host: str) -> bool:
        """Remove session mapping for user@host"""
        pass
```

## Testing

Run the test suite to verify everything works correctly:

```bash
python -m pytest tests/test_auth_providers.py -v
```

Or run individual test files:

```bash
python tests/test_auth_providers.py
```

## Examples

See `examples/usage_examples.py` for comprehensive examples of different usage patterns:

```bash
python examples/usage_examples.py
```

## Advanced Use Cases

### Database Storage Provider

```python
from classes.auth_providers import StorageProvider

class DatabaseStorageProvider(StorageProvider):
    def __init__(self, connection_string):
        # Initialize database connection
        pass
    
    def save_session(self, session_id, auth_data):
        # Save to database
        pass
    
    # Implement other methods...
```

### Redis Storage Provider

```python
import redis
from classes.auth_providers import StorageProvider

class RedisStorageProvider(StorageProvider):
    def __init__(self, redis_url):
        self.redis_client = redis.from_url(redis_url)
    
    def save_session(self, session_id, auth_data):
        self.redis_client.setex(
            f"session:{session_id}", 
            3600,  # 1 hour TTL
            json.dumps(auth_data)
        )
        return True
    
    # Implement other methods...
```

### Environment-Based Configuration

```python
import os
from classes.cliExecutorRefactored import cliExecutor
from classes.concrete_providers import FileStorageProvider, MemoryStorageProvider

def create_executor():
    if os.getenv('ENVIRONMENT') == 'test':
        return create_memory_executor()
    else:
        session_dir = os.getenv('SESSION_DIR', '.sessionStore')
        user_dir = os.getenv('USER_DIR', '.authStore')
        return cliExecutor(
            storage_provider=FileStorageProvider(session_dir),
            user_session_provider=FileUserSessionProvider(user_dir)
        )
```

## Contributing

When adding new providers:

1. Inherit from the appropriate abstract base class
2. Implement all required methods
3. Add comprehensive unit tests
4. Update documentation with usage examples
5. Consider backward compatibility implications

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and paths are correct
2. **Permission Errors**: Check file system permissions for storage directories
3. **Session Not Found**: Verify session IDs and storage provider configuration

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Potential areas for future development:

- **Encryption**: Add encryption support for stored session data
- **Session Expiration**: Implement automatic session cleanup
- **Metrics**: Add monitoring and metrics collection
- **Async Support**: Add async/await support for I/O operations
- **Configuration Validation**: Add schema validation for configuration
