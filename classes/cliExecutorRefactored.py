import json
from typing import Dict, Any, Optional

from .auth_providers import AuthProvider, StorageProvider, UserSessionProvider
from .concrete_providers import (
    HomebridgeAuthProvider, 
    FileStorageProvider, 
    FileUserSessionProvider,
    generate_session_id
)
from . import hbApi


class cliExecutor:
    """
    Refactored CLI executor with dependency injection for auth and storage providers.
    
    This version abstracts authentication and storage logic, making it easier to use
    in different projects with different storage requirements.
    """
    
    def __init__(self, 
                 auth_provider: Optional[AuthProvider] = None,
                 storage_provider: Optional[StorageProvider] = None,
                 user_session_provider: Optional[UserSessionProvider] = None):
        """
        Initialize the CLI executor with pluggable providers.
        
        Args:
            auth_provider: Provider for authentication logic
            storage_provider: Provider for session storage
            user_session_provider: Provider for user-to-session mappings
        """
        # Use default file-based providers if none specified (backward compatibility)
        self.storage_provider = storage_provider or FileStorageProvider()
        self.user_session_provider = user_session_provider or FileUserSessionProvider()
        
        # Auth provider will be created per-request since it needs host/port info
        self._auth_provider = auth_provider
        self.hb = None
    
    def processArgs(self, args):
        """Entry point from the main class which calls the actions."""
        actionMethod = getattr(self, args.action, lambda: "Invalid Action")
        actionMethod(args)
    
    def authorize(self, args):
        """Process authorization request and maintain sessions per user/host."""
        try:
            # Parse configuration
            if args.configFile is None:
                config = {
                    'host': args.host,
                    'port': args.port,
                    'username': args.username,
                    'password': args.password,
                    'secure': args.secure
                }
            else:
                with open(args.configFile, "r") as f:
                    config = json.loads(f.read())
            
            # Validate required fields
            if config.get('host') is None:
                raise Exception("Host required for Authorization request")
            
            if config.get('username') is None:
                raise Exception("Username required for Authorization request")
            
            if config.get('password') is None:
                raise Exception("Password required for Authorization request")
            
            # Set defaults
            port = config.get('port', 8581)
            secure = config.get('secure', False)
            
            # Create or use provided auth provider
            if self._auth_provider is None:
                auth_provider = HomebridgeAuthProvider(config['host'], port, secure)
            else:
                auth_provider = self._auth_provider
            
            # Check if we have an existing session for this user@host
            existing_session_id = self.user_session_provider.get_session_id(
                config['username'], config['host']
            )
            
            session_id = existing_session_id
            auth_data = None
            
            # Try to load existing session
            if session_id and self.storage_provider.session_exists(session_id):
                auth_data = self.storage_provider.load_session(session_id)
                if auth_data:
                    auth_provider.set_token(auth_data)
                    
                    # Check if the existing token is still valid
                    if auth_provider.is_valid():
                        result = {'sessionId': session_id}
                        print(json.dumps(result))
                        return result
            
            # Generate new session ID if needed
            if not session_id:
                session_id = generate_session_id()
            
            # Perform authentication
            credentials = {
                'username': config['username'],
                'password': config['password']
            }
            
            auth_result = auth_provider.authenticate(credentials)
            
            if auth_result.get('status_code') != 201:
                raise Exception('Authorization failure')
            
            # Save the session
            if not self.storage_provider.save_session(session_id, auth_result):
                raise Exception('Failed to save session')
            
            # Update user-to-session mapping
            if not self.user_session_provider.set_session_id(
                config['username'], config['host'], session_id
            ):
                raise Exception('Failed to save user session mapping')
            
            result = {'sessionId': session_id}
            print(json.dumps(result))
            return result
            
        except Exception as inst:
            print(inst)
        except:
            print("Unknown error processing authorization")
    
    def request(self, args):
        """Process a direct API request."""
        try:
            if not self.loadSession(args.sessionId):
                raise Exception('Session load failed')
            
            request_body = json.loads(args.requestBody) if args.requestBody else {}
            parameters = json.loads(args.parameters) if args.parameters else {}
            
            request_result = self.hb.apiRequest(
                args.endpoint, 
                args.method, 
                requestBody=request_body, 
                parameters=parameters
            )
            
            if request_result['status_code'] != 200:
                error_msg = f"HTTP Status {request_result['status_code']}"
                if 'body' in request_result and 'error' in request_result['body']:
                    error_msg += f" {request_result['body']['error']}: {request_result['body']['message']}"
                raise Exception(error_msg)
            
            print(json.dumps(request_result))
            
        except Exception as inst:
            print(inst)
    
    def setaccessorychar(self, args):
        """Set the characteristics of an accessory."""
        try:
            # Create the characteristic data
            formatted_char_val = int(args.charSet[1]) if args.charSet[1].isnumeric() else args.charSet[1]
            
            char_data = {
                'characteristicType': args.charSet[0],
                'value': formatted_char_val
            }
            
            if not self.loadSession(args.sessionId):
                raise Exception('Session load failed')
            
            find_accessories = self.hb.findAccessoriesByName(args.name)
            
            if find_accessories is not None:
                for accessory in find_accessories:
                    for characteristic in accessory['serviceCharacteristics']:
                        if characteristic['type'] == args.charSet[0]:
                            parameters = {'uniqueId': accessory['uniqueId']}
                            
                            set_result = self.hb.apiRequest(
                                '/api/accessories/{uniqueId}', 
                                'put', 
                                requestBody=char_data, 
                                parameters=parameters
                            )
                            
                            if set_result['status_code'] != 200:
                                error_msg = f"HTTP Status {set_result['status_code']}"
                                if 'body' in set_result and 'error' in set_result['body']:
                                    error_msg += f" {set_result['body']['error']}: {set_result['body']['message']}"
                                print(error_msg)
                            else:
                                print(json.dumps(set_result))
                                return set_result
                            break
                    else:
                        continue
                    break
            else:
                raise Exception("No accessories found")
                
        except Exception as inst:
            print(inst)
    
    def accessorycharvalues(self, args):
        """Get accessory characteristic values."""
        try:
            if not self.loadSession(args.sessionId):
                raise Exception('Session load failed')
            
            find_accessories = self.hb.findAccessoriesByName(args.name)
            results = {}
            
            if find_accessories is not None:
                for accessory in find_accessories:
                    for characteristic in accessory['serviceCharacteristics']:
                        for char_type in args.charSet:
                            if char_type == characteristic['type']:
                                results[characteristic['type']] = characteristic['value']
                
                print(json.dumps(results))
                return results
                
        except Exception as inst:
            print(inst)
    
    def listaccessorychars(self, args):
        """List accessory characteristics."""
        try:
            if not self.loadSession(args.sessionId):
                raise Exception('Session load failed')
            
            find_accessories = self.hb.findAccessoriesByName(args.name)
            results = {}
            
            if find_accessories is not None:
                print("\tCharacteristic\tValue\tRead\tWrite\n")
                for accessory in find_accessories:
                    print(accessory['serviceName'])
                    
                    for characteristic in accessory['serviceCharacteristics']:
                        print(f"\t{characteristic['type']}\t{characteristic['value']}\t{characteristic['canRead']}\t{characteristic['canWrite']}")
                        results[characteristic['type']] = characteristic['value']
                
                return results
            else:
                raise Exception("No accessories found")
                
        except Exception as inst:
            print(inst)
    
    def loadSession(self, session_id: str) -> bool:
        """Load a session from storage and set up the API client."""
        try:
            # Load session data
            session_data = self.storage_provider.load_session(session_id)
            if not session_data:
                print("Session ID not found")
                return False
            
            # Create API client with session data
            self.hb = hbApi.hbApi(
                session_data.get('host'),
                session_data.get('port', 8581),
                session_data.get('secure', False)
            )
            self.hb.authorization = session_data
            
            # Create auth provider and check if token is still valid
            auth_provider = HomebridgeAuthProvider(
                session_data.get('host'),
                session_data.get('port', 8581),
                session_data.get('secure', False)
            )
            auth_provider.set_token(session_data)
            
            if auth_provider.is_valid():
                return True
            else:
                print("Authorization is no longer valid")
                return False
                
        except Exception as e:
            print(f"Error loading session: {e}")
            return False


# Factory functions for easy instantiation
def create_default_executor() -> cliExecutor:
    """Create a cliExecutor with default file-based providers (backward compatible)."""
    return cliExecutor()


def create_memory_executor() -> cliExecutor:
    """Create a cliExecutor with in-memory providers (useful for testing)."""
    from .concrete_providers import MemoryStorageProvider, MemoryUserSessionProvider
    
    return cliExecutor(
        storage_provider=MemoryStorageProvider(),
        user_session_provider=MemoryUserSessionProvider()
    )


def create_custom_executor(auth_provider: AuthProvider = None,
                          storage_provider: StorageProvider = None,
                          user_session_provider: UserSessionProvider = None) -> cliExecutor:
    """Create a cliExecutor with custom providers."""
    return cliExecutor(
        auth_provider=auth_provider,
        storage_provider=storage_provider,
        user_session_provider=user_session_provider
    )
