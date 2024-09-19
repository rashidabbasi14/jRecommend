import pyodbc

class DatabaseSchemaFetcher:
    """
    Class responsible for fetching the schema from a SQL Server database using a connection string.
    """
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def fetch_schema(self):
        try:
            # Establish a connection to the SQL Server
            print(self.connection_string)
            connection = pyodbc.connect(self.connection_string)
            cursor = connection.cursor()

            # Fetch table information
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            tables = cursor.fetchall()

            schema = ""
            # Loop through tables and fetch column details
            for table in tables:
                schema += f"Table: {table[0]}\n"
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{table[0]}'
                """)
                columns = cursor.fetchall()
                for column in columns:
                    schema += f"  - {column[0]}: {column[1]}\n"
                schema += "\n"
            
            cursor.close()
            connection.close()
            return schema
        except Exception as e:
            return f"Error fetching schema: {e}"
