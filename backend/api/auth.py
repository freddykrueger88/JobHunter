from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.core.database import get_db
from backend.models.user import User
from backend.core.security import verify_password, hash_password, create_access_token, AUTH_ENABLED

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str


@router.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    if not AUTH_ENABLED:
        return {"access_token": "auth-disabled", "token_type": "bearer"}
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falsche Zugangsdaten")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if not AUTH_ENABLED:
        raise HTTPException(status_code=400, detail="Auth ist deaktiviert (AUTH_ENABLED=false)")
    exists = await db.execute(select(User).where(User.username == data.username))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")
    user = User(username=data.username, hashed_password=hash_password(data.password))
    db.add(user)
    await db.commit()
    return {"message": f"Benutzer '{data.username}' angelegt"}


@router.post("/change-password")
async def change_password(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    user.hashed_password = hash_password(data.password)
    await db.commit()
    return {"message": "Passwort geändert"}
