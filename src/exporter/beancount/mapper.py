import re
import hashlib
from typing import Optional, Dict
from src.models import Account, Currency, SecurityInfo, InvestmentInfo, BankInfo, AssetInfo, CreditCardInfo, LiabilityInfo, LoanInfo, IncomeInfo, ExpenseInfo

# Default global map for backward compatibility
DEFAULT_COMMODITY_MAP: Dict[str, str] = {}

def normalize_commodity(code: str) -> str:
    """Sanitizes a commodity code to strictly follow Beancount v3 syntax."""
    if not code:
        return "UNKNOWN"
    
    # 1. Convert to uppercase and replace common separators with underscores
    res = code.upper().replace(' ', '_').replace('&', '_')
    
    # 2. Keep only allowed characters: A-Z, 0-9, '.', '_', '-', "'"
    res = "".join(c for c in res if c.isalnum() or c in "._-'")
    
    # 3. Ensure it starts with a letter. If not, prepend SYM_
    if res and res[0].isdigit():
        res = "SYM_" + res
    
    # 4. Final check: if it's empty or still doesn't start with a letter, fallback
    if not res or not res[0].isalpha():
        res = "C_" + (res if res else hashlib.md5(code.encode()).hexdigest()[:8].upper())
        
    # 5. Limit length (Beancount limit is 24)
    return res[:24]

def get_commodity_code(currency: Currency, commodity_map: Optional[Dict[str, str]] = None) -> str:
    """Selects the best Beancount commodity code for a given currency/security."""
    if commodity_map is None:
        commodity_map = DEFAULT_COMMODITY_MAP

    # 1. Check manual translation map first (priority)
    if currency.name in commodity_map:
        return normalize_commodity(commodity_map[currency.name])
    if currency.ticker in commodity_map:
        return normalize_commodity(commodity_map[currency.ticker])
    if currency.code in commodity_map:
        return normalize_commodity(commodity_map[currency.code])

    # 2. Prefer ticker if present
    if currency.ticker:
        return normalize_commodity(currency.ticker)
    
    # 3. Prefer code if it's not a GUID
    code = currency.code
    is_guid = len(code) == 36 and code.count('-') == 4
    if code and not is_guid:
        return normalize_commodity(code)
    
    # 4. Fallback to name
    if currency.name:
        return normalize_commodity(currency.name)
    
    return normalize_commodity(code) if code else "UNKNOWN"

def normalize_name(name: str) -> str:
    # 1. Split by parentheses for hierarchical conversion (e.g. A(B) -> A:B)
    raw_parts = re.split(r'[()]', name)
    
    normalized_parts = []
    for part in raw_parts:
        # 2. Extract alphanumeric components (Unicode-aware, excluding underscore)
        components = re.findall(r'[^\W_]+', part, re.UNICODE)
        
        # 3. Capitalize each component for CamelCase
        normalized_components = [c[0].upper() + c[1:] if c else "" for c in components]
        
        # 4. Join components
        res = "".join(normalized_components)
        if res:
            normalized_parts.append(res)
    
    # 5. Join hierarchical parts with ':'
    result = ":".join(normalized_parts)
    
    # 6. Fallback for completely non-alphanumeric names (rare)
    if not result and name:
        h = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
        result = "U" + h
        
    return result

class AccountRegistry:
    def __init__(self):
        self.used_paths = set()

    def get_unique_path(self, path: str) -> str:
        if path not in self.used_paths:
            self.used_paths.add(path)
            return path
        
        counter = 2
        while True:
            new_path = f"{path}_{counter}"
            if new_path not in self.used_paths:
                self.used_paths.add(new_path)
                return new_path
            counter += 1

def get_beancount_path(account: Account) -> str:
    # If it's a security, collapse it into its parent (the Investment account)
    if isinstance(account.info, SecurityInfo):
        return get_beancount_path(account.info.parent)

    current = account
    path_parts = []
    
    # Climb up and collect names
    while current and current.info is not None:
        name = normalize_name(current.name)
        path_parts.append(name)
        current = current.info.parent
        
    # Determine the category from the account's info
    info = account.info
    if info is None:
        return "Equity:Root"
    
    if isinstance(info, BankInfo):
        category = "Assets:Bank"
    elif isinstance(info, (InvestmentInfo, SecurityInfo)):
        category = "Assets:Investment"
    elif isinstance(info, AssetInfo):
        category = "Assets:Cash"
    elif isinstance(info, CreditCardInfo):
        category = "Liabilities:Card"
    elif isinstance(info, (LiabilityInfo, LoanInfo)):
        category = "Liabilities"
    elif isinstance(info, IncomeInfo):
        category = "Income"
    elif isinstance(info, ExpenseInfo):
        category = "Expenses"
    else:
        category = "Equity"
        
    # If the top-most account name matches the category, skip it to avoid redundant prefix
    # We check the last part of the category (e.g. "Bank" in "Assets:Bank")
    cat_parts = category.split(":")
    if path_parts and path_parts[-1].lower() == cat_parts[-1].lower():
        path_parts.pop()
        
    path_parts.append(category)
    return ":".join(reversed(path_parts))
