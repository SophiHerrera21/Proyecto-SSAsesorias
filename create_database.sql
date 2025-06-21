-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS virtualAsesoriSS3;

-- Usar la base de datos
USE virtualAsesoriSS3;

-- Crear usuario si no existe
CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON virtualAsesoriSS3.* TO 'root'@'localhost';
FLUSH PRIVILEGES; 