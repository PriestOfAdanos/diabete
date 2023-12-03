import datetime
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from fastapi.security import OAuth2PasswordRequestForm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv
import joblib
from kerastuner.tuners import RandomSearch
from keras_tuner import HyperModel
from fastapi import FastAPI, HTTPException, UploadFile, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from fastapi.security import OAuth2PasswordRequestForm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv
import joblib
from keras.models import Sequential
from keras.layers import Dense
from db_manager import DatabaseManager
from keras.models import load_model

from jwt_utils import (
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from db_models import (
    UserRegister,
    TokenSchema,
    User,
    Patient,
    PredictionInput,
    DiabetesHistoricalOutput,
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

model_name = "model"

class MyHyperModel(HyperModel):
    def __init__(self, input_shape):
        self.input_shape = input_shape

    def build(self, hp):
        model = Sequential()
        model.add(Dense(units=hp.Int('units', min_value=32, max_value=512, step=32),
                        activation='relu', input_shape=self.input_shape))
        model.add(Dense(1, activation='linear'))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

@app.post("/train")
async def train_model(file: UploadFile, user: User = Depends(get_current_user)):
    db.insert_diabetes_data(file.file)

    df = db.select_all_diabetes_data()

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    input_size = X_train.shape[1]  # Number of features

    model = Sequential()
    model.add(Dense(64, input_shape=(input_size,), activation='linear'))
    model.add(Dense(32, activation='linear'))
    model.add(Dense(16, activation='linear'))
    model.add(Dense(1, activation='linear'))

    model.compile(optimizer='adam', loss='mean_squared_error')

    input_shape = [X_train.shape[1]]  # Assuming X_train is your input data
    hypermodel = MyHyperModel(input_shape=input_shape)


    tuner = RandomSearch(
    hypermodel,
    objective='val_loss',
    max_trials=5,
    executions_per_trial=3,
    directory='my_dir',
    project_name='hparam_tuning'
    )

    tuner.search(X_train, y_train, epochs=10, validation_data=(X_test, y_test))
    best_model = tuner.get_best_models(num_models=1)[0]
    best_model.save(model_name)

    return {"message": "Model trained and saved successfully"}


@app.post("/predict")
async def predict_diabetes(
    input_data: PredictionInput, user: User = Depends(get_current_user)
):
   
    try:
        model = load_model(model_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=500, detail="Model not found. Please train the model first."
        )
    i_data  = input_data.dict()['input']
    input_df = pd.DataFrame([i_data])
    prediction = model.predict(input_df)
    prediction_native_type = int(prediction[0])  # or float, as appropriate
    if input_data.patient_id is not None:
        db.add_historical_data_to_patient(
            patient_id=input_data.patient_id,
            output=DiabetesHistoricalOutput(
                pregnancies=input_data.input.pregnancies,
                glucose=input_data.input.glucose,
                blood_pressure=input_data.input.blood_pressure,
                skin_thickness=input_data.input.skin_thickness,
                insulin=input_data.input.insulin,
                bmi=input_data.input.bmi,
                diabetes_pedigree_function=input_data.input.diabetes_pedigree_function,
                age=input_data.input.age,
                prediction=bool(prediction_native_type),
                created_at=datetime.datetime.today().timestamp(),
            ),
        )

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


@app.get("/me", summary="Get details of currently logged in user", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
    return user


@app.post("/patient", summary="Adds new patient to database", response_model=Patient)
async def create_patient(patient_data: Patient, user: User = Depends(get_current_user)):
    return db.create_patient(patient_data)


@app.get(
    "/patient", summary="Get list of patients with data", response_model=List[Patient]
)
async def get_users(user: User = Depends(get_current_user)):
    return db.get_patients()
