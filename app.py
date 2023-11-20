from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

class DiabetesPredictionInput(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree_function: float
    age: int

app = FastAPI()

@app.post("/train")
async def train_model():

    df = pd.read_csv('diabetes.csv')
    df.columns = ['pregnancies','glucose','blood_pressure','skin_thickness','insulin','bmi','diabetes_pedigree_function','age','outcome']

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    joblib.dump(model, 'diabetes_model.joblib')

    return {"message": "Model trained and saved successfully"}

@app.post("/predict")
async def predict_diabetes(input_data: DiabetesPredictionInput):
    try:
        model = joblib.load('diabetes_model.joblib')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Model not found. Please train the model first.")
    input_df = pd.DataFrame([input_data.dict()])
    prediction = model.predict(input_df)
    prediction_native_type = int(prediction[0])  # or float, as appropriate
    return {"prediction": prediction_native_type}