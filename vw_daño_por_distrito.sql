USE PiuraEmergencias;
go

create or alter view dbo.vw_danos_distrito_anio as 
select 
	ubigeo,
    distrito,
    peligro,
    YEAR(fecha_evento) AS anio,
    COUNT(*) AS emergencias,
    SUM(damnificados) AS damnificados_reportados,
    SUM(afectados) AS afectados_reportados,
    SUM(viviendas_destruidas) AS viviendas_destruidas,
    SUM(viviendas_afectadas) AS viviendas_afectadas,
    SUM(CAST(cuatro_danos_en_cero AS INT)) AS registros_cuatro_ceros
from dbo.emergencias_piura
group by ubigeo , distrito, peligro, year(fecha_evento);

go 
select top (10)*from dbo.vw_danos_distrito_anio
order by anio desc , damnificados_reportados desc,ubigeo , peligro;
GO

USE PiuraEmergencias;
GO

If OBJECT_ID(N'dbo.población_distrital',N'U') is null
begin
    create table dbo.poblacion_distrital(
    UBIGEO char(10) not null,
    distrito nvarchar(100) not null,
    anio SMALLINT NOT NULL,
    poblacion_proyectada INT NOT NULL,

    constraint PK_poblacion_distrital
    primary key (UBIGEO,anio),

    constraint CK_poblacion_positiva
    check (poblacion_proyectada > 0)
    );
end;
go

SELECT COUNT(*) AS registros
FROM dbo.poblacion_distrital;


USE PiuraEmergencias;
GO

SELECT
    @@SERVERNAME AS servidor,
    DB_NAME() AS base_actual;

SELECT
    s.name AS esquema,
    t.name AS tabla
FROM sys.tables AS t
JOIN sys.schemas AS s
    ON t.schema_id = s.schema_id
WHERE t.name LIKE '%poblacion%';

select 
 d.ubigeo,
 d.distrito,
 d.anio,
 d.peligro
 from dbo.vw_danos_distrito_anio as d
 left join dbo.poblacion_distrital as p 
 on d.UBIGEO = p."UBIGEO"
 and d.anio = p.anio
 where d.anio between 2018 and 2025
 and p.UBIGEO is null;

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
  
  where d.anio BETWEEN 2018 AND 2025
  order by d.ubigeo, d.anio, d.peligro;