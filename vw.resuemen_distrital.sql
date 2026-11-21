USE PiuraEmergencias;
GO

CREATE OR ALTER VIEW dbo.vw_resumen_distrital AS
SELECT
    ubigeo,
    distrito,
    peligro,
    COUNT(*) AS anios_del_periodo,
    COUNT(emergencias) AS anios_con_registros,
    COUNT(*) - COUNT(emergencias) AS anios_sin_registros,
    SUM(emergencias) AS emergencias_reportadas,
    SUM(afectados_reportados) AS afectados_acumulados,
    SUM(damnificados_reportados) AS damnificados_acumulados,
    SUM(viviendas_destruidas) AS viviendas_destruidas,
    SUM(viviendas_afectadas) AS viviendas_afectadas,
    MAX(afectados_reportados_por_cada_1000)
        AS maximo_anual_afectados_por_1000,
    SUM(registros_cuatro_ceros) AS registros_cuatro_ceros,
    CAST(
        100.0 * SUM(registros_cuatro_ceros)
        / NULLIF(SUM(emergencias), 0)
        AS DECIMAL(6, 2)
    ) AS porcentaje_registros_cuatro_ceros
FROM dbo.vw_panel_distrital
GROUP BY
    ubigeo,
    distrito,
    peligro;
GO

SELECT *
FROM dbo.vw_resumen_distrital
ORDER BY
    peligro,
    anios_con_registros DESC,
    maximo_anual_afectados_por_1000 DESC,
    ubigeo;



    USE PiuraEmergencias;
GO

SELECT
    codigo_sinpad,
    fecha_evento,
    ubigeo,
    distrito,
    peligro,
    afectados,
    damnificados,
    viviendas_destruidas,
    viviendas_afectadas,
    cuatro_danos_en_cero
FROM dbo.emergencias_piura
WHERE distrito = N'LOBITOS'
  AND peligro = N'LLUVIA INTENSA'
  AND fecha_evento >= '20230101'
  AND fecha_evento < '20240101'
ORDER BY fecha_evento, codigo_sinpad;