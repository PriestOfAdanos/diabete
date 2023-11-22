from typing import Optional, BinaryIO

import pandas as pd
from pysqlitecipher.sqlitewrapper import SqliteCipher
import os
import logging


class DatabaseManager:
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

        if not self.db.checkTableExist("diabetes"):
            self._init_database()

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
