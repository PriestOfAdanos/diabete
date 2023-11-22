from fastapi import FastAPI, HTTPException, UploadFile, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from fastapi.security import OAuth2PasswordRequestForm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv
import joblib

from db_manager import DatabaseManager
from jwt_utils import (
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from models import (
    DiabetesPredictionInput,
    UserRegister,
    TokenSchema,
    User,
    UserOut,
)
from password_utils import verify_password

load_dotenv()
db = DatabaseManager()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/train")
async def train_model(file: UploadFile, user: User = Depends(get_current_user)):
    db.insert_diabetes_data(file.file)

    df = db.select_all_diabetes_data()

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = LogisticRegression()
    model.fit(X_train, y_train)
    joblib.dump(model, "diabetes_model.joblib")

    return {"message": "Model trained and saved successfully"}


@app.post("/predict")
async def predict_diabetes(
    input_data: DiabetesPredictionInput, user: User = Depends(get_current_user)
):
    try:
        model = joblib.load("diabetes_model.joblib")
    except FileNotFoundError:
        raise HTTPException(
            status_code=500, detail="Model not found. Please train the model first."
        )
    input_df = pd.DataFrame([input_data.dict()])
    prediction = model.predict(input_df)
    prediction_native_type = int(prediction[0])  # or float, as appropriate
    return {"prediction": prediction_native_type}


@app.get("/data", response_class=HTMLResponse)
async def get_data_from_database(user: User = Depends(get_current_user)):
    return db.select_all_diabetes_data().to_html(notebook=True)


@app.post("/signup", summary="Create new user")
async def create_user(data: UserRegister):
    return db.create_doctor(data)


@app.post(
    "/login",
    summary="Create access and refresh tokens for user",
    response_model=TokenSchema,
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_doctor(form_data.username)
    print(form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    hashed_pass = user.hashed_password
    print(hashed_pass)
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password",
        )

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


@app.get(
    "/me", summary="Get details of currently logged in user", response_model=UserOut
)
async def get_me(user: User = Depends(get_current_user)):
    return user
