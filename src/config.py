import os
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ExportConfig:
    operating_currencies: List[str] = field(default_factory=list)
    commodity_map: Dict[str, str] = field(default_factory=dict)
    global_settings: Dict[str, Any] = field(default_factory=dict)
    start_date: str = "1970-01-01"

    @classmethod
    def load_from_yaml(cls, path: str = "commodity_map.yaml") -> "ExportConfig":
        commodity_map = {}
        global_settings = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                    if config_data:
                        if "translations" in config_data:
                            commodity_map = config_data["translations"]
                        if "settings" in config_data:
                            global_settings = config_data["settings"]
            except Exception as e:
                print(f";; Warning: Failed to load {path}: {e}")
        
        operating_currencies = global_settings.get("operating_currencies", [])
        
        return cls(
            operating_currencies=operating_currencies,
            commodity_map=commodity_map,
            global_settings=global_settings
        )
