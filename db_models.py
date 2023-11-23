from datetime import datetime

from pydantic import BaseModel


class DiabetesPredictionInput(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree_function: float
    age: int


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str


class UserOut(User):
    hashed_password: str
    last_login: datetime


class UserRegister(User):
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
