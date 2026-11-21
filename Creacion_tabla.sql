use PiuraEmergencias;

if object_id(N'dbo.emergencias_piura',N'U') IS NULL
begin
	CREATE TABLE dbo.emergencias_piura (
        codigo_sinpad INT NOT NULL PRIMARY KEY,
        fecha_evento DATE NOT NULL,
        ubigeo CHAR(6) NOT NULL,
        departamento NVARCHAR(50) NOT NULL,
        provincia NVARCHAR(50) NOT NULL,
        distrito NVARCHAR(50) NOT NULL,
        peligro NVARCHAR(100) NOT NULL,

        damnificados INT NOT NULL CHECK (damnificados >= 0),
        afectados INT NOT NULL CHECK (afectados >= 0),
        viviendas_destruidas INT NOT NULL
            CHECK (viviendas_destruidas >= 0),
        viviendas_afectadas INT NOT NULL
            CHECK (viviendas_afectadas >= 0),

        cuatro_danos_en_cero BIT NOT NULL,
        observacion_calidad NVARCHAR(250) NULL
    );
    end;
