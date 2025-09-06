"""
Backward compatibility layer for the original cliHelper.py

This file provides a drop-in replacement for the original cliHelper.py that uses
the new abstracted architecture under the hood while maintaining the same API.
"""

import os
import json
import random
import string

from . import hbApi
from .cliExecutorRefactored import cliExecutor as RefactoredExecutor


class cliExecutor:
    """
    Backward compatible version of cliExecutor.
    
    This class maintains the exact same interface as the original cliExecutor
    but uses the new abstracted architecture internally. Existing code should
    work without any changes.
    """
    
    # Class variables for backward compatibility
    authStoreDir = '.authStore'
    sessionStoreDir = '.sessionStore'
    hb = None

    def __init__(self):
        """Initialize with the same behavior as the original."""
        # Create directories for backward compatibility
        if not os.path.exists(self.authStoreDir):
            os.makedirs(self.authStoreDir)
        
        if not os.path.exists(self.sessionStoreDir):
            os.makedirs(self.sessionStoreDir)
        
        # Create the refactored executor with default file-based providers
        # that use the same directory structure as the original
        from .concrete_providers import FileStorageProvider, FileUserSessionProvider
        
        self._executor = RefactoredExecutor(
            storage_provider=FileStorageProvider(self.sessionStoreDir),
            user_session_provider=FileUserSessionProvider(self.authStoreDir)
        )
    
    def processArgs(self, args):
        """Entry point from the main class which calls the actions."""
        return self._executor.processArgs(args)
    
    def authorize(self, args):
        """Process authorization request and maintain sessions per user/host."""
        result = self._executor.authorize(args)
        # Set the hb attribute for backward compatibility
        self.hb = self._executor.hb
        return result
    
    def request(self, args):
        """Process a direct API request."""
        result = self._executor.request(args)
        # Set the hb attribute for backward compatibility
        self.hb = self._executor.hb
        return result
    
    def setaccessorychar(self, args):
        """Set the characteristics of an accessory."""
        result = self._executor.setaccessorychar(args)
        # Set the hb attribute for backward compatibility
        self.hb = self._executor.hb
        return result
    
    def accessorycharvalues(self, args):
        """Get accessory characteristic values."""
        result = self._executor.accessorycharvalues(args)
        # Set the hb attribute for backward compatibility
        self.hb = self._executor.hb
        return result
    
    def listaccessorychars(self, args):
        """List accessory characteristics."""
        result = self._executor.listaccessorychars(args)
        # Set the hb attribute for backward compatibility
        self.hb = self._executor.hb
        return result
    
    def checkAuth(self):
        """Helper method to confirm the authorization is still valid."""
        if self.hb is None:
            return False
        
        try:
            authCheck = self.hb.apiRequest("/api/auth/check", "get")
            return authCheck['status_code'] == 200
        except:
            return False
    
    def loadSession(self, sessionId):
        """Helper method to load a previous session from a given session ID."""
        result = self._executor.loadSession(sessionId)
        # Set the hb attribute for backward compatibility
        self.hb = self._executor.hb
        return result


# For complete backward compatibility, we can also provide the original class name
# in case someone imports it directly
cliHelper = cliExecutor
