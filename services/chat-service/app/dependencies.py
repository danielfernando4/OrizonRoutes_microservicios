import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer()


def decode_token(token: str) -> dict:
    """Decodifica y valida un JWT emitido por el Identity Service.

    Lanza HTTPException en caso de error. Usado por el endpoint REST.
    Para WebSockets se usa `decode_token_or_none`, que no depende del
    ciclo de excepciones HTTP.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        ) from exc

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    return {
        "id": user_id,
        "role": payload.get("role"),
        "email": payload.get("email"),
    }


def decode_token_or_none(token: str) -> dict | None:
    """Variante silenciosa de decode_token, pensada para el handshake WS."""
    try:
        return decode_token(token)
    except HTTPException:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    return decode_token(credentials.credentials)
