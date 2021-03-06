CREATE DATABASE IF NOT EXISTS `review`;
USE `review`;

DROP TABLE IF EXISTS `REVIEW`;
CREATE TABLE IF NOT EXISTS `REVIEW` (
  `review_id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` VARCHAR(100) NOT NULL,
  `customer_name`VARCHAR(100) NOT NULL,
  `driver_id` int(11) NOT NULL,
  `driver_name` VARCHAR(100) NOT NULL,
  `order_id` int(11) NOT NULL,
  `feedback` VARCHAR(140) NOT NULL,
  CONSTRAINT review_id_pk PRIMARY KEY (`review_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

