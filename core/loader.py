# core/loader.py
import pandas as pd
import sqlalchemy
import requests
import os

class DataLoader:

    @staticmethod
    def from_csv(filepath: str) -> pd.DataFrame:
        """Load data from a CSV file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"File not found: {filepath}"
            )
        return pd.read_csv(filepath)

    @staticmethod
    def from_excel(
        filepath: str, sheet=0
    ) -> pd.DataFrame:
        """Load data from an Excel file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"File not found: {filepath}"
            )
        return pd.read_excel(filepath, sheet_name=sheet)

    @staticmethod
    def from_postgres(
        connection_string: str, query: str
    ) -> pd.DataFrame:
        """Load data from PostgreSQL database"""
        try:
            engine = sqlalchemy.create_engine(
                connection_string
            )
            return pd.read_sql(query, engine)
        except Exception as e:
            raise ConnectionError(
                f"Database connection failed: {e}"
            )

    @staticmethod
    def from_api(
        url: str,
        params: dict = None,
        data_key: str = None,
        headers: dict = None
    ) -> pd.DataFrame:
        """Load data from a REST API endpoint"""
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data_key and data_key in data:
                data = data[data_key]
            return pd.DataFrame(data)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"API request failed: {e}"
            )