from ninja.security import HttpBearer
from jose import jwt, JWTError
from django.conf import settings
from django.contrib.auth.models import User
from ninja import Router
from django.contrib.auth import authenticate
from pydantic import BaseModel

router = Router()

class LoginSchema(BaseModel):
    username: str
    password: str

@router.post("/token", auth=None)
def get_token(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user is None:
        return {"error": "Неверный логин или пароль"}
    
    payload = {"user_id": user.id}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return {"token": token}

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = User.objects.get(id=user_id)
            request.user = user
            return user
        except (JWTError, User.DoesNotExist):
            return None