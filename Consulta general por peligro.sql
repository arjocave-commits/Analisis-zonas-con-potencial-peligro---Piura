use master;

if DB_ID(N'PiuraEmergencias') is null
	begin 
	create database PiuraEmergencias;
end

use PiuraEmergencias;

SELECT DB_NAME() AS base_actual;

SELECT COUNT(*) AS registros
FROM dbo.emergencias_piura;

USE PiuraEmergencias;

Select peligro,count(*) as registros,
sum(damnificados) as damnificados_reportados,
sum (CAST(cuatro_danos_en_cero as int))as registros_de_cuatro_Ceros
from dbo.emergencias_piura
group by peligro;


with danos_distritales as(
	select 
		ubigeo , distrito , peligro , count(*) as emergencias, sum(damnificados) as damnificados_reportados
	from dbo.emergencias_piura
	group by ubigeo,distrito,peligro),

clasificacion as (
		Select * , DENSE_RANK() over(partition by peligro order by damnificados_reportados desc) as posicion,
		cast(100.0 * damnificados_reportados / nullif(sum(damnificados_reportados)over(partition by peligro), 0 ) as
		decimal (6,2) ) as porcentaje_del_total from danos_distritales)


select * from clasificacion
where posicion <= 5 order by peligro,posicion,ubigeo;