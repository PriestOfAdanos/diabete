from datetime import datetime
from typing import List, Optional

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


class DiabetesHistoricalOutput(DiabetesPredictionInput):
    prediction: bool
    created_at: datetime


class Patient(BaseModel):
    id: Optional[int]
    PESEL: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    historical_data: Optional[List[DiabetesHistoricalOutput]]


class PredictionInput(BaseModel):
    patient_id: Optional[int]
    input: DiabetesPredictionInput


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str


class UserOut(User):
    hashed_password: str


class UserRegister(User):
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
