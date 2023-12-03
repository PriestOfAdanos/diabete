import requests
port = 8090
def test_train_model_endpoint(token):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        # requests won't add a boundary if this header is set when you pass files=
        # 'Content-Type': 'multipart/form-data',
    }

    files = {
        'file': ('diabetes.csv', open('diabetes.csv', 'rb'), 'text/csv'),
    }

    response = requests.post('http://localhost:8090/train', headers=headers, files=files)
    assert response.status_code == 200
    print("train 200")

def get_login():
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'grant_type': '',
        'username': 'senior_registrar@hospital.com',
        'password': 'passwd',
        'scope': '',
        'client_id': '',
        'client_secret': '',
    }

    response = requests.post('http://localhost:8090/login', headers=headers, data=data)

    return response

def test_predict_diabetes_endpoint(token):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    json_data = {
        'patient_id': None,
        'input': {
            'pregnancies': 0,
            'glucose': 0,
            'blood_pressure': 0,
            'skin_thickness': 0,
            'insulin': 0,
            'bmi': 0,
            'diabetes_pedigree_function': 0,
            'age': 0,
        },
    }

    response = requests.post(f'http://localhost:{port}/predict', headers=headers, json=json_data)
    assert response.status_code == 200
    print("predict: 200")

def test_get_data_endpoint(token):
    headers = {
        'accept': 'text/html',
        'Authorization': f'Bearer {token}',
    }

    response = requests.get(f'http://localhost:{port}/data', headers=headers)
    assert response.status_code == 200
    print("data: 200")

def test_signup_endpoint(token):
    print("signup")
    url = f"http://localhost:{port}/signup"
    # Replace this with the appropriate user data for your endpoint
    user_data = {
        "email": "test@example.com",
        "password": "yourpassword"
    }
    response = requests.post(url, json=user_data)
    assert response.status_code == 200
token = get_login().json().get("access_token")
test_get_data_endpoint(token)
test_predict_diabetes_endpoint(token)
test_train_model_endpoint(token)