"""Simple in-memory authentication helpers for the MVP demo."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import uuid4

from . import data


TOKEN_TTL = timedelta(hours=8)


@dataclass
class AuthenticatedUser:
    username: str
    display_name: str
    role: str
    permissions: list[str]


class TokenStore:
    """Tracks bearer tokens issued to demo users."""

    def __init__(self) -> None:
        self._tokens: Dict[str, tuple[AuthenticatedUser, datetime]] = {}

    def issue_token(self, user: AuthenticatedUser) -> str:
        self._cleanup()
        token = uuid4().hex
        self._tokens[token] = (user, datetime.utcnow())
        return token

    def get_user(self, token: str) -> Optional[AuthenticatedUser]:
        self._cleanup()
        record = self._tokens.get(token)
        if not record:
            return None
        user, issued_at = record
        if datetime.utcnow() - issued_at > TOKEN_TTL:
            self._tokens.pop(token, None)
            return None
        return user

    def revoke(self, token: str) -> None:
        self._tokens.pop(token, None)

    def _cleanup(self) -> None:
        expired = [
            token
            for token, (_, issued_at) in self._tokens.items()
            if datetime.utcnow() - issued_at > TOKEN_TTL
        ]
        for token in expired:
            self._tokens.pop(token, None)


def verify_credentials(username: str, password: str) -> Optional[AuthenticatedUser]:
    user_record = data.USERS.get(username)
    if not user_record:
        return None
    if user_record["password"] != password:
        return None
    return AuthenticatedUser(
        username=username,
        display_name=user_record["display_name"],
        role=user_record["role"],
        permissions=user_record["permissions"],
    )


token_store = TokenStore()
