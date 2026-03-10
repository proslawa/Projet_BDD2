import os
import pyodbc

# Copy this file to config.py for local use, or set these variables in your OS/host.
SECRET_KEY = os.getenv("SECRET_KEY", "replace-with-a-strong-secret")
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))

DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_DATABASE = os.getenv("DB_DATABASE", "PROJET_BDD2")
DB_USER = os.getenv("DB_USER")  # ex: sa
DB_PASSWORD = os.getenv("DB_PASSWORD")  # ex: strong-password
DB_TRUST_CERT = os.getenv("DB_TRUST_CERT", "yes")


def get_connection():
    parts = [
        f"DRIVER={{{DB_DRIVER}}};",
        f"SERVER={DB_SERVER};",
        f"DATABASE={DB_DATABASE};",
        f"TrustServerCertificate={DB_TRUST_CERT};",
    ]

    if DB_USER and DB_PASSWORD:
        parts.append(f"UID={DB_USER};")
        parts.append(f"PWD={DB_PASSWORD};")
    else:
        parts.append("Trusted_Connection=yes;")

    conn_str = "".join(parts)
    return pyodbc.connect(conn_str)
