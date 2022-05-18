CREATE DATABASE IF NOT EXISTS hospital;
USE hospital;
CREATE TABLE IF NOT EXISTS expediente (
  id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre varchar(255) NOT NULL,
  diagnostico varchar(450) NOT NULL,
  tratamiento varchar(450) NOT NULL,
  passwordSalt varchar(24) NOT NULL,
  iv varchar(256) NOT NULL,
  diagnostico_tag varchar(256) NOT NULL,
  treatment_tag varchar(256) NOT NULL

);
CREATE USER IF NOT EXISTS 'cripto'@'localhost' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON hospital.* TO 'cripto'@'localhost';
FLUSH PRIVILEGES;
