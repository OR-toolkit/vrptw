import yaml
import os
from typing import Any, Dict

class ConfigLoader:
    _config = None

    @classmethod
    def load_config(cls, config_path: str = "src/config.yaml") -> Dict[str, Any]:
        """
        Loads the YAML configuration file.
        """
        if cls._config is None:
            if not os.path.exists(config_path):
                # Fallback to absolute path if running from root
                abs_path = os.path.join(os.getcwd(), config_path)
                if not os.path.exists(abs_path):
                    raise FileNotFoundError(f"Configuration file not found at {config_path}")
                config_path = abs_path
                
            with open(config_path, 'r') as f:
                cls._config = yaml.safe_load(f)
        return cls._config

def get_config() -> Dict[str, Any]:
    return ConfigLoader.load_config()
