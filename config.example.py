import os
import pyodbc

# Copy this file to config.py for local use, or set these variables in your OS/host.
SECRET_KEY = os.getenv("SECRET_KEY", "replace-with-a-strong-secret")
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))

DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT")  # ex: 1433
DB_DATABASE = os.getenv("DB_DATABASE", "PROJET_BDD2")
DB_USER = os.getenv("DB_USER")  # ex: sa
DB_PASSWORD = os.getenv("DB_PASSWORD")  # ex: strong-password
DB_ENCRYPT = os.getenv("DB_ENCRYPT", "yes")
DB_TRUST_CERT = os.getenv("DB_TRUST_CERT", "yes")
DB_TIMEOUT = os.getenv("DB_TIMEOUT", "30")
DB_ODBC_EXTRA = os.getenv("DB_ODBC_EXTRA", "")


def get_connection():
    parts = [
        f"DRIVER={{{DB_DRIVER}}};",
        f"SERVER={DB_SERVER}{(',' + DB_PORT) if DB_PORT else ''};",
        f"DATABASE={DB_DATABASE};",
        f"Encrypt={DB_ENCRYPT};",
        f"TrustServerCertificate={DB_TRUST_CERT};",
        f"Connection Timeout={DB_TIMEOUT};",
    ]

    if DB_USER and DB_PASSWORD:
        parts.append(f"UID={DB_USER};")
        parts.append(f"PWD={DB_PASSWORD};")
    else:
        parts.append("Trusted_Connection=yes;")

    if DB_ODBC_EXTRA:
        parts.append(DB_ODBC_EXTRA if DB_ODBC_EXTRA.endswith(";") else f"{DB_ODBC_EXTRA};")

    conn_str = "".join(parts)
    return pyodbc.connect(conn_str)
