from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv
import joblib

from db_manager import DatabaseManager


class DiabetesPredictionInput(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree_function: float
    age: int


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
async def train_model(file: UploadFile):
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
async def predict_diabetes(input_data: DiabetesPredictionInput):
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
async def get_data_from_database():
    return db.select_all_diabetes_data().to_html(notebook=True)
