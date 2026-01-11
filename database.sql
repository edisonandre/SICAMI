CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    documento TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    password TEXT NOT NULL,
    rol TEXT CHECK (rol IN ('admin','estudiante')) NOT NULL
);

CREATE TABLE estudiantes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    grado INTEGER CHECK (grado BETWEEN 6 AND 11),
    curso TEXT NOT NULL
);

CREATE TABLE materias (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    grado INTEGER CHECK (grado BETWEEN 6 AND 11)
);

CREATE TABLE actividades (
    id SERIAL PRIMARY KEY,
    materia_id INTEGER REFERENCES materias(id),
    nombre TEXT NOT NULL,
    periodo INTEGER CHECK (periodo BETWEEN 1 AND 4),
    porcentaje INTEGER CHECK (porcentaje BETWEEN 1 AND 100)
);

CREATE TABLE notas (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER REFERENCES estudiantes(id),
    actividad_id INTEGER REFERENCES actividades(id),
    nota DECIMAL(3,2) CHECK (nota BETWEEN 1 AND 5)
);
