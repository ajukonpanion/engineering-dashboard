from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict
import hashlib
import hmac

@dataclass
class UserDB:
    # username -> password_hash (sha256)
    users: Dict[str, str]

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_users(path: str) -> UserDB:
    p = Path(path)
    if not p.exists():
        # default fallback (professional default still allowed for now)
        return UserDB(users={"admin": _sha256("admin")})
    data = json.loads(p.read_text(encoding="utf-8"))
    # expects {"users": [{"username":"Ajzal","password":"qwerty"}, ...]}
    users = {"admin": _sha256("admin")}
    for u in data.get("users", []):
        if "username" in u and "password" in u:
            users[u["username"]] = _sha256(u["password"])
    return UserDB(users=users)

def verify_user(db: UserDB, username: str, password: str) -> bool:
    ph = db.users.get(username)
    if not ph:
        return False
    return hmac.compare_digest(ph, _sha256(password))
