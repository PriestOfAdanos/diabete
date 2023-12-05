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
