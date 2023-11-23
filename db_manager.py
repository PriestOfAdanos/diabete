import datetime
from typing import Optional, BinaryIO

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import Response
from pysqlitecipher.sqlitewrapper import SqliteCipher
import os
import logging

import password_utils
from db_models import UserOut, UserRegister


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
                ["last_login", "REAL"],
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
                datetime.datetime.now().timestamp(),
            ],
            True,
        )

        self.db.createTable(
            "patients",
            [
                ["first_name", "TEXT"],
                ["last_name", "TEXT"],
                ["pregnancies", "INT"],
                ["email", "TEXT"],
                ["phone_number", "TEXT"],
                ["glucose", "REAL"],
                ["blood_pressure", "REAL"],
                ["skin_thickness", "REAL"],
                ["insulin", "REAL"],
                ["bmi", "REAL"],
                ["diabetes_pedigree_function", "REAL"],
                ["age", "INT"],
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
            print(d)
            if d[3] == email:
                return UserOut(
                    first_name=d[1],
                    last_name=d[2],
                    email=d[3],
                    phone_number=d[4],
                    hashed_password=d[5],
                    last_login=datetime.datetime.fromtimestamp(d[6]),
                )
        return None

    def create_doctor(self, user: UserRegister):
        columns, data = self.db.getDataFromTable("doctors", True)
        for d in data:
            if d[2] == user.email or d[3] == user.phone_number:
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
                None,
            ],
            True,
        )
        return Response(
            f"Successfully created a doctor {user.first_name} {user.last_name}"
        )
