"""Category helpers adapted from the original expense bot; no live integrations."""
from typing import Dict

def _norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = (
        s.replace("á", "a").replace("à", "a").replace("ã", "a").replace("â", "a")
         .replace("é", "e").replace("ê", "e")
         .replace("í", "i")
         .replace("ó", "o").replace("ô", "o").replace("õ", "o")
         .replace("ú", "u")
         .replace("ç", "c")
    )
    return s

def apply_rules_from_sheet(text: str, options: dict) -> dict:
    """
    Regra determinística: classifica TIPO usando keywords (coluna B).
    """
    t = _norm(text)
    out: Dict[str, str] = {}

    kw_map = options.get("tipo_keywords", {}) or {}
    for kw in sorted(kw_map.keys(), key=len, reverse=True):
        if kw and kw in t:
            out["tipo"] = kw_map[kw]
            break
    return out

