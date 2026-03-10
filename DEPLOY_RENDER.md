# Deployment Guide: Render + Docker + Azure SQL

## 1. Prerequisites
- Your code is pushed to GitHub.
- Azure SQL database is already online and accessible.
- SQL login/user is ready (`DB_USER`, `DB_PASSWORD`).

## 2. Render Service Creation
1. In Render: `New +` -> `Web Service`.
2. Connect your GitHub repo `proslawa/Projet_BDD2`.
3. Root directory: leave empty (your app files are already at repo root).
4. Render detects `render.yaml` automatically (Blueprint), or you can deploy manually with Docker.

## 3. Environment Variables (Render dashboard)
Set these variables in Render:

- `SECRET_KEY`: long random value
- `ITEMS_PER_PAGE`: `10`
- `DB_DRIVER`: `ODBC Driver 18 for SQL Server`
- `DB_SERVER`: `<your-server>.database.windows.net`
- `DB_PORT`: `1433`
- `DB_DATABASE`: `PROJET_BDD2`
- `DB_USER`: `<azure-sql-user>`
- `DB_PASSWORD`: `<azure-sql-password>`
- `DB_ENCRYPT`: `yes`
- `DB_TRUST_CERT`: `no`
- `DB_TIMEOUT`: `30`

## 4. Azure SQL Network Rules
In Azure SQL Server firewall:
- Allow connections from Azure services.
- Add Render outbound IPs (recommended for production hardening).

## 5. Start Command
Handled by Docker `CMD`:

```bash
gunicorn --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:${PORT:-10000} wsgi:flask_app
```

## 6. Health Check
- Endpoint: `/health`
- Configured in `render.yaml`.

## 7. Common Issues
- `pyodbc` error: verify ODBC 18 is installed (handled by Dockerfile).
- SQL auth error: verify `DB_USER`/`DB_PASSWORD`.
- TLS error: keep `DB_ENCRYPT=yes`, `DB_TRUST_CERT=no` for Azure SQL.
