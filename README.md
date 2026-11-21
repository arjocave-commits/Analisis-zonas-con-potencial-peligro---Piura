# Piura: lluvias e inundaciones

Análisis de emergencias reportadas, daños humanos y materiales y su relación con la población distrital. El proyecto combina Python, SQL Server, Power Query y Power BI para comparar distritos y explorar su evolución temporal.

## Objetivo

Identificar patrones históricos de impacto y recurrencia que permitan seleccionar distritos para una revisión más profunda. El análisis es descriptivo: no predice inundaciones ni constituye una clasificación oficial de riesgo.

## Alcance y fuentes

- INDECI / SINPAD: archivo `BD_2003-2025_EMERGENCIAS.csv`, con registros de 2003–2025. Se seleccionaron Piura y las categorías `INUNDACION` y `LLUVIA INTENSA`: 2.147 registros.
- INEI: población distrital proyectada 2018–2026, preparada en Power Query. Archivo de trabajo `poblacion_piura_preparada.xlsx`, hoja `poblacion_distrital`: 585 filas, 65 distritos y nueve años.
- El informe comparativo con población se limita a 2018–2025. La exploración inicial conserva 2003–2025.
- Las fuentes ANA se exploraron, pero no se integraron en esta versión.

Antes de publicar el repositorio, incorporar los enlaces exactos de descarga y las fechas de consulta de ambas fuentes. El Excel preparado no reemplaza la referencia a la publicación original del INEI.

## Flujo de trabajo

1. Python lee el CSV con separador punto y coma, codificación cp1252 y UBIGEO como texto.
2. Se filtran territorio y peligros, se revisan códigos, fechas y campos de daños y se conserva una marca para los cuatro daños en cero.
3. Power Query transforma la población de columnas anuales a filas por distrito y año.
4. Python carga directamente los datos en SQL Server mediante SQLAlchemy y pyodbc, dentro de transacciones y con comprobación de cantidades.
5. SQL agrega por distrito, año y peligro y enlaza población mediante UBIGEO y año.
6. Power BI permite comparar distritos y explorar su evolución.

## Archivos revisados

| Archivo | Función |
|---|---|
| `Analisis_datos.py` | Exploración, preparación y carga de emergencias; exporta también un CSV preparado. |
| `conexion_sql.py` | Configuración y prueba de conexión a SQL Server con autenticación de Windows. |
| `carga_poblacion.py` | Lectura del Excel preparado, validación y carga de población. |
| `Consulta general por peligro.sql` | Creación de base y consultas exploratorias, incluido ranking con DENSE_RANK. |
| `Creacion_tabla.sql` | Creación de la tabla de emergencias y restricciones. |
| `vw_daño_por_distrito.sql` | Vista anual de daños, creación de población y consultas de cruce. |
| `Lluvias_intensas_porUBIGEO.sql` | Recurrencia de registros de lluvia intensa. |
| `vw_indicadores_distritales.sql` | Crea la vista que enlaza daños anuales y población mediante UBIGEO y año y calcula afectados por 1.000 habitantes. |
| `dbo.vw_panel_distrital.sql` | Crea el panel completo de distrito, año y peligro y comprueba combinaciones con y sin registro. |
| `vw.resuemen_distrital.sql` | Vista resumen y consulta de detalle del caso Lobitos. |
| `Lluvias_PIURA.pbix` | Informe Power BI. |
| `main.py` | Plantilla inicial de PyCharm; no interviene en el análisis. |

## Informe Power BI

### Comparación anual

Filtros de año y peligro, tarjetas de emergencias, afectados y damnificados, comparación de afectados acumulados y por cada 1.000 habitantes, y detalle distrital.

### Evolución temporal

Selector de distrito, tarjetas acumuladas de 2018–2025, evolución de afectados y columnas de emergencias por año y peligro.

La página de calidad de datos no forma parte de las dos páginas principales acordadas. Sus controles se documentan aquí y en los scripts.

## Indicadores y decisiones metodológicas

- Emergencias: cantidad de registros del conjunto seleccionado; no se interpreta automáticamente como episodios meteorológicos independientes.
- Afectados y damnificados: sumas de los valores reportados, mantenidas como categorías separadas.
- Afectados por 1.000 habitantes: afectados acumulados del año y peligros seleccionados / población proyectada del mismo distrito y año × 1.000.
- La población se cuenta una sola vez por distrito al seleccionar ambos peligros. Las tasas no se suman entre distritos ni entre años.
- La medida del informe requiere un único año; con varios años devuelve vacío.
- El panel completo tiene 65 distritos × 8 años × 2 peligros = 1.040 combinaciones: 303 con registro y 737 sin registro.
- Se conservan los NULL del panel para distinguir combinaciones sin registro de registros con valores en cero.

## Controles realizados durante el proyecto

- Revisión de duplicados SINPAD, formatos UBIGEO y coherencia de nombres territoriales.
- Conversión de fechas con dos formatos: día/mes/año de cuatro dígitos y, para pendientes, mes/día/año de dos dígitos. Contraste con año y mes originales.
- Revisión de faltantes, valores no numéricos, negativos y decimales en cuatro campos de daños.
- Comprobación de unicidad UBIGEO–año, cobertura 2018–2026 y población positiva.
- Conteos de carga y conciliación de resultados entre Python, SQL y Power BI.

Parte de los controles de emergencias imprime resultados para revisión manual; no todos detienen automáticamente la carga. Los scripts de carga rechazan tablas con datos para evitar duplicar una carga inicial, pero no implementan actualización incremental.

## Resultados comprobados en el desarrollo

| Piura, 2023 | Emergencias | Afectados reportados | Damnificados reportados |
|---|---:|---:|---:|
| Lluvia intensa | 341 | 303.842 | 29.436 |
| Inundación | 10 | 2.065 | 124 |
| Ambas categorías | 351 | 305.907 | 29.560 |

- En lluvias de 2023, Tambo Grande registra 43.027 afectados y Catacaos 32.090. Lobitos destaca en la comparación respecto a población: 2.265 reportados / 1.373 habitantes × 1.000 = 1.649,67.
- Lobitos suma tres registros con 1.101, 1.158 y 6 afectados. No se dispone de identificadores personales para determinar si existen personas repetidas entre eventos.
- Paimas acumula 28 registros, 12.739 afectados y 1.228 damnificados en 2018–2025. Sus siete registros de lluvia de 2023 suman 3.727 afectados; sus siete de 2025 suman 6.005. Igual frecuencia no implica igual impacto.

Estos valores fueron contrastados durante la construcción del proyecto; esta revisión documental no volvió a ejecutar las cargas ni consultó la base activa.

## Limitaciones

- Sin registro no significa ausencia de emergencias ni demuestra por sí solo un fallo de reporte.
- Cuatro campos de daños en cero no demuestran ausencia de otros daños ni un error de carga. Se conservan y se identifican para revisión.
- Los afectados acumulados pueden incluir personas contabilizadas en varios eventos; una tasa mayor a 1.000 no representa más del 100 % de personas únicas afectadas.
- La población es una proyección referencial, no una medición de personas expuestas al peligro.
- No se ha establecido aquí la cobertura completa del último año ni la estabilidad del registro a lo largo del tiempo. Debe verificarse antes de interpretar cambios como tendencias del fenómeno físico.
- El tamaño de población, la recurrencia y los daños reportados son dimensiones complementarias; no bastan para construir una clasificación oficial de riesgo.

## Reproducción: estado actual y pendientes

Requisitos del flujo existente: Python, pandas, SQLAlchemy, pyodbc, openpyxl, SQL Server, ODBC Driver 18 y Power BI Desktop. No se han fijado versiones de paquetes en los archivos revisados.

El proyecto original está en `C:\Users\user\PycharmProjects\PythonProject5`. Los scripts usan autenticación de Windows y una instancia local definida en `conexion_sql.py`; cada usuario debe ajustar esa conexión a su entorno.

Orden lógico para una instalación nueva:

1. Crear `PiuraEmergencias` con el bloque inicial de `Consulta general por peligro.sql`. El resto del archivo consulta tablas que aún no existirán.
2. Crear `dbo.emergencias_piura` con `Creacion_tabla.sql`.
3. Ajustar la conexión y ejecutar `Analisis_datos.py` desde la carpeta del proyecto, con el CSV presente.
4. Crear la vista anual y la tabla de población usando los bloques pertinentes de `vw_daño_por_distrito.sql`.
5. Colocar el Excel preparado junto a `carga_poblacion.py` y ejecutar ese script.
6. Ejecutar `vw_indicadores_distritales.sql` y después `dbo.vw_panel_distrital.sql`. El primero utiliza CREATE VIEW: para una base donde la vista ya existe, no volver a ejecutar ese bloque sin adaptar la instrucción a CREATE OR ALTER VIEW.
7. Ejecutar `vw.resuemen_distrital.sql` para el resumen y las consultas analíticas de `Lluvias_intensas_porUBIGEO.sql`.
8. Abrir el PBIX, ajustar su origen SQL y actualizar los datos. Verificar los resultados de referencia anteriores.

Pendientes detectados al leer los archivos:

- Las definiciones de las cuatro vistas utilizadas en el flujo SQL ya están guardadas y fueron revisadas como texto el 21/11/2026. No se ha ejecutado todavía una reconstrucción completa en una base nueva.
- `vw_daño_por_distrito.sql` comprueba `dbo.población_distrital` con tilde, pero crea `dbo.poblacion_distrital` sin tilde. Unificar el nombre para que la comprobación de existencia sea consistente, especialmente en bases sensibles a acentos.
- El mismo archivo declara UBIGEO de población como CHAR(10), mientras emergencias utiliza CHAR(6). Documentar o normalizar ambos a seis caracteres en una revisión posterior del esquema.
- Durante el desarrollo del PBIX se cargaron dos tablas con nombres similares (`vw_panel_distital` y `vw_panel_distrital`). Las medidas y los ejes deben usar una misma tabla coherente. No eliminar una copia sin revisar sus dependencias.
- Las medidas DAX y las transformaciones originales de Power Query deben exportarse como texto para facilitar la revisión externa. No se extrajeron del PBIX en esta revisión.

## Publicación del portafolio

Incluir scripts, SQL completos, PBIX, capturas de las dos páginas y este README. Excluir `.venv`, `.idea` y `__pycache__`. Documentar la procedencia y las condiciones de reutilización de los datos antes de redistribuirlos. Conservar el original descargado separado de las salidas preparadas.


