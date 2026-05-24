import os
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ExportConfig:
    operating_currencies: List[str] = field(default_factory=list)
    commodity_map: Dict[str, str] = field(default_factory=dict)
    global_settings: Dict[str, Any] = field(default_factory=dict)
    start_date: str = "1970-01-01"
    ignore_future: bool = False
    cutoff_date: Optional[str] = None

    @classmethod
    def load_from_yaml(cls, path: str = "commodity_map.yaml") -> "ExportConfig":
        commodity_map = {}
        global_settings = {}
        
        # Scaffolding: create template if missing
        if not os.path.exists(path):
            try:
                default_template = """# Moneydance to Beancount Configuration Map

settings:
  # Base currencies to declare as operating currencies in Beancount
  operating_currencies: ["TWD", "USD", "EUR"]
  
  # Ignore all transactions, prices, and budgets dated in the future
  ignore_future: false

translations:
  # Map Moneydance commodity names/tickers to Beancount-compliant ASCII symbols.
  # Example:
  # "中華電信": "CH_TELECOM"
"""
                with open(path, "w", encoding="utf-8") as f:
                    f.write(default_template)
                print(f";; Created default configuration file at {path}")
            except Exception as e:
                print(f";; Warning: Failed to create default configuration file: {e}")
        
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                    if config_data:
                        if "translations" in config_data:
                            commodity_map = config_data["translations"] or {}
                        if "settings" in config_data:
                            global_settings = config_data["settings"] or {}
            except Exception as e:
                print(f";; Warning: Failed to load {path}: {e}")
        
        operating_currencies = global_settings.get("operating_currencies", [])
        ignore_future = global_settings.get("ignore_future", False)
        cutoff_date = global_settings.get("cutoff_date", None)
        
        return cls(
            operating_currencies=operating_currencies,
            commodity_map=commodity_map,
            global_settings=global_settings,
            ignore_future=ignore_future,
            cutoff_date=cutoff_date
        )
