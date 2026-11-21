from pathlib import Path
import pandas as pd
from sqlalchemy import text

from conexion_sql import engine

archivo = Path(__file__).parent / "poblacion_piura_preparada.xlsx"

poblacion = pd.read_excel(archivo,sheet_name="poblacion_distrital",dtype={"UBIGEO":"string"})

print(poblacion.head().to_string(index=False))
print("Filas:", len(poblacion))
print("Distritos:", poblacion["UBIGEO"].nunique())

duplicados = poblacion.duplicated(["UBIGEO","anio"]).sum()
print("Parejas UBIGEO y años repetidas",duplicados)

print("valores faltantes")
print(poblacion.isna().sum())

anios_esperados = set(range(2018,2027))

cobertura = poblacion.groupby("UBIGEO")["anio"].agg(
    lambda valores: set(valores)==anios_esperados
)

print("Distritos con años incompletos o inesperados:", (~cobertura).sum())

columnas_sql = [
    "UBIGEO",
    "distrito",
    "anio",
    "poblacion_proyectada"
]

datos_sql = poblacion[columnas_sql].copy()

if datos_sql.empty:
    raise ValueError("No se puede crear datos para poblacion")

if datos_sql.isna().any().any():
    raise ValueError("Hay datos faltantes")

if datos_sql.duplicated(["UBIGEO","anio"]).any():
    raise ValueError("Hay datos repetidas")

if not cobertura.all():
    raise ValueError("Hay valores con años incompletos")

datos_sql["UBIGEO"]=datos_sql["UBIGEO"].astype("string").str.strip()

if not datos_sql["UBIGEO"].str.fullmatch(r"20\d{4}", na=False).all():
    raise ValueError("Hay códigos UBIGEO con formato incorrecto para Piura.")

for columna in ["anio","poblacion_proyectada"]:
    valores = pd.to_numeric(datos_sql[columna],errors="raise")

    if valores.mod(1).ne(0).any():
        raise ValueError("Hay valores faltantes o contienen decimales")

    datos_sql[columna] = valores.astype("int64")

    if datos_sql["poblacion_proyectada"].le(0).any():
        raise ValueError("Hay valores menores o iguales a 0")

with engine.begin() as conexion:
    existentes = conexion.execute(
        text("SELECT COUNT(*) FROM dbo.poblacion_distrital")).scalar_one()
    if existentes > 0:
        raise ValueError("La tabla ya fue cargada")

    datos_sql.to_sql(
        name="poblacion_distrital",
        con=conexion,
        schema="dbo",
        if_exists="append",
        index=False,
        chunksize=100,
    )

    cargados = conexion.execute(
        text("SELECT COUNT(*) FROM dbo.poblacion_distrital")
    ).scalar_one()

    if cargados != len(datos_sql):
        raise ValueError ("El conteo no coincide con las filas sql")

print("Carga de poblacion confirmada. Registros: ", cargados)




