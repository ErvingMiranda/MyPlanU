from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordBearer

from app.core.Database import ObtenerSesion
from app.models.Goal import Usuario
from app.core.Auth import hash_password, verify_password, create_access_token, decode_access_token

RouterAuth = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RegistroIn(BaseModel):
    Correo: EmailStr
    Nombre: str
    Contrasena: str

class LoginIn(BaseModel):
    Correo: EmailStr
    Contrasena: str

class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"

@RouterAuth.post("/auth/registro", response_model=TokenRespuesta, status_code=201)
def Registro(datos: RegistroIn, SesionBD: Session = Depends(ObtenerSesion)):
    # Verificar duplicado
    existe = SesionBD.exec(select(Usuario).where(Usuario.Correo == datos.Correo)).first()
    if existe:
        raise HTTPException(status_code=409, detail="Correo ya registrado")
    u = Usuario(Correo=datos.Correo, Nombre=datos.Nombre, ContrasenaHash=hash_password(datos.Contrasena))
    SesionBD.add(u)
    SesionBD.commit()
    SesionBD.refresh(u)
    token = create_access_token(str(u.Id))
    return TokenRespuesta(access_token=token)

@RouterAuth.post("/auth/login", response_model=TokenRespuesta)
def Login(datos: LoginIn, SesionBD: Session = Depends(ObtenerSesion)):
    u = SesionBD.exec(select(Usuario).where(Usuario.Correo == datos.Correo, Usuario.EliminadoEn.is_(None))).first()
    if not u or not verify_password(datos.Contrasena, u.ContrasenaHash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")
    token = create_access_token(str(u.Id))
    return TokenRespuesta(access_token=token)

def get_current_user(SesionBD: Session = Depends(ObtenerSesion), token: str = Depends(oauth2_scheme)) -> Usuario:
    payload = decode_access_token(token)
    if not payload or 'sub' not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
    try:
        uid = int(payload['sub'])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
    u = SesionBD.get(Usuario, uid)
    if not u or u.EliminadoEn is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no valido")
    return u
