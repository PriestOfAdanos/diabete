import datetime
from typing import Optional, BinaryIO

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import Response
from pysqlitecipher.sqlitewrapper import SqliteCipher
import os
import logging

import password_utils
from db_models import UserOut, UserRegister, Patient, DiabetesHistoricalOutput


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DatabaseManager(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.db: Optional[SqliteCipher] = None
        self._setup_database_object()

    def _setup_database_object(self) -> None:
        try:
            self.db = SqliteCipher(
                dataBasePath=os.getenv("DB_PATH"),
                checkSameThread=False,
                password=os.getenv("DB_PASSWORD"),
            )
        except Exception as ex:
            logging.error(ex)

        for table_name in ["diabetes", "doctors", "patients"]:
            if not self.db.checkTableExist(table_name):
                self._init_database()
                break

    def _init_database(self) -> None:
        self.db.createTable(
            "diabetes",
            [
                ["pregnancies", "INT"],
                ["glucose", "REAL"],
                ["blood_pressure", "REAL"],
                ["skin_thickness", "REAL"],
                ["insulin", "REAL"],
                ["bmi", "REAL"],
                ["diabetes_pedigree_function", "REAL"],
                ["age", "INT"],
                ["outcome", "INT"],
            ],
            True,
            True,
        )

        self.db.createTable(
            "doctors",
            [
                ["first_name", "TEXT"],
                ["last_name", "TEXT"],
                ["email", "TEXT"],
                ["phone_number", "TEXT"],
                ["hashed_password", "TEXT"],
            ],
            True,
            True,
        )

        self.db.insertIntoTable(
            "doctors",
            [
                "Senior",
                "Registrar",
                "senior_registrar@hospital.com",
                "+48-111-222-333",
                password_utils.get_hashed_password(os.getenv("DEV_PASSWORD")),
            ],
            True,
        )

        self.db.createTable(
            "patients",
            [
                ["PESEL", "TEXT"],
                ["first_name", "TEXT"],
                ["last_name", "TEXT"],
                ["email", "TEXT"],
                ["phone_number", "TEXT"],
                ["historical_data", "BLOB"],
            ],
            True,
            True,
        )

    def select_all_diabetes_data(self) -> pd.DataFrame:
        columns, data = self.db.getDataFromTable("diabetes", True, True)
        return pd.DataFrame(data=data, columns=columns)

    def insert_diabetes_data(self, csv_file: BinaryIO) -> None:
        df = pd.read_csv(csv_file)
        df.columns = [
            "pregnancies",
            "glucose",
            "blood_pressure",
            "skin_thickness",
            "insulin",
            "bmi",
            "diabetes_pedigree_function",
            "age",
            "outcome",
        ]

        for i in df.index:
            self.db.insertIntoTable(
                "diabetes", [df[col_name][i] for col_name in df.columns], True
            )

    def dump_diabetes_data_to_csv(self) -> None:
        pass

    def get_doctor(self, email: str) -> Optional[UserOut]:
        columns, data = self.db.getDataFromTable("doctors", True)
        for d in data:
            if d[3] == email:
                return UserOut(
                    first_name=d[1],
                    last_name=d[2],
                    email=d[3],
                    phone_number=d[4],
                    hashed_password=d[5],
                )
        return None

    def create_doctor(self, user: UserRegister):
        columns, data = self.db.getDataFromTable("doctors", True)
        for d in data:
            if d[3] == user.email or d[4] == user.phone_number:
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor with email {user.email} or phone number {user.phone_number} already exists.",
                )
        self.db.insertIntoTable(
            "doctors",
            [
                user.first_name,
                user.last_name,
                user.email,
                user.phone_number,
                password_utils.get_hashed_password(user.password),
            ],
            True,
        )
        return Response(
            f"Successfully created a doctor {user.first_name} {user.last_name}"
        )

    def create_patient(self, patient: Patient):
        columns, data = self.db.getDataFromTable("patients", True)
        for d in data:
            if (
                d[1] == patient.PESEL
                or d[4] == patient.email
                or d[5] == patient.phone_number
            ):
                raise HTTPException(
                    status_code=404,
                    detail=f"Patient with PESEL {patient.PESEL} or email {patient.email} or phone number {patient.phone_number} already exists.",
                )
        self.db.insertIntoTable(
            "patients",
            [
                patient.PESEL,
                patient.first_name,
                patient.last_name,
                patient.email,
                patient.phone_number,
                "".encode(),
            ],
            True,
        )

        return patient

    def add_historical_data_to_patient(
        self, patient_id: int, output: DiabetesHistoricalOutput
    ):
        columns, data = self.db.getDataFromTable("patients", True)
        exists = False
        patient_data = None
        print("hm")
        for d in data:
            if d[0] == patient_id:
                exists = True
                patient_data = d[6]
                break
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with ID {patient_id} does not exists.",
            )
        print("got patient")
        patient_data = patient_data.decode()
        print("patient current data:", patient_data)
        data_str = (
            f"{output.pregnancies},{output.glucose},{output.blood_pressure},{output.skin_thickness},"
            f"{output.insulin},{output.bmi},{output.diabetes_pedigree_function},{output.age},"
            f"{output.prediction},{output.created_at.timestamp()};"
        )

        patient_data += data_str

        print("patient current data:", patient_data)
        self.db.updateInTable(
            "patients", patient_id, "historical_data", patient_data.encode(), True
        )

    def get_patients(self):
        columns, data = self.db.getDataFromTable("patients", True)
        patients = []
        for d in data:
            historical_data = []

            for data_point in d[6].decode().split(";")[:-1]:
                data_point = data_point.split(",")
                historical_data.append(
                    DiabetesHistoricalOutput(
                        pregnancies=data_point[0],
                        glucose=data_point[1],
                        blood_pressure=data_point[2],
                        skin_thickness=data_point[3],
                        insulin=data_point[4],
                        bmi=data_point[5],
                        diabetes_pedigree_function=data_point[6],
                        age=data_point[7],
                        prediction=data_point[8],
                        created_at=data_point[9],
                    )
                )

            patients.append(
                Patient(
                    id=d[0],
                    PESEL=d[1],
                    first_name=d[2],
                    last_name=d[3],
                    email=d[4],
                    phone_number=d[5],
                    historical_data=historical_data,
                )
            )
        return patients
