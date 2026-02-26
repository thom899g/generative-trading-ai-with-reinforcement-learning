"""
Configuration Management Module
Centralized configuration with validation and environment-specific settings
"""
import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field, validator
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TradingConfig(BaseSettings):
    """Validated configuration schema for trading system"""
    
    # Firebase Configuration
    firebase_project_id: str = Field(..., env="FIREBASE_PROJECT_ID")
    firebase_credentials_path: Path = Field(..., env="FIREBASE_CREDENTIALS_PATH")
    
    # Exchange Configuration
    exchange_api_key: str = Field(..., env="EXCHANGE_API_KEY")
    exchange_api_secret: str = Field(..., env="EXCHANGE_API_SECRET")
    exchange_name: str = "binance"
    trading_pair: str = "BTC/USDT"
    
    # Risk Parameters
    max_position_size: float = Field(0.1, env="MAX_POSITION_SIZE")
    max_daily_loss: float = Field(0.05, env="MAX_DAILY_LOSS")
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    
    # RL Parameters
    rl_learning_rate: float = 0.001
    rl_discount_factor: float = 0.99
    rl_epsilon_start: float = 1.0
    rl_epsilon_end: float = 0.01
    rl_epsilon_decay: float = 0.995
    
    # Generative AI Parameters
    strategy_generation_interval: int = 3600  # seconds
    max_strategies_in_memory: int = 100
    
    # Telegram Alerts
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(None, env="TELEGRAM_CHAT_ID")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @validator("firebase_credentials_path")
    def validate_firebase_credentials(cls, v: Path) -> Path:
        """Ensure Firebase credentials file exists"""
        if not v.exists():
            logger.error(f"Firebase credentials file not found: {v}")
            raise FileNotFoundError(f"Firebase credentials file not found: {v}")
        return v
    
    @validator("max_position_size", "max_daily_loss", "stop_loss_pct", "take_profit_pct")
    def validate_risk_parameters(cls, v: float) -> float:
        """Validate risk parameters are within safe bounds"""
        if not 0 < v < 1:
            raise ValueError(f"Risk parameter {v} must be between 0 and 1")
        return v


class ConfigManager:
    """Singleton configuration manager with hot-reloading capability"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[TradingConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize configuration with validation"""
        try:
            self._config = TradingConfig()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def get_config(self) -> TradingConfig:
        """Get current configuration instance"""
        if self._config is None:
            self._initialize()
        return self._config
    
    def reload_config(self) -> None:
        """Reload configuration from environment"""
        logger.info("Reloading configuration from environment")
        self._config = TradingConfig()


# Global configuration accessor
config_manager = ConfigManager()