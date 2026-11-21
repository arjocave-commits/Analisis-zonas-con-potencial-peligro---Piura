from xml.dom.minidom import ProcessingInstruction

import pandas as pd

from pathlib import Path

from sqlalchemy import text
from conexion_sql import engine

df = pd.read_csv("BD_2003-2025_EMERGENCIAS.csv",sep=";",encoding="cp1252",
    dtype={"COD. DISTRITO": "string"})

print(df.head())

print(df.shape)

piura = df[df["DPTO."]=="PIURA"]

print("Zona Piura hay :" , piura.shape[0])

print(piura["PELIGRO"].value_counts())

print (piura["CODIGO DE EMERGENCIA-SINPAD"].duplicated().sum())

print(piura.isna().sum())

print(piura["AÑO"].value_counts().sort_index())


categorias=["INUNDACION","LLUVIA INTENSA"]

eventos_agua = piura[piura["PELIGRO"].isin(categorias)].copy()

tabla_anual = pd.crosstab(eventos_agua["AÑO"], eventos_agua["PELIGRO"])

print(tabla_anual)

danos_anuales = (eventos_agua.groupby(["AÑO","PELIGRO"])[["DAMNIFICADOS"]].sum())

print(danos_anuales)


inundaciones_2017 = eventos_agua[(eventos_agua["AÑO"]==2017)&(eventos_agua["PELIGRO"]=="INUNDACION")]
print(
    inundaciones_2017[
        ["CODIGO DE EMERGENCIA-SINPAD", "PROV.", "DIST.", "DAMNIFICADOS","AFECTADOS",
"VIVIENDAS DESTRUIDAS",
"VIVIENDAS AFECTADAS"]
    ].sort_values("DAMNIFICADOS", ascending=False).to_string(index=False)
)

resumen_distrital = (inundaciones_2017.groupby(["COD. DISTRITO","DIST."]).
agg(emergencias=("CODIGO DE EMERGENCIA-SINPAD","nunique"),damnificados_reportados=("DAMNIFICADOS","sum"),
afectados_reportados=("AFECTADOS","sum"),viviendas_destruidas=("VIVIENDAS DESTRUIDAS", "sum"),
viviendas_afectadas=("VIVIENDAS AFECTADAS", "sum")))

print(resumen_distrital.sort_values("damnificados_reportados",ascending=False).reset_index().to_string(index=False))



print(inundaciones_2017[inundaciones_2017["COD. DISTRITO"] == "200107"].T.to_string())

cura_mori_2017 = eventos_agua[
    (eventos_agua["COD. DISTRITO"] == "200107")
    & (eventos_agua["AÑO"] == 2017)
]

print(
    cura_mori_2017[
        [
            "CODIGO DE EMERGENCIA-SINPAD",
            "FECHA  DE LA EMER",
            "PELIGRO",
            "DAMNIFICADOS",
            "AFECTADOS",
            "VIVIENDAS DESTRUIDAS"
        ]
    ].to_string(index=False)
)

eventos_agua["observacion_calidad"] = ""

eventos_agua.loc[
    eventos_agua["CODIGO DE EMERGENCIA-SINPAD"] == 86087,
    "observacion_calidad"
] = "Daños pendientes de verificar"

columnas_danos = [
    "DAMNIFICADOS",
    "AFECTADOS",
    "VIVIENDAS DESTRUIDAS",
    "VIVIENDAS AFECTADAS"
]

sin_danos_en_cuatro_campos = (
    eventos_agua[columnas_danos].eq(0).all(axis=1)
)

print(sin_danos_en_cuatro_campos.value_counts())

print(
    pd.crosstab(
        eventos_agua["PELIGRO"],
        sin_danos_en_cuatro_campos
    )
)

eventos_agua["cuatro_danos_en_cero"]=sin_danos_en_cuatro_campos

eventos_agua["fecha_evento"]=pd.to_datetime(eventos_agua["FECHA  DE LA EMER"],format="%d/%m/%Y",errors="coerce")
print(eventos_agua["fecha_evento"].isna().sum())

fechas_por_revisar = eventos_agua.loc[eventos_agua["fecha_evento"].isna(),"FECHA  DE LA EMER"]

print(fechas_por_revisar.head(20).map(repr).to_string(index=False))

pendientes = eventos_agua["fecha_evento"].isna()

eventos_agua.loc[pendientes,"fecha_evento"]=pd.to_datetime(eventos_agua.loc[pendientes,"FECHA  DE LA EMER"],
                                                           format="%m/%d/%y",errors="coerce")

print(eventos_agua["fecha_evento"].isna().sum())

meses = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3,
    "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
    "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9,
    "SETIEMBRE": 9, "OCTUBRE": 10,
    "NOVIEMBRE": 11, "DICIEMBRE": 12
}

mes_original = (
    eventos_agua["MES"]
    .str.strip()
    .str.upper()
    .map(meses)
)

print("Meses sin reconocer:", mes_original.isna().sum())

print(
    "Diferencias de año:",
    (eventos_agua["fecha_evento"].dt.year != eventos_agua["AÑO"]).sum())

print(
    "Diferencias de mes:",
    (eventos_agua["fecha_evento"].dt.month != mes_original).sum()
)

ubigeo = eventos_agua["COD. DISTRITO"]

print("UBIGEO vacios: ",ubigeo.isna().sum())

print("UBIGEO con formatos incorrectos: ",(~ubigeo.str.fullmatch(r"\d{6}", na=False)).sum())

print("UBIGEO fuera de Piura:",(~ubigeo.str.startswith("20", na=False)).sum())

nombres_por_ubigeo = eventos_agua.groupby("COD. DISTRITO")[["PROV.","DIST."]].nunique()

conflictos_ubigeo = nombres_por_ubigeo[
    (nombres_por_ubigeo > 1).any(axis=1)
]

print(conflictos_ubigeo)



danos_numericos = eventos_agua[columnas_danos].apply(pd.to_numeric,errors="coerce")

revision_danos = pd.DataFrame({"faltantes_originales": eventos_agua[columnas_danos].isna().sum(),
                               "valores_no_numericos":(danos_numericos.isna()& eventos_agua[columnas_danos].notna()).sum()
                               ,"valores_negativos":(danos_numericos<0).sum(),
                               "valores_con_decimales":(danos_numericos.notna()& danos_numericos.mod(1).ne(0)).sum()})

print(revision_danos.to_string())


resumen_por_ano = (eventos_agua.groupby(["COD. DISTRITO", "DIST.", "PELIGRO", "AÑO"]).agg(emergencias=("CODIGO DE EMERGENCIA-SINPAD", "nunique"),
        damnificados=("DAMNIFICADOS", "sum"),
        afectados=("AFECTADOS", "sum"),
        viviendas_destruidas=("VIVIENDAS DESTRUIDAS", "sum"),
        registros_cuatro_ceros=("cuatro_danos_en_cero", "sum")).reset_index())


print(
    resumen_por_ano[resumen_por_ano["PELIGRO"]=="INUNDACION"]
    .sort_values("damnificados", ascending=False)
    .head(15).to_string(index=False)
)

solo_inundaciones = resumen_por_ano[resumen_por_ano["PELIGRO"]=="INUNDACION"]

recurrencia = (solo_inundaciones.groupby(["COD. DISTRITO", "DIST."]).agg(
    anos_con_registros = ("AÑO","nunique"),
    emergencias = ("emergencias","sum"),
    damnificados_acumulados = ("damnificados","sum"),
    damnificados_ano_maximo = ("damnificados","max"),
    registro_cuatro_ceros = ("registros_cuatro_ceros","sum")).reset_index())

total = recurrencia["damnificados_acumulados"]

recurrencia["porcentaje_en_ano_maximo"] = (recurrencia["damnificados_ano_maximo"].div(total.where(total>0)).mul(100).round(1))

print(recurrencia.sort_values("damnificados_acumulados",ascending=False).head(15).to_string(index=False))



inundaciones=eventos_agua[eventos_agua["PELIGRO"]=="INUNDACION"]

total_historico = (inundaciones.groupby(["COD. DISTRITO", "DIST."])["DAMNIFICADOS"].sum())

total_sin_2017 = (inundaciones[inundaciones["AÑO"]!= 2017].groupby(["COD. DISTRITO","DIST."])["DAMNIFICADOS"].sum())

comparacion = pd.concat(
    [
        total_historico.rename("total_historico"),
        total_sin_2017.rename("total_sin_2017")
    ],
    axis=1
)

print(comparacion.sort_values("total_sin_2017",ascending=False).head(10).to_string())

comparacion_anual = (
    danos_anuales["DAMNIFICADOS"]
    .unstack("PELIGRO")
    .reindex(columns=["INUNDACION", "LLUVIA INTENSA"])
)

print(comparacion_anual.to_string())

lluvias_2023 = resumen_por_ano[(resumen_por_ano["AÑO"]==2023)&(resumen_por_ano["PELIGRO"]=="LLUVIA INTENSA")]

print(lluvias_2023.sort_values("damnificados",ascending=False).head(10).to_string())

caso_2023= eventos_agua[(eventos_agua["COD. DISTRITO"] == "200115")
& (eventos_agua["PELIGRO"] == "LLUVIA INTENSA")&(eventos_agua["AÑO"]==2023)]

print(caso_2023[
    [
    "CODIGO DE EMERGENCIA-SINPAD",
    "fecha_evento",
    "DAMNIFICADOS",
    "AFECTADOS",
    "VIVIENDAS DESTRUIDAS"
]].to_string(index=False))

resumen_distrito_peligro = (resumen_por_ano.groupby(["COD. DISTRITO", "DIST.", "PELIGRO"])
    .agg(
    anos_con_registros=("AÑO","nunique"),
    emergencias = ("emergencias","sum"),
    damnificados_reportados = ("damnificados","sum"),
    afectados_reportados = ("afectados","sum"),
    viviendas_destruidas=("viviendas_destruidas","sum"),
    registro_cuatro_ceros = ("registros_cuatro_ceros","sum")
)
    .reset_index())

print(resumen_distrito_peligro.sort_values("damnificados_reportados",ascending=False).head(15).to_string())


print(
    "Total desde registros:",
    eventos_agua.groupby("PELIGRO")["DAMNIFICADOS"].sum()
)

print(
    "Total desde resumen anual:",
    resumen_por_ano.groupby("PELIGRO")["damnificados"].sum()
)

carpeta_salida = Path("datos_preparados")
carpeta_salida.mkdir(exist_ok=True)

archivo_salida = carpeta_salida / "emergencias_piura_2003_2025.csv"

eventos_agua.to_csv(archivo_salida,sep=";", index=False , encoding="utf-8-sig",date_format="%Y-%m-%d"
)

print("Archivo guardado en:", archivo_salida.resolve())
print("Registros exportados:", len(eventos_agua))

nombres_sql = {
    "CODIGO DE EMERGENCIA-SINPAD": "codigo_sinpad",
    "fecha_evento": "fecha_evento",
    "COD. DISTRITO": "ubigeo",
    "DPTO.": "departamento",
    "PROV.": "provincia",
    "DIST.": "distrito",
    "PELIGRO": "peligro",
    "DAMNIFICADOS": "damnificados",
    "AFECTADOS": "afectados",
    "VIVIENDAS DESTRUIDAS": "viviendas_destruidas",
    "VIVIENDAS AFECTADAS": "viviendas_afectadas",
    "cuatro_danos_en_cero": "cuatro_danos_en_cero",
    "observacion_calidad": "observacion_calidad",}

datos_sql = eventos_agua[list(nombres_sql)].rename(columns=nombres_sql)

with engine.begin() as conexion:
    existentes = conexion.execute(text("SELECT COUNT(*) FROM dbo.emergencias_piura")).scalar_one()

    if existentes > 0:
        raise ValueError ("La tabla ya contiene los datos cargados")

    datos_sql.to_sql(
        name="emergencias_piura",
        con = conexion,
        schema="dbo",
        if_exists="append",
        index=False,
        chunksize=200,
    )
    cargados = conexion.execute(text("SELECT COUNT(*) FROM dbo.emergencias_piura")).scalar_one()

    if cargados != len(datos_sql):
        raise ValueError("El conteo de SQL está fallando, no coinciden las cantidades")

print("Carga confirmada. Registro en sql:",cargados)

