# Trening Sieci Neuronowej dla Danych o Cukrzycy

Dokumentacja opisuje proces trenowania modelu sieci neuronowej z wykorzystaniem zestawu danych dotyczących cukrzycy. Proces ten obejmuje wstawianie danych, ich selekcję, przetwarzanie, tworzenie modelu, dostrajanie hiperparametrów oraz zapisywanie modelu.

## Wstawianie i Selekcja Danych

Początkowo, dane o cukrzycy są wstawiane do bazy danych, a następnie wybierane do przetwarzania.
```python
db.insert_diabetes_data(file.file)
df = db.select_all_diabetes_data()
```
## Przetwarzanie Wstępne Danych

Zbiór danych jest dzielony na cechy (X) i zmienną docelową (y). Następnie jest podzielony na zestawy treningowe i testowe.
```python
X = df.iloc[:, :-1]
y = df.iloc[:, -1]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```
## Tworzenie Modelu

Tworzony jest sekwencyjny model sieci neuronowej z gęstymi warstwami. Rozmiar wejścia (input_size) jest ustalany na podstawie cech danych treningowych.
```python
input_size = X_train.shape[1]
model = Sequential()
model.add(Dense(64, input_shape=(input_size,), activation='linear'))
model.add(Dense(32, activation='linear'))
model.add(Dense(16, activation='linear'))
model.add(Dense(1, activation='linear'))
model.compile(optimizer='adam', loss='mean_squared_error')
```
## Dostrajanie Hiperparametrów

Definiowany jest niestandardowy hipermodel, a następnie przeprowadzane jest dostrajanie hiperparametrów przy użyciu RandomSearch.
```python
input_shape = [X_train.shape[1]]
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
```
## Zapisywanie Najlepszego Modelu

Najlepszy model z procesu dostrajania jest zapisywany do dalszego wykorzystania.
```python
best_model = tuner.get_best_models(num_models=1)[0]
best_model.save(model_name)
```
## Wnioski

Proces kończy się zwróceniem wiadomości o pomyślnym wytrenowaniu i zapisaniu modelu.
```python
return {"message": "Model trained and saved successfully"}
```
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
