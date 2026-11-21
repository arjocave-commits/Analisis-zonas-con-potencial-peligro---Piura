USE PiuraEmergencias;
GO

SELECT
    ubigeo,
    distrito,
    peligro,
    COUNT(*) AS anios_del_periodo,
    COUNT(emergencias) AS anios_con_registros,
    COUNT(*) - COUNT(emergencias) AS anios_sin_registros,
    SUM(emergencias) AS emergencias_reportadas,
    SUM(afectados_reportados) AS afectados_reportados,
    SUM(damnificados_reportados) AS damnificados_reportados
FROM dbo.vw_panel_distrital
WHERE peligro = N'LLUVIA INTENSA'
GROUP BY
    ubigeo,
    distrito,
    peligro
ORDER BY
    anios_con_registros DESC,
    ubigeo;