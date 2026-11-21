USE PiuraEmergencias;
GO

CREATE OR ALTER VIEW dbo.vw_panel_distrital AS
SELECT
    p.ubigeo,
    p.distrito,
    p.anio,
    peligros.peligro,
    p.poblacion_proyectada,
    CASE
        WHEN i.ubigeo IS NULL THEN N'SIN REGISTRO'
        ELSE N'CON REGISTRO'
    END AS estado_registro,
    i.emergencias,
    i.afectados_reportados,
    i.damnificados_reportados,
    i.viviendas_destruidas,
    i.viviendas_afectadas,
    i.registros_cuatro_ceros,
    i.afectados_reportados_por_cada_1000
FROM dbo.poblacion_distrital AS p
CROSS JOIN (
    VALUES
        (N'INUNDACION'),
        (N'LLUVIA INTENSA')
) AS peligros(peligro)
LEFT JOIN dbo.vw_indicadores_distritales AS i
    ON p.ubigeo = i.ubigeo
    AND p.anio = i.anio
    AND peligros.peligro = i.peligro
WHERE p.anio BETWEEN 2018 AND 2025;
GO

SELECT
    estado_registro,
    COUNT(*) AS combinaciones
FROM dbo.vw_panel_distrital
GROUP BY estado_registro;
GO