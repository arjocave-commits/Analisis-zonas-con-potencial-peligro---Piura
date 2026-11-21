USE [PiuraEmergencias]
GO

/****** Objeto: View [dbo].[vw_indicadores_distritales] Fecha de script: 21/11/2026 09:30:25 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


create   view [dbo].[vw_indicadores_distritales] AS 
SELECT
    d.ubigeo,
    d.distrito,
    d.anio,
    d.peligro,
    d.afectados_reportados,
    p.poblacion_proyectada,
    d.emergencias,
    d.damnificados_reportados,
    d.viviendas_destruidas,
    d.viviendas_afectadas,
    d.registros_cuatro_ceros,
    cast(1000.0 * d.afectados_reportados / nullif(p.poblacion_proyectada,0) as decimal(12,2)) as afectados_reportados_por_cada_1000
  FROM dbo.vw_danos_distrito_anio as d
  left join dbo.poblacion_distrital as p
  on d.UBIGEO = p.UBIGEO
  and d.anio=p.anio
  where d.anio BETWEEN 2018 AND 2025;
GO

