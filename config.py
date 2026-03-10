import pyodbc

SECRET_KEY     = "PROJET_BDD2"
ITEMS_PER_PAGE = 10


def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=.\\PROJET_BDD2;"        # instance nommée
        "DATABASE=PROJET_BDD2;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)