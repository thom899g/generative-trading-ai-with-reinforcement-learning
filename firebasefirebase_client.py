"""
Firebase Client Module
Manages all Firebase interactions with robust error handling and connection pooling
"""
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from google.cloud.firestore_v1.base_query import FieldFilter
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class FirebaseClient:
    """Singleton Firebase client with connection management"""
    
    _instance: Optional['FirebaseClient'] = None
    _initialized: bool = False
    _db: Optional[firestore.Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_manager):
        if not self._initialized:
            self.config = config_manager.get_config()
            self._initialize_firebase()
            self._initialized = True
            self._executor = ThreadPoolExecutor(max_workers=10)
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase with error handling and retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(
                        str(self.config.firebase_credentials_path)
                    )
                    firebase_admin.initialize_app(cred, {
                        'projectId': self.config.firebase_project_id,
                    })
                
                self._db