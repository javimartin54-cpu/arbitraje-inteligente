import requests
from jose import jwt
from jose.exceptions import JWTError
from fastapi import Header, HTTPException

_cache = {"jwks": None, "url": None}

def _jwks(url: str):
    if _cache["jwks"] is None or _cache["url"] != url:
        _cache["jwks"] = requests.get(url, timeout=10).json()["keys"]
        _cache["url"] = url
    return _cache["jwks"]

def get_current_user(authorization: str = Header(None), jwks_url: str = "") -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        key = next((k for k in _jwks(jwks_url) if k.get("kid") == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token key")
        claims = jwt.decode(token, key, options={"verify_aud": False})
        sub = claims.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token subject")
        return sub
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
