## How to:
 - pip install -r requirements.txt
 - uvicorn app:app --reload
 - http://127.0.0.1:8000/docs#/ <- testowanie endpointów

## Co tu jest:
 - endointy train i predict 
 - /predict nie tworzy nic, zwraca json {"predict": int }
 ```bash 
 curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "pregnancies": 0,
  "glucose": 0,
  "blood_pressure": 0,
  "skin_thickness": 0,
  "insulin": 0,
  "bmi": 0,
  "diabetes_pedigree_function": 0,
  "age": 0
}'
 ```
 - /train nie zwraca nic, bierze plik diabetes.csv, tworzy plik diabetes_model.joblib
 ```bash 
 curl -X 'POST' 'http://127.0.0.1:8000/train'  -H 'accept: application/json' -d ''
 ```
