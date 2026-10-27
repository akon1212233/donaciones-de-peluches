-- Selecciona una base vacía antes de ejecutar este script.
-- Local: CREATE DATABASE donaciones_peluches_db CHARACTER SET utf8mb4;
-- Railway: usa la base indicada por MYSQLDATABASE, sin crear otra.

CREATE TABLE usuarios(
    id_usuario INT AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    PRIMARY KEY(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE estados(
    id_estado INT AUTO_INCREMENT,
    estado VARCHAR(50) NOT NULL,
    PRIMARY KEY(id_estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO estados (id_estado, estado) VALUES
    (1, 'Disponible'),
    (2, 'Adoptado');

CREATE TABLE peluches(
    id_peluche INT AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    id_estado INT NOT NULL DEFAULT 1,
    id_donador INT NOT NULL,
    id_adoptante INT NULL,
    visitas INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY(id_peluche),
    FOREIGN KEY (id_estado) REFERENCES estados(id_estado),
    FOREIGN KEY (id_donador) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_adoptante) REFERENCES usuarios(id_usuario),
    CONSTRAINT adopcion_coherente CHECK (
        (id_estado = 1 AND id_adoptante IS NULL) OR
        (id_estado = 2 AND id_adoptante IS NOT NULL AND id_adoptante != id_donador)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
