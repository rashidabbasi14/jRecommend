import os
import json

class Helper:
    @staticmethod
    def fetch_connection_string():
        return (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
    )

    @staticmethod
    def is_valid_json(string):
        try:
            json.loads(string)
            return True
        except ValueError:
            return False