-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-11-2024 a las 01:42:37
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `ccb_dev`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cuentas`
--

CREATE TABLE `cuentas` (
  `id` int(10) NOT NULL,
  `numero_cuenta` int(10) NOT NULL,
  `saldo` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Volcado de datos para la tabla `cuentas`
--

INSERT INTO `cuentas` (`id`, `numero_cuenta`, `saldo`) VALUES
(1, 134687, 1000),
(2, 259871, 2000),
(3, 521788, 3000),
(4, 584712, 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dev_query`
--

CREATE TABLE `dev_query` (
  `iddev` int(10) NOT NULL,
  `devquery` text DEFAULT NULL,
  `devlanguage` varchar(255) DEFAULT NULL,
  `devanswer` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `respuestas_chatbot`
--

CREATE TABLE `respuestas_chatbot` (
  `idchatbot` int(10) NOT NULL,
  `palabra_clave` text NOT NULL,
  `respuesta` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Volcado de datos para la tabla `respuestas_chatbot`
--

INSERT INTO `respuestas_chatbot` (`idchatbot`, `palabra_clave`, `respuesta`) VALUES
(1, 'hola,hey,qué tal', '¡Hola! ¿En qué puedo ayudarte?'),
(2, 'precio,costo,valor', 'Los precios pueden varían según el modelo según sus especificaciones y necesidades'),
(3, 'envío,entrega', 'Ofrecemos envío gratuito en órdenes superiores.');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `cuentas`
--
ALTER TABLE `cuentas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `no_cta` (`numero_cuenta`);

--
-- Indices de la tabla `dev_query`
--
ALTER TABLE `dev_query`
  ADD PRIMARY KEY (`iddev`);

--
-- Indices de la tabla `respuestas_chatbot`
--
ALTER TABLE `respuestas_chatbot`
  ADD PRIMARY KEY (`idchatbot`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `cuentas`
--
ALTER TABLE `cuentas`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `dev_query`
--
ALTER TABLE `dev_query`
  MODIFY `iddev` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `respuestas_chatbot`
--
ALTER TABLE `respuestas_chatbot`
  MODIFY `idchatbot` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
