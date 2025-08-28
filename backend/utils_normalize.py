import hashlib, re
from typing import Optional

_ws = re.compile(r"\s+")

def norm(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = _ws.sub(" ", s)
    return s

def make_hash_key(source: str, title: str, company: str | None, location: str | None, canonical_url: str | None) -> str:
    base = "|".join([
        norm(source),
        norm(title),
        norm(company),
        norm(location),
        norm(canonical_url),
    ])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
