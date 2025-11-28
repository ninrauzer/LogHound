"""
config_loader.py
----------------
Loads and validates configuration from config.json.
Provides default values if the file doesn't exist or has errors.
"""

import json
import os


def load_config(config_file="config.json"):
    """
    Load configuration from a JSON file.
    
    Args:
        config_file: Path to configuration file (default config.json)
    
    Returns:
        dict: Dictionary with loaded configuration
    """
    config_default = {
        "base_path": r"C:\LogOps",
        "extensions": [".log", ".txt", ".csv"],
        "log_types": ["ALL"],
        "report_dir": r"C:\BrainStein\LogHound\reports",
        "verbose": "ERROR",
        "search_string": "",
        "ip_suspicious_threshold": 50
    }
    
    if not os.path.exists(config_file):
        print(f"[WARNING] Configuration file not found. Using default values.")
        return config_default
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Validate required fields
        for key in config_default:
            if key not in config:
                config[key] = config_default[key]
        
        return config
    
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error reading config.json: {e}")
        print(f"   Using default values.")
        return config_default
    except Exception as e:
        print(f"[ERROR] Unexpected error loading configuration: {e}")
        return config_default
