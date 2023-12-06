# Dokumentacja dla API Predykcji Cukrzycy

## Przegląd
Dokumentacja prezentuje API do predykcji cukrzycy zaimplementowane za pomocą FastAPI. API łączy w sobie modele uczenia maszynowego do predykcji cukrzycy, uwierzytelnianie użytkowników oraz zarządzanie danymi.

## Wykorzystane Biblioteki
- FastAPI: Nowoczesny framework do tworzenia API.
- Pandas: Biblioteka do analizy i manipulacji danymi.
- Scikit-learn: Biblioteka do uczenia maszynowego.
- Keras: API do głębokiego uczenia.
- Keras Tuner: Narzędzie do dostrajania hiperparametrów dla modeli Keras.
- Dotenv: Zarządzanie zmiennymi środowiskowymi.
- Joblib: Biblioteka do serializacji.

## Główne Komponenty
1. **Konfiguracja FastAPI**: Używa FastAPI, middleware CORS dla zapytań cross-origin oraz zarządzania zmiennymi środowiskowymi.

2. **Zarządzanie Bazą Danych**: Wykorzystuje `DatabaseManager` do operacji na bazie danych.

3. **Autentykacja**: Używa tokenów JWT do bezpiecznego uwierzytelniania użytkowników.

4. **Endpoint Trenowania Modelu (`/train`)**: 
   - Trenuje model regresji logistycznej oraz sieć neuronową przy użyciu przesłanych danych.
   - Używa Keras Tuner do optymalizacji hiperparametrów.
   - Zapisuje najlepszy model.

5. **Endpoint Predykcji (`/predict`)**:
   - Ładuje wytrenowany model.
   - Przewiduje status cukrzycy na podstawie podanych cech.

6. **Endpoint Pobierania Danych (`/data`)**: Dostarcza reprezentację HTML danych o cukrzycy.

7. **Rejestracja Użytkownika (`/signup`)**: Rejestruje nowych użytkowników.

8. **Logowanie (`/login`)**: Uwierzytelnia użytkowników i dostarcza tokeny dostępu i odświeżania.

9. **Szczegóły Użytkownika (`/me`)**: Pobiera szczegóły zalogowanego użytkownika.

## Architektura Modelu
- **Regresja Logistyczna**: Używana do początkowej predykcji.
- **Sieć Neuronowa**: Sekwencyjny model z warstwami gęstymi. Architektura jest optymalizowana za pomocą Keras Tuner.

## Bezpieczeństwo
- Używa JWT do bezpiecznej autentykacji opartej na tokenach.
- Szyfrowanie haseł dla bezpiecznego przechowywania i weryfikacji.

## Baza danych
- W projekcie użyta została baza danych SQLite
- Baza danych zawiera 3 tabele
   - diabetes - zawiera dane do szkolenia modelu
   - patients - zawiera informacje o pacjencie oraz jego historię predykcji
   - doctors  - zawiara listę kont wraz z zaszyfrowanymi hasłami algorytmem `bcrypt`
- Wszystkie table (łącznie z nazwą tabeli i kolumn) są zaszyfrowane algorytmemt `md5` używając funkcji hashującej `SHA512` dzięki bibliotece SQLCipher

## Operacje na Bazie Danych
- Wstawianie i pobieranie danych o cukrzycy.
- Rejestracja użytkowników i autentykacja.

## Model Użytkownika
- Definiuje modele danych użytkownika do rejestracji, uwierzytelnienia i reprezentacji wyników.

## Użycie
1. **Trenowanie Modelu**:
   - Endpoint: `/train`
   - Metoda: POST
   - Wymaga uwierzytelnionego użytkownika.
   - Przesyłanie zbioru danych o cukrzycy do treningu.

2. **Wykonywanie Predykcji**:
   - Endpoint: `/predict`
   - Metoda: POST
   - Wymaga wytrenowanego modelu i uwierzytelnionego użytkownika.

3. **Pobieranie Danych**:
   - Endpoint: `/data`
   - Metoda: GET
   - Wymaga uwierzytelnionego użytkownika.

4. **Rejestracja Użytkownika**:
   - Endpoint: `/signup`
   - Metoda: POST

5. **Logowanie Użytkownika**:
   - Endpoint: `/


## How to:
 - pip install -r requirements.txt
 - uvicorn app:app --reload
 - http://127.0.0.1:8000/docs#/ <- testowanie endpointów

## To run frontend:
- npm run dev

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

## Testowanie
odpalamy aplikację jak ^
uruchamiamy komendę:
```bash 
python3 ./tests/test.py
```
