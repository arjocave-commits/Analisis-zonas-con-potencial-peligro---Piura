import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

print("Controladores ODBC instalados:")
for controlador in pyodbc.drivers():
    print(controlador)

url = URL.create(
    "mssql+pyodbc",
    host=r"LAPTOP-5FPIF11N\SQLEXPRESS",
    database="PiuraEmergencias",
    query={
        "driver": "ODBC Driver 18 for SQL Server",
        "Trusted_Connection": "yes",
        "Encrypt": "yes",
        "TrustServerCertificate": "yes",
    },
)

engine = create_engine(url)

with engine.connect() as conexion:
    resultado = conexion.execute(
        text("""
            SELECT
                @@SERVERNAME AS servidor,
                DB_NAME() AS base_actual,
                SUSER_SNAME() AS usuario
        """)
    ).mappings().one()

    print(dict(resultado))