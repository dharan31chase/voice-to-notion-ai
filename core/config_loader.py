#!/usr/bin/env python3
"""
Configuration Loader for AI Assistant
Loads YAML configuration files with environment variable override support
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required fields"""
    pass


class ConfigLoader:
    """
    Centralized configuration management system.
    
    Features:
    - Loads all YAML files from config/ directory
    - Supports dot notation access: config.get("openai.model")
    - Environment variable overrides: OPENAI_MODEL overrides openai.model
    - Validation with sensible defaults
    - Reloadable for development
    
    Priority Order: ENV Variable > YAML > Hardcoded Default
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader
        
        Args:
            config_dir: Path to config directory (default: ./config relative to project root)
        """
        # Determine project root (parent of core/ directory)
        self.project_root = Path(__file__).parent.parent
        
        if config_dir is None:
            self.config_dir = self.project_root / "config"
        else:
            self.config_dir = Path(config_dir)
        
        self._config = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all YAML files from config directory"""
        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")
            return
        
        # Load all .yaml files
        yaml_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
        
        if not yaml_files:
            logger.warning(f"No YAML files found in {self.config_dir}")
            return
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        # Merge into main config
                        self._config.update(data)
                        logger.debug(f"Loaded config from {yaml_file.name}")
            except Exception as e:
                logger.error(f"Error loading {yaml_file.name}: {e}")
                raise ConfigError(f"Failed to load {yaml_file.name}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        Supports environment variable override.
        
        Args:
            key: Dot-notation key (e.g., "openai.model")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Examples:
            config.get("openai.model")
            config.get("openai.max_tokens", 500)
        """
        # Check environment variable first (highest priority)
        env_var = self._key_to_env_var(key)
        env_value = os.getenv(env_var)
        if env_value is not None:
            logger.debug(f"Using environment variable {env_var}={env_value}")
            return self._convert_env_value(env_value)
        
        # Navigate through nested dictionary using dot notation
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_required(self, key: str) -> Any:
        """
        Get required configuration value.
        Raises ConfigError if not found.
        
        Args:
            key: Dot-notation key
            
        Returns:
            Configuration value
            
        Raises:
            ConfigError: If key not found
        """
        value = self.get(key)
        if value is None:
            raise ConfigError(f"Required configuration key missing: {key}")
        return value
    
    def reload(self):
        """Reload all configuration files (useful for development)"""
        self._config = {}
        self._load_all_configs()
        logger.info("Configuration reloaded")
    
    def validate(self, required_keys: Optional[list] = None):
        """
        Validate required configuration keys exist
        
        Args:
            required_keys: List of required keys (dot notation)
            
        Raises:
            ConfigError: If any required key is missing
        """
        if required_keys is None:
            # Default required keys for the system
            required_keys = [
                "openai.model",
                "paths.transcripts",
                "paths.processed"
            ]
        
        missing_keys = []
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)
        
        if missing_keys:
            raise ConfigError(f"Missing required configuration keys: {', '.join(missing_keys)}")
    
    def _key_to_env_var(self, key: str) -> str:
        """
        Convert dot notation key to environment variable name
        
        Examples:
            "openai.model" -> "OPENAI_MODEL"
            "paths.transcripts" -> "PATHS_TRANSCRIPTS"
        """
        return key.upper().replace('.', '_')
    
    def _convert_env_value(self, value: str) -> Any:
        """
        Convert environment variable string to appropriate Python type
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value (bool, int, float, or string)
        """
        # Boolean conversion
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        if value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Default: return as string
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary (for debugging)"""
        return self._config.copy()
    
    def __repr__(self) -> str:
        return f"<ConfigLoader: {len(self._config)} top-level keys from {self.config_dir}>"


# Global singleton instance
_config_instance = None


def get_config(reload: bool = False) -> ConfigLoader:
    """
    Get global configuration instance (singleton pattern)
    
    Args:
        reload: If True, reload configuration
        
    Returns:
        ConfigLoader instance
    """
    global _config_instance
    
    if _config_instance is None or reload:
        _config_instance = ConfigLoader()
    
    return _config_instance


# Convenience alias
Config = get_config


if __name__ == "__main__":
    # Test the config loader
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        config = ConfigLoader()
        print(f"✅ Config loader initialized: {config}")
        print(f"📊 Configuration keys: {list(config.get_all().keys())}")
        
        # Test get with default
        model = config.get("openai.model", "gpt-3.5-turbo")
        print(f"🤖 OpenAI Model: {model}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


